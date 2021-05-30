from typing import Optional
import torch
from torch import Tensor
from torch import nn
import torch.nn.functional as F
# Copyright (c)  2020  Xiaomi Corporation (authors: Daniel Povey, Haowen Qiu)
# Apache 2.0
from torch.utils.tensorboard import SummaryWriter
from snowfall.models import AcousticModel
from snowfall.training.diagnostics import measure_weight_norms


class CNNReluBN(nn.Module):
    """Args:
        idim: Input dimension e.g. 40 or 80 for MFCC
        odim: Output dimension e.g. 256
        (batch_size, input_length, num_features). (#batch, time, idim)
    """
    def __init__(self, idim: int, odim: int) -> None:
        """Construct one layer cnn --> relu ---> batchnorm object
           Args:
             idim:  Number of features at input, e.g. 40 or 80 for MFCC
             odim:  Output dimension (number of features), e.g. 256
        """
        super().__init__()
        self.convolutions = nn.ModuleList()
        self.batchnorms = nn.ModuleList()
        layers = []
        #self.convolutions.append(torch.nn.Conv2d(1, 64, 3, stride=1, padding=1))
        #self.convolutions.append(torch.nn.Conv2d(64, 64, 3, stride=1, padding=1))
        #self.convolutions.append(torch.nn.Conv2d(64, 128, 3, stride=1, padding=1))
        #self.convolutions.append(torch.nn.Conv2d(128, 128, 3, stride=1, padding=1))
        #self.batchnorms.append(nn.BatchNorm2d(64))
        #self.batchnorms.append(nn.BatchNorm2d(64))
        #self.batchnorms.append(nn.BatchNorm2d(128))
        #self.batchnorms.append(nn.BatchNorm2d(128))
        layers.append(torch.nn.Conv2d(1, 64, 3, stride=1, padding=1))
        layers.append(torch.nn.ReLU())
        layers.append(torch.nn.BatchNorm2d(64))
        layers.append(torch.nn.Conv2d(64, 64, 3, stride=1, padding=1))
        layers.append(torch.nn.ReLU())
        layers.append(torch.nn.BatchNorm2d(64))
        layers.append(torch.nn.Conv2d(64, 128, 3, stride=1, padding=1))
        layers.append(torch.nn.ReLU())
        layers.append(torch.nn.BatchNorm2d(128))
        layers.append(torch.nn.MaxPool2d(3, stride=(1, 2),  padding=1))
        layers.append(torch.nn.Conv2d(128, 128, 3, stride=1, padding=1))
        layers.append(torch.nn.ReLU())
        layers.append(torch.nn.BatchNorm2d(128))
        layers.append(torch.nn.Conv2d(128, 256, 3, stride=1, padding=1))
        layers.append(torch.nn.ReLU())
        layers.append(torch.nn.BatchNorm2d(256))
        layers.append(torch.nn.MaxPool2d(3, stride=(1, 2),  padding=1))
        layers.append(torch.nn.Conv2d(256, 256, 3, stride=1, padding=1))
        layers.append(torch.nn.ReLU())
        layers.append(torch.nn.BatchNorm2d(256))
        self.layers = nn.Sequential(*layers)
        self.out = nn.Linear(5120, odim)

    def forward(self, x: Tensor) -> Tensor:
        """
        Args:
            x: Input tensor of dimension (batch_size, input_length, num_features). (#batch, time, idim).
        Returns:
           torch.Tensor: Subsampled tensor of dimension (batch_size, input_length, d_model).
           d_model: Embedding dimension.
        """
        x = x.unsqueeze(1)  # (b, c, t, f)
        #for conv, bn in zip(self.convolutions, self.batchnorms):
        #    x = F.relu(bn(conv(x)))
        x = self.layers(x)
        b, c, t, f = x.size()
        x = self.out(x.transpose(1, 2).contiguous().view(b, t, c * f))
        #x = x.transpose(1, 2).contiguous().view(b, t, c * f)
        return x


class CnnTdnn1a(AcousticModel):
    """
    Args:
        num_features (int): Number of input features
        num_classes (int): Number of output classes
    """

    def __init__(self, num_features: int, num_classes: int, subsampling_factor: int = 3) -> None:
        super().__init__()
        self.num_features = num_features
        self.num_classes = num_classes
        self.subsampling_factor = subsampling_factor
        self.cnnrelubn = CNNReluBN(num_features, 1536)
        self.tdnn = nn.Sequential(
            nn.Conv1d(in_channels=1536,
                      out_channels=500,
                      kernel_size=1,
                      stride=1,
                      padding=1), nn.ReLU(inplace=True),
            nn.BatchNorm1d(num_features=500, affine=False),
            nn.Conv1d(in_channels=500,
                      out_channels=2000,
                      kernel_size=3,
                      stride=1,
                      padding=1), nn.ReLU(inplace=True),
            nn.BatchNorm1d(num_features=2000, affine=False),
            nn.Conv1d(in_channels=2000,
                      out_channels=2000,
                      kernel_size=3,
                      stride=self.subsampling_factor,  # <---- stride=3: subsampling_factor!
                      padding=1), nn.ReLU(inplace=True),
            nn.BatchNorm1d(num_features=2000, affine=False),
            nn.Conv1d(in_channels=2000,
                      out_channels=2000,
                      kernel_size=1,
                      stride=1,
                      padding=0), nn.ReLU(inplace=True),
            nn.BatchNorm1d(num_features=2000, affine=False),
            nn.Conv1d(in_channels=2000,
                      out_channels=num_classes,
                      kernel_size=1,
                      stride=1,
                      padding=0))

    def forward(self, x: Tensor) -> Tensor:
        r"""
        Args:
            x (torch.Tensor): Tensor of dimension (batch_size, num_features, input_length).

        Returns:
            Tensor: Predictor tensor of dimension (batch_size, number_of_classes, input_length).
        """
        x = x.permute(0, 2, 1)  # (B, F, T) -> (B, T, F)
        x = self.cnnrelubn(x)
        x = x.permute(0, 2, 1)  # (B, T, F) -> (B, F, T)
        x = self.tdnn(x)
        x = nn.functional.log_softmax(x, dim=1)
        return x

    def write_tensorboard_diagnostics(
            self,
            tb_writer: SummaryWriter,
            global_step: Optional[int] = None
    ):
        tb_writer.add_scalars(
            'train/weight_l2_norms',
            measure_weight_norms(self, norm='l2'),
            global_step=global_step
        )
        tb_writer.add_scalars(
            'train/weight_max_norms',
            measure_weight_norms(self, norm='linf'),
            global_step=global_step
        )
