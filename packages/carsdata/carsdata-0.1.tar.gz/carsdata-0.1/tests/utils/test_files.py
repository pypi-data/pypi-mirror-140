import numpy as np
from carsdata.utils.files import read_txt_file, get_data_files
from .fixtures import SPATIAL_SHAPE, NB_PIXELS, SPECTRAL_SHAPE, SPECTRAL_UNITS, DATA, LINES_IDX, COLUMNS_IDX, POS,\
    txt_wave_pos_file, txt_wave_file, CUBE_PIXELS, CUBE_SHAPE, CUBE, txt_cube_wave_file


def test_read_txt_with_pos(txt_wave_pos_file):
    measures, spectral_units, pos = read_txt_file(txt_wave_pos_file)
    np.testing.assert_allclose(measures, np.reshape(DATA, (*SPATIAL_SHAPE, SPECTRAL_SHAPE)))
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS)
    np.testing.assert_allclose(pos, np.reshape(POS, (*SPATIAL_SHAPE, 2)))


def test_part_spectra_txt(txt_wave_pos_file):
    begin = 2
    end = 100
    measures, spectral_units, pos = read_txt_file(txt_wave_pos_file, spectral_range=(begin, end))
    np.testing.assert_allclose(measures, np.reshape(DATA, (*SPATIAL_SHAPE, SPECTRAL_SHAPE))[..., begin:end])
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS[begin:end])
    np.testing.assert_allclose(pos, np.reshape(POS, (*SPATIAL_SHAPE, 2)))


def test_read_txt_with_shape(txt_wave_file):
    measures, spectral_units, pos = read_txt_file(txt_wave_file, SPATIAL_SHAPE)
    np.testing.assert_allclose(measures, np.reshape(DATA, (*SPATIAL_SHAPE, SPECTRAL_SHAPE)))
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS)
    assert pos is None


def test_read_txt_without_shape(txt_wave_file):
    measures, spectral_units, pos = read_txt_file(txt_wave_file)
    np.testing.assert_allclose(measures, DATA)
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS)
    assert pos is None


def test_read_txt_1_pixel_with_pos(txt_wave_pos_file):
    begin = 5, 2
    nb_measures = 1, 1
    end = [begin[i] + nb_measures[i] for i in range(len(begin))]
    measures, spectral_units, pos = read_txt_file(txt_wave_pos_file, begin=begin, nb_measures=nb_measures)
    np.testing.assert_allclose(measures,
                               np.reshape(DATA, (*SPATIAL_SHAPE, SPECTRAL_SHAPE))[begin[0]:end[0], begin[1]:end[1]])
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS)
    np.testing.assert_allclose(pos, np.reshape(POS, (*SPATIAL_SHAPE, 2))[begin[0]:end[0], begin[1]:end[1]])


def test_read_txt_multiple_lines_with_pos(txt_wave_pos_file):
    begin = 5, 0
    nb_measures = 2, 10
    end = [begin[i] + nb_measures[i] for i in range(len(begin))]
    measures, spectral_units, pos = read_txt_file(txt_wave_pos_file, begin=begin, nb_measures=nb_measures)
    np.testing.assert_allclose(measures,
                               np.reshape(DATA, (*SPATIAL_SHAPE, SPECTRAL_SHAPE))[begin[0]:end[0], begin[1]:end[1]])
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS)
    np.testing.assert_allclose(pos, np.reshape(POS, (*SPATIAL_SHAPE, 2))[begin[0]:end[0], begin[1]:end[1]])


def test_read_txt_multiple_pixels_with_pos(txt_wave_pos_file):
    begin = 4, 1
    nb_measures = 2, 3
    end = [begin[i] + nb_measures[i] for i in range(len(begin))]
    measures, spectral_units, pos = read_txt_file(txt_wave_pos_file, begin=begin, nb_measures=nb_measures)
    data = np.reshape(DATA, (*SPATIAL_SHAPE, SPECTRAL_SHAPE))[begin[0]:end[0], begin[1]:end[1]]
    np.testing.assert_allclose(measures, data)
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS)
    pos_truth = np.reshape(POS, (*SPATIAL_SHAPE, 2))[begin[0]:end[0], begin[1]:end[1]]
    np.testing.assert_allclose(pos, pos_truth)


def test_read_txt_multiple_pixels_with_shape(txt_wave_file):
    begin = 4, 0
    nb_measures = 2, 3
    end = [begin[i] + nb_measures[i] for i in range(len(begin))]
    measures, spectral_units, pos = read_txt_file(txt_wave_file, SPATIAL_SHAPE, begin=begin, nb_measures=nb_measures)
    data = np.reshape(DATA, (*SPATIAL_SHAPE, SPECTRAL_SHAPE))[begin[0]:end[0], begin[1]:end[1]]
    np.testing.assert_allclose(measures, data)
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS)


def test_cube_txt_with_shape(txt_cube_wave_file):
    begin = 0, 4, 0
    nb_measures = 10, 2, 3
    end = [begin[i] + nb_measures[i] for i in range(len(begin))]
    measures, spectral_units, pos = read_txt_file(txt_cube_wave_file, CUBE_SHAPE, begin=begin, nb_measures=nb_measures)
    data = np.reshape(CUBE, (*CUBE_SHAPE, SPECTRAL_SHAPE))[begin[0]:end[0], begin[1]:end[1], begin[2]:end[2]]
    np.testing.assert_allclose(measures, data)
    np.testing.assert_allclose(spectral_units, SPECTRAL_UNITS)


def test_get_data_files(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    p = d / "d.txt"
    p.write_text('a')
    d1 = d / "d1"
    d1.mkdir()
    p1 = d1 / "d1.txt"
    p1.write_text('a')
    d2 = d / "d2"
    d2.mkdir()
    p2 = d2 / "d2.txt"
    p2.write_text('a')
    data_files = get_data_files(str(d))
    assert data_files == [str(p), str(p1), str(p2)]


def test_get_data_files_exclude(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    p = d / "d.txt"
    p.write_text('a')
    d1 = d / "d1"
    d1.mkdir()
    p1 = d1 / "d1.txt"
    p1.write_text('a')
    d2 = d / "d2"
    d2.mkdir()
    p2 = d2 / "d2.txt"
    p2.write_text('a')
    data_files = get_data_files(str(d), exclude_directories=[str(d2)])
    assert data_files == [str(p), str(p1)]