import torch
from torch.utils.data import DataLoader, TensorDataset


dataset = TensorDataset(torch.rand(20, 4))
loader = DataLoader(dataset, shuffle=True)
print(list(loader.sampler))
for x in loader:
    print(x)
