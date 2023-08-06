import torch
from torch import nn
import MetaOptim


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.p = nn.Parameter(torch.ones(1, 1))

    def forward(self, x):
        # h = torch.relu(self.p * x)
        h = self.p * x
        return h


net = Net()
x = 1-torch.ones(1, 1, requires_grad=True)
x = x.detach_().requires_grad_(True)
optim = MetaOptim.MetaAdam([net])
with MetaOptim.SlidingWindow():
    y = net(x)
    optim.step(y)
    net.p.backward(retain_graph=True)
    # y = net(x)
    # y.backward()
pass

# x = torch.tensor(0., requires_grad=True)
# (x ** 2).sqrt().backward()
# p = torch.tensor(1., requires_grad=True)
# y = x * p
# grad = torch.autograd.grad(y, p, create_graph=True)[0]
# exp_avg_sq = grad * grad.conj()  # the same as grad * grad
# exp_avg_sq.sqrt().backward()
# pass
