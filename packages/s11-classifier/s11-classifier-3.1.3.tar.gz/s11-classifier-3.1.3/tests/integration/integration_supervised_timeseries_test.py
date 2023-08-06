"Supervised timeseries integration test for classifier"
from pathlib import Path

import numpy as np
import pytest
import rasterio
from classifier.cli import classification
from classifier.settings import WORKSPACE
from classifier.utils.general import save_config_as_json


@pytest.mark.parametrize('test_arg',
                         [[True, True]])
def test_supervised_timeseries_randomforest(runner):
    """
    Test for running a supervised randomforest classification
    on a timeseries
    """
    save_config_as_json(threads=1, algorithm="randomforest",
                        remove_outliers=False,
                        rasters_are_timeseries=True)

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
                         [[True, True]])
def test_supervised_timeseries_xgboost(runner):
    """
    Test for running a supervised xgboost classification
    on a timeseries
    """
    save_config_as_json(threads=1, algorithm="xgboost",
                        remove_outliers=False, rasters_are_timeseries=True)

    rois_path = Path(WORKSPACE) / 'integration_test_rois.gpkg'
    runner.invoke(classification, [
        "--name", 'test_result', '--overwrite', True,
        '--rois', rois_path, "integration_test_rasters"])
    directory = Path(WORKSPACE) / 'test_result' / 'classification.tif'
    with rasterio.open(directory, 'r') as dst:
        result = dst.read(1)
        assert np.all(result[:, 0:4] == result[0, 0])
        assert np.all(result[:, 5:10] == result[0, 5])
