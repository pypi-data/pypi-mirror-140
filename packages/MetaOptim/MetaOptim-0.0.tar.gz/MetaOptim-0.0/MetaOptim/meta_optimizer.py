"""
modified from torch.optim.optimizer.py
"""
import functools
from collections import defaultdict, abc as container_abcs
from copy import deepcopy
from itertools import chain
from typing import Iterable

import torch
from torch.optim.optimizer import required
from torch import distributed

from . import _functional as F


class SlidingWindow(object):
    r"""The class for handling the behaviors of MetaOptimizer and network parameters.

     We take the process of one outer loop that doing the inner update and computing outer loss
     and then performing meta update for the meta parameters as a window.
     The training process can be considered as a window sliding process,
     all the behavior are handled by the class SlidingWindow.

     The class ``SlidingWindow`` should be used in the following way: ::

         for outer_step in range(OUTER_RANGE):
            with SlidingWindow(offline=True):
                for inner_step in range(INNER_RANGE):
                    # do inner loop
                # compute and back-propagate the outer loss
                # do some update on meta parameters

    You should do inner loop with the ``with`` statement.
    At the stage of exiting the ``with`` statement,
    ``SlidingWindow`` will automatically set the network parameters and clear the temporary gradient graph.


    Args:
         offline (bool, optional): use offline mode to update the network or not. (default: False)
            backward_hook (callable, optional): backward hook that would be registered on the 1-th order gradients,
            it takes effect when calculating the meta gradient. (default: None)
        backward_hook (Callable, optional): register a hook to the inner loop first derivative.
            The motivation for designing this mechanism is the second derivative often is numerical unstable,
            we allow user use some function, e.g., ``MetaOptim.zero_nan_hook``, to deal with some excepctions.
         record_grad_tape (bool, optional): record intermediate network parameters with name,
            i.e., parameters after an inner update. (default: False)
         pickup_step (int, optional): in the online case,
            we often use network parameters in the last inner loop step of current sliding window
            as the start network parameters in the next sliding window.
            Here we allow users pickup the network parameters in the 'pickup_step'-th inner loop step
            as the start network parameters in the next sliding window.
            (default: -1, stands for pickling the network parameters in the last inner loop step.)
    """
    OPTIMIZER_COUNTER = 0
    ALREADY_SLIDING = False
    REGISTERED_OPTIMIZERS = dict()

    def __init__(self, offline=False, backward_hook=None, record_grad_tape=False, pickup_step=-1):
        SlidingWindow.OFFLINE = offline
        SlidingWindow.BACKWARD_HOOK = backward_hook
        SlidingWindow.RECORD_GRAD_TAPE = record_grad_tape
        if pickup_step != -1 and offline:
            raise RuntimeError("offline mode does not support pickup_step")
        SlidingWindow.PICKUP_STEP = pickup_step

    def __enter__(self):
        if SlidingWindow.ALREADY_SLIDING:
            raise RuntimeError("sliding window twice")
        SlidingWindow.ALREADY_SLIDING = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in SlidingWindow.REGISTERED_OPTIMIZERS:
            if SlidingWindow.OFFLINE:
                SlidingWindow.REGISTERED_OPTIMIZERS[key]._exit_offline()
                F.detach_optimizer(SlidingWindow.REGISTERED_OPTIMIZERS[key])
            else:
                if SlidingWindow.PICKUP_STEP == -1:
                    F.detach_optimizer(SlidingWindow.REGISTERED_OPTIMIZERS[key])
                SlidingWindow.REGISTERED_OPTIMIZERS[key]._exit_online()

        SlidingWindow.REGISTERED_OPTIMIZERS.clear()
        SlidingWindow.ALREADY_SLIDING = False

    def named_parameters(self):
        pass


