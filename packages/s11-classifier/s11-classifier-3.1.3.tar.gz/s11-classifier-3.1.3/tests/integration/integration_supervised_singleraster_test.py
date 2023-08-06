"Supervised single raster integration test for classifier"
from pathlib import Path

import numpy as np
import pytest
import rasterio
from classifier.cli import classification
from classifier.settings import WORKSPACE
from classifier.utils.general import save_config_as_json


@pytest.mark.parametrize('test_arg',
                         [[False, True]])
def test_supervised_singleraster_randomforest(runner):
    """
    Test for running a supervised randomforest classification
    on a single raster
    """
    save_config_as_json(threads=1, algorithm="randomforest",
                        remove_outliers=False)

    rois_path = Path(WORKSPACE) / 'integration_test_rois.gpkg'
    runner.invoke(classification, [
        "--name", 'test_result', '--overwrite', True,
        '--rois', rois_path, "integration_test_rasters"])
    directory = Path(WORKSPACE) / 'test_result' / 'classification.tif'
    with rasterio.open(directory, 'r') as dst:
        result = dst.read(1)
        assert np.all(result[:, 0:4] == result[0, 0])
        assert np.all(result[:, 5:10] == result[0, 5])


@pytest.mark.parametrize('test_arg',
                         [[False, True]])
def test_supervised_singleraster_xgboost(runner):
    """
    Test for running a supervised xgboost classification
    on a single raster
    """
    save_config_as_json(threads=1, algorithm="xgboost",
                        remove_outliers=False)

    rois_path = Path(WORKSPACE) / 'integration_test_rois.gpkg'
    runner.invoke(classification, [
        "--name", 'test_result', '--overwrite', True,
        '--rois', rois_path, "integration_test_rasters"])
    directory = Path(WORKSPACE) / 'test_result' / 'classification.tif'
    with rasterio.open(directory, 'r') as dst:
        result = dst.read(1)
        assert np.all(result[:, 0:4] == result[0, 0])
        assert np.all(result[:, 5:10] == result[0, 5])


@pytest.mark.parametrize('test_arg',
                         [[False, True]])
def test_supervised_singleraster_singleclass(runner):
    """
    Test for running a supervised singleclass classification
    on a single raster
    """
    save_config_as_json(threads=1, algorithm="singleclass",
                        remove_outliers=False)

    rois_path = Path(WORKSPACE) / 'integration_test_rois.gpkg'
    runner.invoke(classification, [
        "--name", 'test_result', '--overwrite', True,
        '--rois', rois_path, "integration_test_rasters"])
    directory = Path(WORKSPACE) / 'test_result' / 'classification.tif'
    with rasterio.open(directory, 'r') as dst:
        result = dst.read(1)
        assert np.all(result[:, 0:4] == result[0, 0])
        assert np.all(result[:, 5:10] == result[0, 5])
