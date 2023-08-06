# Meta-Optim

A differentiable optimizer.

## Features

*Meta-Optim* aims to help users implement their meta-learning algorithms, e.g., [Model-Agnostic Meta-Learning](https://proceedings.mlr.press/v70/finn17a.html), in a convenient way.

- It provides several popular differentiable optimizers, e.g., [Adam](https://arxiv.org/abs/1412.6980).
- Without modifying the neural network structure during the inner update stage in meta-learning, *Meta-Optim* makes it possible for users implement complex algorithms, e.g., [Meta-Gradient Reinforcement Learning (MGRL)](https://arxiv.org/abs/1805.09801).
- Online & Offline
- API
- Performance

## Install

```bash
git clone git@github.com:metaopt/meta-optim.git
pip install -e .
```


## Concepts

Meta-learning often is implemented by two-level update. The two-level update often includes a outer loop for updating the meta-parameters and a inner loop for updating the neural network. We divide the existing meta-learning algorithms into online meta-learning and offline meta-learning according to the neural network update strategy.

Assume <img src="https://latex.codecogs.com/svg.latex?\alpha" /> is meta-parameters and <img src="https://latex.codecogs.com/svg.latex?\theta" /> is neural network parameters. <img src="https://latex.codecogs.com/svg.latex?\alpha" /> starts with <img src="https://latex.codecogs.com/svg.latex?\alpha_0" /> and <img src="https://latex.codecogs.com/svg.latex?\theta" /> starts with <img src="https://latex.codecogs.com/svg.latex?\theta_0" />.

![fig](./figs/offline_mode.png)

*Offline Meta-Learning*

The offline meta-learning algorithms use *inner loss* <img src="https://latex.codecogs.com/svg.latex?L_{in}" /> update the neural network by using gradient based optimizer: <img src="https://latex.codecogs.com/svg.latex?\theta_{1}\leftarrow\theta_{0}-\nabla_{\theta_{0}}L_{in}(\alpha_{0},\theta_{0})" />, which is called *inner loop*. use the Then they use *outer loss* <img src="https://latex.codecogs.com/svg.latex?L_{out}" /> perform updates on neural network and meta parameters: <img src="https://latex.codecogs.com/svg.latex?\theta_3=\theta_0-\nabla_{\theta_0}(\alpha_0,\theta_2)" />, <img src="https://latex.codecogs.com/svg.latex?\alpha_1=\alpha_0-\nabla_{\alpha_0}(\alpha_0,\theta_2)" />. We call the above inner loop and meta update is one *outer iteration*.

![fig](./figs/online_mode.png)

*Online Meta-Learning*

The biggest difference between offline and online meta-learning is that the outer loss in online meta-learning does not update the neural network, which takes from the network parameters in the last inner iteration directly. The online update schema is often used in the meta reinforcement learning.

*Meta-Optim* supports both two update strategies. Users only need to pass one argument and then *Meta-Optim* will automatically deal with the network update process.

## Usage

### Few-Shot Classification

Let's start with a few-shot classification task introduced in the famous MAML algorithm. This code has been modified from [Higher's PyTorch MAML implementation](https://github.com/facebookresearch/higher/blob/main/examples/maml-omniglot.py). The few-shot classification task does inner loop and back-propagates meta-gradient on each task.

Inner loop should run with the `with` statement:

```python
import MetaOptim

for train_iter in range(train_iters):
    # prepare data
    #...

    for task_iter in range(num_tasks):
        with MetaOptim.SlidingWindow(offline=True):
            for inner_iter in range(inner_iters):
                # compute inner loss and perform inner update
                # ...

            # compute outer loss and back-propagate
            # ...

        # update and finish one train iteration
        # ...
```

The argument `offline` stands for update network parameters in offline or online manner.

Assume we use SGD for the inner loop network update and Adam for the outer network update, the code could be:

```python
import torch
import MetaOptim

# initialize the network and dataloader
net = Net()
loader = Loader()
outer_optim = torch.optim.Adam(net.parameters())

for train_iter in range(train_iters):
    x_spt, y_spt, x_qry, y_qry = next(loader)
    outer_optim.zero_grad()
    for task_iter in range(num_tasks):
        # use network as input argument instead of calling method `parameters`
        inner_optim = MetaOptim.MetaSGD([net])

        with MetaOptim.SlidingWindow(offline=True):
            for inner_iter in range(inner_iters):
                # compute inner loss and perform inner update
                spt_logits = net(x_spt[task_iter])
                spt_loss = F.cross_entropy(spt_logits, y_spt[task_iter])
                inner_optim.step(spt_loss)

            # compute the outer loss and back-propagate it
            qry_logits = net(x_qry[task_iter])
            qry_loss = F.cross_entropy(qry_logits, y_qry[task_iter])
            qry_loss.backward()

        # update and finish one train iteration
        outer_optim.step()
```

We address that the initialization of the meta-optimizer is `inner_optim = meta_optim.MetaSGD([net])`, we use network as input argument.

### Meta-Gradient Reinforcement Learning

Here we propose another example, the MGRL algorithm. The actor-critic based reinforcement learning algorithms always contain a simulation environment, an actor, and a critic. The actor takes as input the given environment observation and output action. The simulation environment takes as input the action and outputs the next environment observation after interacting with the environment together with the reward for that action. The critic takes as input the observation-action pair and outputs the "quality" of taking such action given the observation. The "quality" could be the Bellman backup or other value functions. The critic tries to minimize the error of the predicted "quality" and the actor tries to output high "quality" action.

The MGRL algorithm makes the some hyper-parameters, e.g.,  the discount factor <img src="https://latex.codecogs.com/svg.latex?\gamma" /> used in the Bellman backup, trainable and update them in a meta style. The code for the MGRL could be the following format, assume <img src="https://latex.codecogs.com/svg.latex?\gamma" /> is the meta-parameter:

```python
import torch
import MetaOptim

# initialize
env = Env()
actor = Actor()
critic = Critic()
gamma = torch.tensor(0.99, requires_grad=True)

actor_optim = MetaOptim.MetaAdam([actor])
critic_optim = MetaOptim.MetaAdam([critic])
gamma_optim = torch.optim.Adam([gamma])

for train_iter in range(train_iters):
    with MetaOptim.SlidingWindow(offline=False):
        for inner_iter in range(inner_iters):
            with torch.no_grad():
                # interact with environment and output a series data
                actions, observations, rewards, dones = env_interact(env, actor)
                returns = compute_returns(rewards, dones, gamma)

            # compute inner loss and perform inner update
            critic_loss = critic_loss_fn(returns, critic)
            actor_loss = actor_loss_fn(observations, actor, critic)
            critic_optim.step(critic_loss)
            actor_optim.step(actor_loss)

        with torch.no_grad():
            # interact with environment and output a series data
            actions, observations, rewards, dones = env_interact(env, actor)
            returns = compute_returns(rewards, dones, gamma)

        # compute the outer loss
        critic_loss = critic_loss_fn(returns, critic)
        actor_loss = actor_loss_fn(observations, actor, critic)
        
        # back-propagate the outer loss and update gamma
        gamma_optim.zero_grad()
        critic_loss.backward()
        actor_loss.backward()
        gamma_optim.step()
```

## Examples

The few-shot example [maml-omniglot.py](examples/few-shot/maml-omniglot.py) can be found in the example directory.

![fsl](./examples/few-shot/maml-accs-MetaOptim.png)

*Result of the few-shot MAML example.*

## License

`Meta-Optim` is released under Apache License Version 2.0.
