"Fixture for setting up the tests, yield CliRunner() and tearing them down"
import os
import shutil
from collections import OrderedDict
from pathlib import Path

import fiona
import numpy as np
import pytest
import rasterio
from classifier.settings import WORKSPACE
from click.testing import CliRunner


@pytest.fixture
def runner(test_arg):
    """Setup, yield CliRunner() and teardown"""
    # setup
    print("SETUP")
    is_timeseries_test = test_arg[0]
    is_supervised_test = test_arg[1]
    # Rasters
    nowhere = 0.0
    pixel_size = 2.0

    transform = rasterio.Affine(
        pixel_size,
        nowhere,
        nowhere,
        nowhere,
        -pixel_size,
        nowhere
    )

    raster_folder = Path(WORKSPACE) / "integration_test_rasters"
    raster_folder.mkdir()

    if is_timeseries_test:
        raster_names = ['test_raster_008570_2020-07-01T000000Z_mean.tif',
                        'test_raster_008570_2020-08-01T000000Z_mean.tif']
    else:
        raster_names = ['test_raster_008570_2020-07-01T000000Z_mean.tif']
    raster_paths = [raster_folder / raster_name
                    for raster_name in raster_names]

    raster_values = [
        np.array([
            np.full((10, 10), [1, 1, 1, 1, 1, 100, 100, 100, 100, 100]),
            np.full((10, 10), [2, 2, 2, 2, 2, 101, 101, 101, 101, 101])
        ], dtype=np.uint8),
        np.array([
            np.full((10, 10), [1, 1, 1, 1, 1, 100, 100, 100, 100, 100]),
            np.full((10, 10), [2, 2, 2, 2, 2, 101, 101, 101, 101, 101])
        ], dtype=np.uint8),
    ]

    for raster_path, data in zip(raster_paths, raster_values):
        with rasterio.open(
            raster_path,
            'w',
            driver='GTiff',
            height=data.shape[1],
            width=data.shape[2],
            count=data.shape[0],
            dtype='uint8',
            crs='+proj=latlong',
            transform=transform
        ) as dst:
            dst.write(data)

    if is_supervised_test:
        # Train polygons
        x_min, y_min, x_max, y_max = 0, -20, 10, 0
        window_polygon_1 = [[(x_min, y_min),
                             (x_min, y_max),
                             (x_max, y_max),
                             (x_max, y_min)]]

        x_min, y_min, x_max, y_max = 10, -20, 20, 0
        window_polygon_2 = [[(x_min, y_min),
                             (x_min, y_max),
                             (x_max, y_max),
                             (x_max, y_min)]]

        polygon1 = {
            "properties": {
                "id": 0,
                "fid": 1
            },
            "geometry": {
                "coordinates": window_polygon_1,
                "type": "Polygon"
            }
        }
        polygon2 = {
            "type": "Feature",
                    "properties": {
                        "id": 1,
                        "fid": 2
                    },
            "geometry": {
                        "coordinates": window_polygon_2,
                        "type": "Polygon"
                    }
        }

        train_polygons = [polygon1, polygon2]
        schema = {
            "geometry": "Polygon",
            "properties": OrderedDict([("id", "int"), ("fid", "int")])
        }
        rois_path = Path(WORKSPACE) / 'integration_test_rois.gpkg'
        with fiona.open(rois_path,
                        "w",
                        driver="GPKG",
                        crs="+proj=latlong",
                        schema=schema) as src:
            src.writerecords(train_polygons)

    yield CliRunner()

    # teardown
    shutil.rmtree(Path(WORKSPACE) / "integration_test_rasters")
    if is_supervised_test:
        os.remove(Path(WORKSPACE) / 'integration_test_rois.gpkg')
    # Delete classification result
    shutil.rmtree(Path(WORKSPACE) / "test_result")
