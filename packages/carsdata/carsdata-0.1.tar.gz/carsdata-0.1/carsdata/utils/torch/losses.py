import sys
import torch
from torch.nn import Module
from carsdata.utils.math import sad
from carsdata.utils.common import factory


class SADLoss(Module):
    """
    Compute spectral angle distance (SAD) between input and output. Spectra has to be at the end of the tensor.
    If reduction is 'mean', the mean between SAD over all spectra is computed.
    If reduction is 'sum', the summation over all spectra is computed.
    If reduction is 'batchmean", the summation over all spectra will be divided by batch size.
    """
    reduction: str

    def __init__(self, reduction: str = 'mean'):
        super().__init__()
        self.reduction = reduction

    def forward(self, output: torch.Tensor, truth: torch.Tensor) -> torch.Tensor:
        """
        Compute the SAD loss between output and truth.

        Parameters
        ----------
        output : Tensor
        truth : Tensor

        Returns
        -------
        Tensor
        """
        output_flat = torch.flatten(output, end_dim=-2)
        truth_flat = torch.flatten(truth, end_dim=-2)
        if output_flat.shape != truth_flat.shape:
            raise ValueError('Output and truth should have the same shape')
        loss = sad(output_flat, truth_flat)
        if self.reduction == 'sum':
            loss = torch.sum(loss)
        elif self.reduction == 'mean':
            loss = torch.sum(loss) / loss.shape[0]
        elif self.reduction == 'batchmean':
            loss = torch.sum(loss) / output.shape[0]
        return loss


def loss_factory(name: str, **kwargs) -> Module:
    return factory([sys.modules[__name__], torch.nn], name, **kwargs)

