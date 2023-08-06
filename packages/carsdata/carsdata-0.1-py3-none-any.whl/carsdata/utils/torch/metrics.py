import torch
from torch.nn import MSELoss, KLDivLoss
from carsdata.utils.torch.losses import SADLoss
from carsdata.utils.metrics import Metric
from carsdata.utils.types import Array, Real
from carsdata.utils.torch.common import convert_to_tensor


class MSE(Metric):
    _mse: MSELoss

    def __init__(self):
        super().__init__()
        self._mse = MSELoss()

    def compute(self, data: Array, result: Array) -> Real:
        data, result = convert_to_tensor(data, result)
        return self._mse(result, data).item()


class SAD(Metric):
    _sad: SADLoss

    def __init__(self):
        super().__init__()
        self._sad = SADLoss()

    def compute(self, data: Array, result: Array) -> Real:
        data, result = convert_to_tensor(data, result)
        return self._sad(result, data).item()


class KLDiv(Metric):
    _kldiv: KLDivLoss
    result_log: bool

    def __init__(self, result_log: bool = False, data_log: bool = False):
        super().__init__()
        self._kldiv = KLDivLoss(log_target=data_log, reduction='batchmean')
        self.result_log = result_log

    def compute(self, data: Array, result: Array) -> Real:
        data, result = convert_to_tensor(data, result)
        if not self.result_log:
            result = result.log()
        return self._kldiv(result, data).item()

    @property
    def data_log(self) -> bool:
        return self._kldiv.log_target

    @data_log.setter
    def data_log(self, data_log: bool) -> None:
        self._kldiv.log_target = data_log