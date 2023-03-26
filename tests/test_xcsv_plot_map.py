import os

import pytest
import cartopy.crs as ccrs

import xcsv
import xcsv.plot_map as xpm

base = os.path.dirname(__file__)

def test_version():
    assert xpm.__version__ == '0.2.0'

@pytest.fixture
def short_test_datasets():
    in_files = [f'{base}/data/short-test-data-{n}.csv' for n in range(1, 4)]
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

def test_get_site_plot_extent(short_test_datasets):
    p = xpm.Plot()
    offset = 5
    expected = [-78.16 - offset, -65.46 + offset, -74.45 - offset, -73.86 + offset]
    actual = p.get_site_plot_extent(short_test_datasets)
    assert actual == expected

def test_get_site_plot_extent_custom_offset(short_test_datasets):
    p = xpm.Plot()
    offset = 10
    expected = [-78.16 - offset, -65.46 + offset, -74.45 - offset, -73.86 + offset]
    actual = p.get_site_plot_extent(short_test_datasets, offset=offset)
    assert actual == expected

def test_get_site_plot_extent_non_existent_keys(short_test_datasets):
    p = xpm.Plot()
    xkey, ykey = 'non-existent-xkey', 'non-existent-ykey'

    with pytest.raises(KeyError):
        actual = p.get_site_plot_extent(short_test_datasets, xkey=xkey, ykey=ykey)

