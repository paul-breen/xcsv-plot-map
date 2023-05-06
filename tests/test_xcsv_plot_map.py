import os

import pytest
import cartopy.crs as ccrs

import xcsv
import xcsv.plot_map as xpm

base = os.path.dirname(__file__)

def test_version():
    assert xpm.__version__ == '0.3.0'

@pytest.fixture
def short_point_test_datasets():
    in_files = [f'{base}/data/short-test-data-{n}.csv' for n in range(1, 4)]
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_bbox_test_datasets():
    in_files = [f'{base}/data/short-test-data-{n}.csv' for n in range(4, 7)]
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_point_coord_mislabelled_test_data():
    in_files = [base + '/data/short-point-coord-mislabelled-test-data.csv']
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_point_coord_missing_test_data():
    in_files = [base + '/data/short-point-coord-missing-test-data.csv']
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_point_coord_missing_test_key_test_data():
    in_files = [base + '/data/short-point-coord-missing-test-key-test-data.csv']
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_point_coord_no_units_test_data():
    in_files = [base + '/data/short-point-coord-no-units-test-data.csv']
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_bbox_coord_mislabelled_test_data():
    in_files = [base + '/data/short-bbox-coord-mislabelled-test-data.csv']
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_bbox_coord_missing_test_data():
    in_files = [base + '/data/short-bbox-coord-missing-test-data.csv']
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_bbox_coord_missing_test_key_test_data():
    in_files = [base + '/data/short-bbox-coord-missing-test-key-test-data.csv']
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

@pytest.fixture
def short_bbox_coord_no_units_test_data():
    in_files = [base + '/data/short-bbox-coord-no-units-test-data.csv']
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

def test_get_crs_class_from_string():
    crs_str = 'PlateCarree'
    expected = ccrs.PlateCarree()
    actual = xpm.Plot().get_crs_class_from_string(crs_str)
    assert actual == expected

def test_get_crs_class_from_string_non_existent_crs():
    crs_str = 'DummyNonExistentCRS'

    with pytest.raises(AttributeError):
        actual = xpm.Plot().get_crs_class_from_string(crs_str)

def test_get_site_plot_extent_from_point(short_point_test_datasets):
    p = xpm.Plot()
    offset = 5
    expected = [-78.16 - offset, -65.46 + offset, -74.45 - offset, -73.86 + offset]
    actual = p.get_site_plot_extent_from_point(short_point_test_datasets)
    assert actual == expected

def test_get_site_plot_extent_from_point_custom_offset(short_point_test_datasets):
    p = xpm.Plot()
    offset = 10
    expected = [-78.16 - offset, -65.46 + offset, -74.45 - offset, -73.86 + offset]
    actual = p.get_site_plot_extent_from_point(short_point_test_datasets, offset=offset)
    assert actual == expected

def test_get_site_plot_extent_from_point_non_existent_keys(short_point_test_datasets):
    p = xpm.Plot()
    xkey, ykey = 'non-existent-xkey', 'non-existent-ykey'

    with pytest.raises(ValueError):
        actual = p.get_site_plot_extent_from_point(short_point_test_datasets, xkey=xkey, ykey=ykey)

def test_get_site_plot_extent_from_bbox(short_bbox_test_datasets):
    p = xpm.Plot()
    offset = 5
    expected = [-78.16 - offset, -65.46 + offset, -74.45 - offset, -73.86 + offset]
    actual = p.get_site_plot_extent_from_bbox(short_bbox_test_datasets)
    assert actual == expected

def test_get_site_plot_extent_from_bbox_custom_offset(short_bbox_test_datasets):
    p = xpm.Plot()
    offset = 10
    expected = [-78.16 - offset, -65.46 + offset, -74.45 - offset, -73.86 + offset]
    actual = p.get_site_plot_extent_from_bbox(short_bbox_test_datasets, offset=offset)
    assert actual == expected

def test_get_site_plot_extent_from_bbox_non_existent_keys(short_bbox_test_datasets):
    p = xpm.Plot()
    xminkey, xmaxkey, yminkey, ymaxkey = 'non-existent-xminkey', 'non-existent-xmaxkey',  'non-existent-yminkey', 'non-existent-ymaxkey'

    with pytest.raises(ValueError):
        actual = p.get_site_plot_extent_from_bbox(short_bbox_test_datasets, xminkey=xminkey, xmaxkey=xmaxkey, yminkey=yminkey, ymaxkey=ymaxkey)

def test_get_site_plot_extent_from_point_mislabelled_coord(short_point_coord_mislabelled_test_data):
    p = xpm.Plot()

    with pytest.raises(ValueError):
        actual = p.get_site_plot_extent_from_point(short_point_coord_mislabelled_test_data)

def test_get_site_plot_extent_from_point_missing_coord(short_point_coord_missing_test_data):
    p = xpm.Plot()

    with pytest.raises(ValueError):
        actual = p.get_site_plot_extent_from_point(short_point_coord_missing_test_data)

def test_get_site_plot_extent_from_point_missing_test_key_coord(short_point_coord_missing_test_key_test_data):
    p = xpm.Plot()

    with pytest.raises(ValueError):
        actual = p.get_site_plot_extent_from_point(short_point_coord_missing_test_key_test_data)

def test_get_site_plot_extent_from_point_no_units_coord(short_point_coord_no_units_test_data):
    p = xpm.Plot()
    offset = 5
    expected = [-65.46 - offset, -65.46 + offset, -73.86 - offset, -73.86 + offset]
    actual = p.get_site_plot_extent_from_point(short_point_coord_no_units_test_data)
    assert actual == expected

def test_get_site_plot_extent_from_bbox_mislabelled_coord(short_bbox_coord_mislabelled_test_data):
    p = xpm.Plot()

    with pytest.raises(ValueError):
        actual = p.get_site_plot_extent_from_bbox(short_bbox_coord_mislabelled_test_data)

def test_get_site_plot_extent_from_bbox_missing_coord(short_bbox_coord_missing_test_data):
    p = xpm.Plot()

    with pytest.raises(ValueError):
        actual = p.get_site_plot_extent_from_bbox(short_bbox_coord_missing_test_data)

def test_get_site_plot_extent_from_bbox_missing_test_key_coord(short_bbox_coord_missing_test_key_test_data):
    p = xpm.Plot()

    with pytest.raises(ValueError):
        actual = p.get_site_plot_extent_from_bbox(short_bbox_coord_missing_test_key_test_data)

def test_get_site_plot_extent_from_bbox_no_units_coord(short_bbox_coord_no_units_test_data):
    p = xpm.Plot()
    offset = 5
    expected = [-78.16 - offset, -65.46 + offset, -74.45 - offset, -73.86 + offset]
    actual = p.get_site_plot_extent_from_bbox(short_bbox_coord_no_units_test_data)
    assert actual == expected

@pytest.mark.parametrize(['plot_on_map','expected'], [
(False, 2),
(True, 1)
])
def test__setup_fallback_figure_and_axes(plot_on_map, expected):
    p = xpm.Plot()
    p._setup_fallback_figure_and_axes(plot_on_map=plot_on_map)
    actual = len(p.axs)
    assert actual == expected

