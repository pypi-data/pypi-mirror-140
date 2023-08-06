import pytest
import numpy as np

SPATIAL_SHAPE = 10, 10
CUBE_SHAPE = 10, 10, 10
NB_PIXELS = np.prod(SPATIAL_SHAPE)
CUBE_PIXELS = np.prod(CUBE_SHAPE)
SPECTRAL_SHAPE = 150
SPECTRAL_UNITS = np.arange(150, dtype=float)
DATA = np.reshape(np.arange(NB_PIXELS * SPECTRAL_SHAPE, dtype=float), (NB_PIXELS, SPECTRAL_SHAPE))
CUBE = np.reshape(np.arange(CUBE_PIXELS * SPECTRAL_SHAPE, dtype=float), (CUBE_PIXELS, SPECTRAL_SHAPE))
LINES_IDX = np.arange(NB_PIXELS, dtype=float) // SPATIAL_SHAPE[1]
COLUMNS_IDX = np.arange(NB_PIXELS, dtype=float) % SPATIAL_SHAPE[1]
POS = np.concatenate([LINES_IDX[..., np.newaxis], COLUMNS_IDX[..., np.newaxis]], axis=1)


@pytest.fixture(scope="session")
def txt_wave_pos_file(tmp_path_factory):
    tmp_file = tmp_path_factory.mktemp("data") / "data_wave_pow.txt"
    with open(tmp_file, 'ab') as f:
        np.savetxt(f, SPECTRAL_UNITS[np.newaxis], delimiter='\t')
        to_write = np.concatenate([POS, DATA], axis=1)
        np.savetxt(f, to_write, delimiter='\t')
    return tmp_file


@pytest.fixture(scope="session")
def txt_wave_file(tmp_path_factory):
    tmp_file = tmp_path_factory.mktemp("data") / "data_wave_pow.txt"
    with open(tmp_file, 'ab') as f:
        np.savetxt(f, SPECTRAL_UNITS[np.newaxis], delimiter='\t')
        np.savetxt(f, DATA, delimiter='\t')
    return tmp_file


@pytest.fixture(scope="session")
def txt_cube_wave_file(tmp_path_factory):
    tmp_file = tmp_path_factory.mktemp("data") / "data_wave_cube.txt"
    with open(tmp_file, 'ab') as f:
        np.savetxt(f, SPECTRAL_UNITS[np.newaxis], delimiter='\t')
        np.savetxt(f, CUBE, delimiter='\t')
    return tmp_file