import numpy as np
from carsdata.utils.data import DataFile
from carsdata.utils.files import read_txt_file
from .fixtures import txt_wave_pos_file


def test_data_file(txt_wave_pos_file):
    measures, spectral_units, pos = read_txt_file(txt_wave_pos_file)
    data = DataFile(str(txt_wave_pos_file))
    assert data.spectral_units is None
    assert data.pos is None
    np.testing.assert_allclose(data.measures, measures)
    np.testing.assert_allclose(data.spectral_units, spectral_units)
    np.testing.assert_allclose(data.pos, pos)
