import time
from abc import ABC
from typing import Sequence, List, Optional, Union, Tuple
import os
import sys
import threading
from tempfile import mkdtemp
from shutil import rmtree
import numpy as np
import torch
from torch import Tensor
from torch.nn import functional
from torch.utils.data import Dataset
from carsdata.utils.files import read_txt_file, get_data_files, get_spectral_units_txt
from carsdata.utils.common import get_shape, factory
from carsdata.utils.types import DType, torch_to_numpy_dtype_dict, Shape
from carsdata.utils.math import sum_norm
from tqdm import tqdm, trange


class CARSDataset(Dataset, ABC):
    spectral_units: Optional[np.ndarray]
    train: bool

    def __init__(self, spectral_units: Optional[np.ndarray] = None, train: bool = True):
        self.spectral_units = spectral_units
        self.train = train

    def file_path(self, idx: int) -> str:
        ...


class _PatchHolder:
    folder: str
    data_paths: List[str]
    patch_size: Sequence[int]
    patch_offset: Sequence[int]
    shapes: List[np.ndarray]
    nb_patches_by_dim: np.ndarray
    nb_patches: np.ndarray
    first_idx: np.ndarray
    created: List[bool]

    def __init__(
        self, folder: str, data_paths: List[str], patch_size: Sequence[int], patch_offset: Sequence[int],
        shapes: List[np.ndarray], nb_patches_by_dim: np.ndarray, nb_patches: np.ndarray, first_idx: np.ndarray
    ) -> None:
        self.folder = folder
        self.data_paths = data_paths
        self.patch_size = patch_size
        self.patch_offset = patch_offset
        self.shapes = shapes
        self.nb_patches_by_dim = nb_patches_by_dim
        self.nb_patches = nb_patches
        self.first_idx = first_idx
        self.created = [False] * self.first_idx[-1]

    def get_patch(self, idx) -> Tensor:
        if not self.created:
            diff = self.first_idx - idx
            diff[diff > 0] = np.iinfo(diff.dtype).min
            file_idx = np.argmax(diff)
            patch_number = -diff[file_idx]
            patch_begin = np.zeros(len(self.shapes[file_idx]), dtype=int)
            file_shape = self.shapes[file_idx]
            for i in range(len(file_shape)):
                divisor = 1 if i == len(file_shape) - 1 else self.nb_patches[file_idx, -2 - i]
                patch_begin[i] = ((patch_number // divisor) % self.nb_patches_by_dim[file_idx, i]) * self.patch_offset[i]
            patch_begin = tuple(patch_begin)
            data, _, _ = read_txt_file(self.data_paths[file_idx], begin=patch_begin, nb_measures=self.patch_size)
            return torch.as_tensor(data)
        else:
            return torch.load(os.path.join(self.folder, f'{idx}.pt'))

    def make_patch(self, idx: Union[int, List[int]]) -> None:
        if isinstance(idx, int):
            idx = [idx]
        for id_patch in idx:
            if not self.created[id_patch]:
                torch.save(self.get_patch(id_patch), os.path.join(self.folder, f'{id_patch}.pt'))


def _get_patch(
    idx: int, data_paths: List[str], patch_size: Sequence[int], patch_offset: Sequence[int], shapes: List[np.ndarray],
    nb_patches_by_dim: np.ndarray, nb_patches: np.ndarray, first_idx: np.ndarray, dtype: DType = torch.double
) -> Tensor:
    diff = first_idx - idx
    diff[diff > 0] = np.iinfo(diff.dtype).min
    file_idx = np.argmax(diff)
    patch_number = -diff[file_idx]
    patch_begin = np.zeros(len(shapes[file_idx]), dtype=int)
    file_shape = shapes[file_idx]
    for i in range(len(file_shape)):
        divisor = 1 if i == len(file_shape) - 1 else nb_patches[file_idx, -2 - i]
        patch_begin[i] = ((patch_number // divisor) % nb_patches_by_dim[file_idx, i]) * patch_offset[i]
    patch_begin = tuple(patch_begin)
    data, _, _ = read_txt_file(data_paths[file_idx],shape=file_shape, begin=patch_begin,
                               nb_measures=patch_size, precision=dtype)
    return torch.as_tensor(data)


def _create_patches(
    folder: str, idx: Union[int, List[int]], data_paths: List[str], patch_size: Sequence[int], patch_offset: Sequence[int],
    shapes: List[np.ndarray], nb_patches_by_dim: np.ndarray, nb_patches: np.ndarray, first_idx: np.ndarray,
    dtype: DType = torch.double
) -> None:
    if isinstance(idx, int):
        idx = [idx]
    for id_patch in idx:
        patch = _get_patch(id_patch, data_paths, patch_size, patch_offset, shapes, nb_patches_by_dim, nb_patches,
                           first_idx, dtype)
        torch.save(patch, os.path.join(folder, f'{id_patch}.pt'))


class CARSMapDataset(CARSDataset):
    data_paths: List[str]
    data_shape: Optional[Shape]
    patch_size: Sequence[int]
    normalization: Optional[str]
    patch_offset: Sequence[int]
    train: bool
    separate_test: bool
    test_paths: Optional[List[str]]
    _shapes: List[np.ndarray]
    _nb_patches_by_dim: np.ndarray
    _nb_patches: np.ndarray
    _first_idx: np.ndarray
    _binary_files_location: Optional[str]
    _numpy_dtype: np.dtype
    _patch_holder = _PatchHolder

    def __init__(
        self, data_paths: Union[str, dict], patch_size: Sequence[int], normalization: Optional[str] = None,
        patch_offset: Optional[Sequence[int]] = None, train: bool = True, separate_test: bool = False,
        test_path: Optional[str] = None, use_binary_files: bool = True, dtype: DType = torch.double
    ) -> None:
        super().__init__(train=train)
        if isinstance(data_paths, dict):
            self.data_shape = data_paths['shape']
            data_paths = data_paths['path']
        else:
            self.data_shape = None
        if os.path.isdir(data_paths):
            self.data_paths = get_data_files(data_paths)
        else:
            self.data_paths = [data_paths]
        self.patch_size = patch_size
        self.normalization = normalization
        if patch_offset is None:
            self.patch_offset = patch_size
        else:
            self.patch_offset = patch_offset
        self.separate_test = separate_test
        if test_path is not None:
            if os.path.isdir(test_path):
                self.test_paths = get_data_files(test_path)
            else:
                self.test_paths = [test_path]
        else:
            self.test_paths = test_path
        if isinstance(dtype, torch.dtype):
            self._numpy_dtype = torch_to_numpy_dtype_dict[dtype]
        else:
            self._numpy_dtype = dtype
        self._shapes = []
        nb_patches_by_dim = []
        nb_patches = []
        self._binary_files_location = None
        for file in self.data_paths:
            if self.data_shape is not None:
                self._shapes.append(np.array(self.data_shape))
            else:
                self._shapes.append(np.array(get_shape(file)))
            patch_array = np.array(self.patch_size)
            offset_array = np.array(self.patch_offset)
            nb_patches_by_dim.append((self._shapes[-1] - (patch_array - offset_array)) // self.patch_offset)
            nb_patches.append(np.cumprod(nb_patches_by_dim[-1][::-1]))
        self._nb_patches_by_dim = np.array(nb_patches_by_dim)
        self._nb_patches = np.array(nb_patches)
        self._first_idx = np.cumsum(np.concatenate(([0], self._nb_patches[:, -1])))
        self.spectral_units = get_spectral_units_txt(self.data_paths[0], precision=self._numpy_dtype)
        if use_binary_files:
            self._binary_files_location = mkdtemp()
            # patch_holder = _PatchHolder(self._binary_files_location, self.data_paths, self.patch_size,
            #                             self.patch_offset, self._shapes, self._nb_patches_by_dim, self._nb_patches,
            #                             self._first_idx)
            # Parallelization provoke error
            #pool_obj = multiprocessing.Pool()
            #pool_obj.map(patch_holder.make_patch, range(self._first_idx[-1]))
            #print('Dataset patches creation')
            threads = []
            nb_threads = 8
            patches_by_thread = self._nb_patches[-1, -1]//nb_threads
            print('Dataset creation starts')
            start = time.time()
            for idx in range(nb_threads):
                begin = idx*patches_by_thread
                nb_patch = patches_by_thread if idx < nb_threads-1 else self._nb_patches[-1, -1]-begin
                id_patches = range(begin, begin+nb_patch)
                threads.append(threading.Thread(target=_create_patches,
                                                args=(self._binary_files_location, id_patches, self.data_paths, self.patch_size,
                                                      self.patch_offset, self._shapes, self._nb_patches_by_dim, self._nb_patches,
                                                      self._first_idx, self._numpy_dtype)))
                threads[-1].start()
            for thread in threads:
                thread.join()
            end = time.time()
            print(f'Dataset creation: {end-start}s')
            # for i in trange(self._first_idx[-1], desc='Dataset patches creation', file=sys.stdout):
            #     # Could be done differently to load max amount of data in RAM and then split into patches to speed up
            #     # patch creation
            #     torch.save(self._get_train_patch(i), os.path.join(self._binary_files_location, f'{i}.pt'))

    def __del__(self):
        if hasattr(self, '_binary_files_location') and self._binary_files_location is not None:
            rmtree(self._binary_files_location)

    def __getitem__(self, idx) -> Tensor:
        if self.train:
            if self._binary_files_location is None:
                data = self._get_train_patch(idx)
            else:
                data = torch.load(os.path.join(self._binary_files_location, f'{idx}.pt'))
        elif self.separate_test:
            data, _, _ = read_txt_file(self.test_paths[idx], shape=self.data_shape, precision=self._numpy_dtype)
            data = torch.as_tensor(data)
        else:
            data, _, _ = read_txt_file(self.data_paths[idx], shape=self.data_shape, precision=self._numpy_dtype)
            data = torch.as_tensor(data)
        if self.normalization == '0_1':
            data = data.permute((2, 0, 1))
            data_linear = data.reshape((data.shape[0], data.shape[1] * data.shape[2]))
            max_data = data_linear.max(dim=1)[0]
            min_data = data_linear.min(dim=1)[0]
            data_linear = data_linear.T
            data_linear = (data_linear - min_data) / (max_data - min_data)
            data_linear = data_linear.T
            data = data_linear.reshape(data.shape)
            data = data.permute((1, 2, 0))
        elif self.normalization == 'sum':
            data = sum_norm(data, dim=-1)
        elif self.normalization == 'softmax':
            data = functional.softmax(data, dim=-1)
        elif self.normalization == 'mean_std':
            linearized_data = torch.reshape(data, (data.shape[0]*data.shape[1], data.shape[2]))
            mean = torch.mean(linearized_data, dim=0, keepdim=True)
            std = torch.std(linearized_data, dim=0, keepdim=True)
            linearized_data = (linearized_data-mean)/std
            data = torch.reshape(linearized_data, data.shape)
        return data

    def __len__(self) -> int:
        if self.train:
            return self._first_idx[-1]
        elif self.separate_test:
            return len(self.test_paths)
        else:
            return len(self.data_paths)

    def file_path(self, idx: int) -> str:
        if self.train:
            diff = self._first_idx - idx
            diff[diff > 0] = np.iinfo(diff.dtype).min
            file_idx = np.argmax(diff)
            return self.data_paths[file_idx]
        elif self.separate_test:
            return self.test_paths[idx]
        else:
            return self.data_paths[idx]

    def _get_train_patch(self, idx) -> Tensor:
        diff = self._first_idx - idx
        diff[diff > 0] = np.iinfo(diff.dtype).min
        file_idx = np.argmax(diff)
        patch_number = -diff[file_idx]
        patch_begin = np.zeros(len(self._shapes[file_idx]), dtype=int)
        file_shape = self._shapes[file_idx]
        for i in range(len(file_shape)):
            divisor = 1 if i == len(file_shape) - 1 else self._nb_patches[file_idx, -2 - i]
            patch_begin[i] = ((patch_number // divisor) % self._nb_patches_by_dim[file_idx, i]) * self.patch_offset[i]
        patch_begin = tuple(patch_begin)
        data, _, _ = read_txt_file(self.data_paths[file_idx], shape=file_shape, begin=patch_begin,
                                   nb_measures=self.patch_size, precision=self._numpy_dtype)
        return torch.as_tensor(data)

    def _create_patch(self, idx: int) -> None:
        # Could be done differently to load max amount of data in RAM and then split into patches to speed up
        # patch creation
        torch.save(self._get_train_patch(idx), os.path.join(self._binary_files_location, f'{idx}.pt'))


class LinearCARSDataset(CARSDataset):
    data_path: str
    normalization: Optional[str]
    train: bool
    separate_test: bool
    test_path: Optional[str]
    shape: Sequence[int]
    spectral_units: np.ndarray
    _numpy_dtype: np.dtype
    _data: Tensor
    _loaded_type: str
    _len: int

    def __init__(
        self, data_path: str, normalization: Optional[str] = None, train: bool = True,
        separate_test: bool = False, test_path: Optional[str] = None, dtype: DType = torch.double
    ) -> None:
        super().__init__(train=train)
        self.data_path = data_path
        self.normalization = normalization
        self.separate_test = separate_test
        self.test_path = test_path
        if isinstance(dtype, torch.dtype):
            self._numpy_dtype = torch_to_numpy_dtype_dict[dtype]
        else:
            self._numpy_dtype = dtype
        self._loaded_type = 'None'
        self._load_data()

    def __getitem__(self, idx) -> Tensor:
        self._load_data()
        map_idx = idx//self.shape[1], idx % self.shape[1]
        data = self._data[map_idx]
        if self.normalization == 'sum':
            data = sum_norm(data, dim=-1)
        elif self.normalization == 'softmax':
            data = functional.softmax(data, dim=-1)
        return data

    def __len__(self) -> int:
        self._load_data()
        return self._len

    def file_path(self, idx: int) -> str:
        if self.train or self.test_path is None:
            return self.data_path
        else:
            return self.test_path

    def _load_data(self) -> None:
        load = False
        data = None
        if self.train or self.test_path is None:
            if self._loaded_type != 'data':
                data, self.spectral_units, _ = read_txt_file(self.data_path, precision=self._numpy_dtype)
                self._loaded_type = 'data'
                load = True
        else:
            if self._loaded_type != 'test':
                data, self.spectral_units, _ = read_txt_file(self.test_path, precision=self._numpy_dtype)
                self._loaded_type = 'test'
                load = True
        if load:
            self.shape = data.shape[:-1]
            self._len = int(np.prod(self.shape))
            self._data = torch.as_tensor(data)

    @property
    def data(self) -> Tensor:
        self._load_data()
        return torch.reshape(self._data, (self._len, self._data.shape[-1]))


def dataset_factory(name: str, **kwargs) -> Dataset:
    return factory(sys.modules[__name__], name, **kwargs)
