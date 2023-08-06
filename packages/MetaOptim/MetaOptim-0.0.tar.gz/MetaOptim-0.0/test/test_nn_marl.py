"""
x = 1, y = 5, lr = 1
loss =  p1_0 * x * y
dloss0/dp1 = x * y
p1_1 = p1_0 - lr * x * y
loss1 = p1_1 * x * y = (p1_0 - lr * x * y) * x * y
dloss1/dlr = - x * y * x * y = -25
dloss/dy = p1_0 * x - lr * x * x * 2 * y = 3 * 1 - 1 * 1 * 1 * 2 * 5 = -7

lr = 1 - (-25) = 26, y = 5 - (-7) = 12
"""
import torch
from torch import nn

import MetaOptim as optim


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.p1 = nn.Parameter(torch.tensor(3.))

    def forward(self, x, y):
        return self.p1 * x * y


if __name__ == "__main__":
    torch.manual_seed(0)
    meta_parameter = torch.tensor(5., requires_grad=True)
    meta_lr = torch.tensor(1., requires_grad=True)
    sgd = optim.SGD([meta_parameter, meta_lr], lr=1.)  # use origin optimizer for meta-parameters
    net = Net()
    outer_sgd = optim.SGD(net.parameters(), lr=0.5)
    meta_sgd = optim.MetaSGD([net], lr=meta_lr)  # use meta optimizer for network

    print(f"before | meta_parameter: {meta_parameter}, meta_lr: {meta_lr}")
    while True:
        with optim.SlidingWindow(offline=True):
            data = torch.ones(1, 1)
            l = net(data, meta_parameter).sum()
            # update network as following
            meta_sgd.step(l)
            # print(f"in | {[p.data for p in list(net.parameters())]}")
            # l = net(data, meta_parameter).sum()

            # update meta-parameters as we used to
            outer_sgd.zero_grad()
            # sgd.zero_grad()
            l.backward()
            # sgd.step()
            outer_sgd.step()
            pass
        # print(f"after | {[p.data for p in list(net.parameters())]}")