class MetaOptimizer(object):
    r"""Base class for all meta optimizers.

    .. warning::
        Parameters need to be specified as collections that have a deterministic
        ordering that is consistent between runs. Examples of objects that don't
        satisfy those properties are sets and iterators over values of dictionaries.

    Args:
        params (List[nn.Module]): networks that are updated in the inner loop.
        defaults: (dict): a dict containing default values of optimization
            options (used when a parameter group doesn't specify them).
    """

    def __init__(self, params, defaults):

        torch._C._log_api_usage_once("python.optimizer")
        self.defaults = defaults

        self._hook_for_profile()

        if not isinstance(params, Iterable):
            raise TypeError("items of params given to the optimizer should be "
                            "iterable but get " + torch.typename(params))

        self.state = defaultdict(dict)
        self.param_groups = []
        self.parameters_backup = []
        self.first_offline_step = False

        self._parameter_list = []
        self._plain_parameter_list = []
        self._grad_normalizer = None
        self._last_state_dict = dict()

        for param in params:
            if not isinstance(param, torch.nn.Module):
                raise TypeError("items of params given to the optimizer should be "
                                "nn.Module but get " + torch.typename(param))
            self.add_param_group({'params': param})

        self._optimizer_id = SlidingWindow.OPTIMIZER_COUNTER
        SlidingWindow.OPTIMIZER_COUNTER += 1

    def __getstate__(self):
        return {
            'defaults': self.defaults,
            'state': self.state,
            'param_groups': self.param_groups
        }

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._hook_for_profile()  # To support multiprocessing pickle/unpickle.

    def __repr__(self):
        format_string = self.__class__.__name__ + ' ('
        for i, group in enumerate(self.param_groups):
            format_string += '\n'
            format_string += 'Parameter Group {0}\n'.format(i)
            for key in sorted(group.keys()):
                if key != 'params':
                    format_string += '    {0}: {1}\n'.format(key, group[key])
        format_string += ')'
        return format_string

    def _exit_online(self):
        r"""Detach temporary network parameters and optimizer parameters (e.g., momentum)
            at the exiting stage of online mode.

        .. note::
            for safety, only use this method in SlidingWindow.__exit__
        """
        if SlidingWindow.PICKUP_STEP != -1:
            self._load_state_dict(self.state_pickup)
            self.state_pickup = None
            for group in self.param_groups:
                F.recover_net_from_plain_list(group['params'], group.pop('params_pickup'), 0, False)
            self.online_update_step = 0

        if distributed.is_initialized():
            for group in self.param_groups:
                F.average_model(group['params'])

    def _exit_offline(self):
        r"""Reset network parameters and optimizer parameters (e.g., momentum) at the exiting stage of offline mode.

        .. note::
            for safety, only use this method in SlidingWindow.__exit__
        """
        self._load_state_dict(self._last_state_dict)
        parameter_idx = 0
        for group in self.param_groups:
            parameter_idx = F.recover_net_from_plain_list(group['params'], self.parameters_backup, parameter_idx, True)
        self.parameters_backup.clear()

    def _register_optimizer(self):
        if SlidingWindow.ALREADY_SLIDING:
            if SlidingWindow.REGISTERED_OPTIMIZERS.get(self._optimizer_id) is None:
                SlidingWindow.REGISTERED_OPTIMIZERS.update({self._optimizer_id: self})
                self.first_offline_step = SlidingWindow.OFFLINE
                if SlidingWindow.RECORD_GRAD_TAPE:
                    for i, group in enumerate(self.param_groups):
                        group['grad_tape'] = {}
                        for k, v in group['params'].named_parameters():
                            group['grad_tape'].update({'step_' + str(group['inner_steps']) + ':' + k: v})
                if SlidingWindow.PICKUP_STEP != -1:
                    self.online_update_step = 0
        else:
            raise RuntimeError("should use 'with SlidingWindow():'")

    def _hook_for_profile(self):
        self._zero_grad_profile_name = "Optimizer.zero_grad#{}.zero_grad".format(self.__class__.__name__)

        def profile_hook_step(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                obj, *_ = args
                profile_name = "Optimizer.step#{}.step".format(obj.__class__.__name__)
                with torch.autograd.profiler.record_function(profile_name):
                    return func(*args, **kwargs)

            return wrapper

        hooked = getattr(self.__class__.step, "hooked", None)
        if not hooked:
            self.__class__.step = profile_hook_step(self.__class__.step)
            self.__class__.step.hooked = True

    def state_dict(self):
        r"""Returns the state of the optimizer as a :class:`dict`.

        It contains two entries:

        * state - a dict holding current optimization state. Its content
            differs between optimizer classes.
        * param_groups - a list containing all parameter groups where each
            parameter group is a dict

        .. note::
            The output ``state_dict`` of this method is compatible to be loaded by
            non-meta optimizer (``torch.optim.Optimizer.load_state_dict()``)
            and meta optimizer (``MetaOptim.MetaOptimizer.load_state_dict()``).
        """
        # Save order indices instead of Tensors
        param_mappings = {}
        start_index = 0

        def pack_group(group):
            nonlocal start_index
            packed = {k: v for k, v in group.items() if k != 'params'}
            param_mappings.update({id(p): i for i, p in enumerate(group['params'].parameters(), start_index)
                                   if id(p) not in param_mappings})
            packed['params'] = [param_mappings[id(p)] for p in group['params'].parameters()]
            start_index += len(packed['params'])
            return packed

        param_groups = []
        flatted_parameters = []
        for group in self.param_groups:
            param_groups.append(pack_group(group))
            flatted_parameters += list(group['params'].parameters())
        # Remap state to use order indices as keys
        for k, v in self.state.items():
            for vk in v:
                if isinstance(v[vk], torch.Tensor):
                    if not v[vk].is_leaf:
                        v[vk] = v[vk].detach().requires_grad_(True)

        def detach_items_in_dict(input_dict):
            output_dict = {}
            for k, v in input_dict.items():
                output_dict.update({k: v.detach().requires_grad_(True) if isinstance(v, torch.Tensor) else v})
            return output_dict

        flatted_parameter_names = []
        for v in self._parameter_list:
            flatted_parameter_names += v
        packed_state = {param_mappings[id(p)]: detach_items_in_dict(self.state[p_name]) for p_name, p in zip(flatted_parameter_names, flatted_parameters)}
        return {
            'state': packed_state,
            'param_groups': param_groups,
        }

    def _load_state_dict(self, state_dict):
        r"""Loads the optimizer state.

        Args:
            state_dict (dict): optimizer state. Should be an object returned
                from a call to :meth:`state_dict`.
        """
        # Validate the state_dict
        groups = self.param_groups
        saved_groups = state_dict['param_groups']

        if len(groups) != len(saved_groups):
            raise ValueError("loaded state dict has a different number of "
                             "parameter groups")
        param_lens = (len(list(g['params'].parameters())) for g in groups)
        saved_lens = (len(g['params']) for g in saved_groups)
        if any(p_len != s_len for p_len, s_len in zip(param_lens, saved_lens)):
            raise ValueError("loaded state dict contains a parameter group "
                             "that doesn't match the size of optimizer's group")

        # Update the state
        id_map = {old_id: [p, origin_name] for old_id, p, origin_name in
                  zip(chain.from_iterable((g['params'] for g in saved_groups)),
                      chain.from_iterable((g['params'].parameters() for g in groups)),
                      chain.from_iterable(self._parameter_list))}

        def cast(param, value):
            r"""Make a deep copy of value, casting all tensors to device of param."""
            if isinstance(value, torch.Tensor):
                # Floating-point types are a bit special here. They are the only ones
                # that are assumed to always match the type of params.
                if param.is_floating_point():
                    value = value.to(param.dtype)
                value = value.to(param.device)
                return value.requires_grad_(True)
            elif isinstance(value, dict):
                return {k: cast(param, v) for k, v in value.items()}
            elif isinstance(value, container_abcs.Iterable):
                return type(value)(cast(param, v) for v in value)
            else:
                return value

        # Copy state assigned to params (and cast tensors to appropriate types).
        # State that is not assigned to params is copied as is (needed for
        # backward compatibility).
        state = defaultdict(dict)
        for k, v in state_dict['state'].items():
            if k in id_map:
                p, origin_name = id_map[k]
                state[origin_name] = cast(p, v)
            else:
                state[k] = v

        # Update parameter groups, setting their 'params' value
        def update_group(group, new_group):
            new_group['params'] = group['params']
            return new_group

        param_groups = [
            update_group(g, ng) for g, ng in zip(groups, saved_groups)]
        self.__setstate__({'state': state, 'param_groups': param_groups})

    def load_state_dict(self, state_dict):
        r"""Loads the optimizer state.

        .. note::
            This method is compatible to both the ``state_dict`` output by
            non-meta optimizer (``torch.optim.Optimizer.state_dict()``)
            and meta optimizer (``MetaOptim.MetaOptimizer.state_dict()``).

        Args:
            state_dict (dict): optimizer state. Should be an object returned
                from a call to :meth:`state_dict`.
        """
        # deepcopy, to be consistent with module API
        state_dict = deepcopy(state_dict)
        # Validate the state_dict
        groups = self.param_groups
        saved_groups = state_dict['param_groups']

        if len(groups) != len(saved_groups):
            raise ValueError("loaded state dict has a different number of "
                             "parameter groups")
        param_lens = (len(list(g['params'].parameters())) for g in groups)
        saved_lens = (len(g['params']) for g in saved_groups)
        if any(p_len != s_len for p_len, s_len in zip(param_lens, saved_lens)):
            raise ValueError("loaded state dict contains a parameter group "
                             "that doesn't match the size of optimizer's group")

        # Update the state
        id_map = {old_id: [p, origin_name] for old_id, p, origin_name in
                  zip(chain.from_iterable((g['params'] for g in saved_groups)),
                      chain.from_iterable((g['params'].parameters() for g in groups)),
                      chain.from_iterable(self._parameter_list))}

        def cast(param, value):
            r"""Make a deep copy of value, casting all tensors to device of param."""
            if isinstance(value, torch.Tensor):
                # Floating-point types are a bit special here. They are the only ones
                # that are assumed to always match the type of params.
                if param.is_floating_point():
                    value = value.to(param.dtype)
                value = value.to(param.device)
                return value.requires_grad_(True)
            elif isinstance(value, dict):
                return {k: cast(param, v) for k, v in value.items()}
            elif isinstance(value, container_abcs.Iterable):
                return type(value)(cast(param, v) for v in value)
            else:
                return value

        # Copy state assigned to params (and cast tensors to appropriate types).
        # State that is not assigned to params is copied as is (needed for
        # backward compatibility).
        state = defaultdict(dict)
        for k, v in state_dict['state'].items():
            if k in id_map:
                p, origin_name = id_map[k]
                state[origin_name] = cast(p, v)
            else:
                state[k] = v

        # Update parameter groups, setting their 'params' value
        def update_group(group, new_group):
            new_group['params'] = group['params']
            return new_group

        param_groups = [
            update_group(g, ng) for g, ng in zip(groups, saved_groups)]
        self.__setstate__({'state': state, 'param_groups': param_groups})

    def zero_grad(self, set_to_none: bool = False):
        if not hasattr(self, "_zero_grad_profile_name"):
            self._hook_for_profile()
        with torch.autograd.profiler.record_function(self._zero_grad_profile_name):
            for group in self.param_groups:
                # now group['params'] should be the network instead of parameter list
                for p in group['params'].parameters():
                    if p.grad is not None:
                        if set_to_none:
                            p.grad = None
                        else:
                            if p.grad.grad_fn is not None:
                                p.grad.detach_()
                            else:
                                p.grad.requires_grad_(False)
                            p.grad.zero_()

    def step(self, loss, closure=None, allow_unused=False):
        r"""Performs a single optimization step (parameter update).

        Args:
            loss (torch.Tensor): The loss that is used to compute the gradient to the network parameters,
                it is usually the inner loop loss.
            closure (callable, optional): A closure that reevaluates the model and
                returns the loss. (default: ``None``)
            allow_unused (bool, optional): If ``False``, specifying inputs that were not
                used when computing outputs (and therefore their grad is always zero)
                is an error. (default: ``False``)

        .. note::
            Unless otherwise specified, this function should not modify the
            ``.grad`` field of the parameters.
        """
        self._register_optimizer()
        loss_ = None
        if closure is not None:
            loss_ = closure()

        parameters = []
        for group in self.param_groups:
            group['inner_steps'] += 1
            parameters += list(group['params'].parameters())

        gradss = list(torch.autograd.grad(loss,
                                          parameters,
                                          create_graph=True,
                                          allow_unused=allow_unused))

        # if self.first_offline_step or distributed.is_initialized():
        #     if self.first_offline_step:
        #         self.first_offline_step = False
        #         self._last_state_dict = self.state_dict()
        #     for parameter in parameters:
        #         parameter._recovered = False
        #     self.parameters_backup = parameters
        # TODO (Jie Ren): current version we do not backup the DDP network parameters,
        #  the reason for reserving the DDP parameter is because of we want to reserve the communication hook,
        #  but I think,
        #  the communication hook may not be required for the gradient from later inner loop parameters may not be used;
        if self.first_offline_step:
            self.first_offline_step = False
            self._last_state_dict = self.state_dict()
            for parameter in parameters:
                parameter._recovered = False
            self.parameters_backup = parameters

        if self._grad_normalizer is not None:
            F.clip_grad_norm_(gradss,
                              self._grad_normalizer.max_norm,
                              self._grad_normalizer.norm_type,
                              self._grad_normalizer.error_if_nonfinite)

        for p, grad in zip(parameters, gradss):
            p._fast_grad = grad
            if SlidingWindow.BACKWARD_HOOK is not None:
                p._fast_grad.register_hook(SlidingWindow.BACKWARD_HOOK)

        self._step()
        if SlidingWindow.RECORD_GRAD_TAPE:
            for group in self.param_groups:
                for k, v in group['params'].named_parameters():
                    group['grad_tape'].update({('step_%i:%s' % (group['inner_steps'], k), v.size()): v.grad_fn})
        if SlidingWindow.PICKUP_STEP != -1:
            self.online_update_step += 1
            if self.online_update_step == SlidingWindow.PICKUP_STEP:
                for group in self.param_groups:
                    parameters = [p.detach().requires_grad_(True) for p in group['params'].parameters()]
                    group['params_pickup'] = parameters
                self.state_pickup = self.state_dict()
        return loss_

    def _step(self):
        raise NotImplementedError

    def named_parameters(self):
        if SlidingWindow.RECORD_GRAD_TAPE:
            for group in self.param_groups:
                for k, v in group['grad_tape'].items():
                    yield k, v
        else:
            for group in self.param_groups:
                for k, v in group['params'].named_parameters():
                    yield k, v

    def add_param_group(self, param_group):
        r"""Add a param group to the :class:`Optimizer` s `param_groups`.

        This can be useful when fine-tuning a pre-trained network as frozen layers can be made
        trainable and added to the :class:`Optimizer` as training progresses.

        Args:
            param_group (dict): Specifies what Tensors should be optimized along with group
            specific optimization options.
        """
        assert isinstance(param_group, dict), "param group must be a dict"
        param_group['inner_steps'] = 0

        params = param_group['params']
        if isinstance(params, torch.nn.Module):
            param_group['params'] = params
        else:
            raise NotImplementedError

        for name, default in self.defaults.items():
            if default is required and name not in param_group:
                raise ValueError("parameter group didn't specify a value of required optimization parameter " +
                                 name)
            else:
                param_group.setdefault(name, default)

        self._parameter_list.append([])
        F.build_parameter_list_no_overlap(params, set(), self._parameter_list[-1], str(len(self.param_groups)))
        self.param_groups.append(param_group)
        self._plain_parameter_list += list(params.parameters())

        if len(self._plain_parameter_list) != len(set(self._plain_parameter_list)):
            raise ValueError("there exists parameter overlapping in params")

    def reset_grad_normalizer(self, max_norm, norm_type=2.0, error_if_nonfinite=False):
        r"""Normalize the gradient.

        Args:
             max_norm (float, int, optional): max norm of the gradients.
             norm_type (float, int, optional): type of the used p-norm. Can be ``'inf'`` for
                infinity norm. (default: 2.0)
             error_if_nonfinite (bool, optional): if True, an error is thrown if the total
                 norm of the gradients from :attr:``parameters`` is ``nan``,
                 ``inf``, or ``-inf``. (default: False)
        """

        class GradNormalizer:
            def __init__(self, max_norm, norm_type, error_if_nonfinite):
                self.max_norm = max_norm
                self.norm_type = norm_type
                self.error_if_nonfinite = error_if_nonfinite
        self._grad_normalizer = GradNormalizer(max_norm, norm_type, error_if_nonfinite)
