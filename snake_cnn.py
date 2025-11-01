import torch
import torch.nn as nn
import torch.nn.functional as F


class snakeCNN(nn.Module):
    def __init__(self,
                 input_size : int):
        super().__init__()

        self.fc1 = nn.Linear(input_size, 16)
        self.r1 = nn.Tanh() 
        self.fc2 = nn.Linear(16, 16)
        self.r2 = nn.Tanh() 
        self.fc3 = nn.Linear(16, 4)

    def forward(self, x):
        x = torch.tensor(x, dtype=torch.float32)
        
        x = self.r1(self.fc1(x))
        x = self.r2(self.fc2(x))
        x = self.fc3(x)

        return torch.argmax(x)

