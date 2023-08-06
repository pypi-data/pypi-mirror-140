""" Unittests for config file"""
import copy
import json
import os
import unittest

from classifier.settings import PARAMETERS, WORKSPACE
from classifier.utils.config import (AccuracyConfiguration, AppConfiguration,
                                     Configuration,
                                     OptimizeSupervisedConfiguration,
                                     SupervisedConfiguration,
                                     UnsupervisedConfiguration, json_to_config)


class ConfigTestCase(unittest.TestCase):
    """ Testclass for config.py"""

    @classmethod
    def setUp(cls):
        algorithm = "randomforest"
        window = 1024
        model = None
        model_save = False  # Save a model file which can be re-ed
        samples = None
        log_level = "INFO"  # Logging level
        threads = -1  # of threads
        imputation = True  # e simple imputation for missing values
        imputation_strategy = "mean"  # Strategy for imputation. mean,
        rasters_are_timeseries = False  # Rasters are timeseries
        imputation_constant = -9999  # constant for imputation
        # if constant was chosen as imputation method
        probability = True
        all_probabilities = False
        optimize = False  # Optimize the model parameters
        optimize_number = 10  # Number of iterations for optimization
        max_features = ["auto", "sqrt", "log2"]
        max_leaf_nodes = [3, 5, 7]
        max_depth = [None, 1, 3, 10, 20000]
        n_estimators = [10, 50, 100]
        boxplots = False  # Plot Boxplots for samples
        remove_outliers = True  # Remove outliers from the training data
        nclasses = 2  # Number of classes for unsupervised
        trainfraction = 1.0  # Fraction of raster ed for training
        perform_assesment = True  # Perform accuracy assessment
        testfraction = 0.25  # Fraction of data to e for training

        cls.ref_config = Configuration(
            AppConfiguration(algorithm=algorithm,
                             window=window,
                             model=model,
                             model_save=model_save,
                             samples=samples,
                             log_level=log_level,
                             threads=threads,
                             imputation=imputation,
                             imputation_strategy=imputation_strategy,
                             rasters_are_timeseries=rasters_are_timeseries,
                             imputation_constant=imputation_constant),
            SupervisedConfiguration(
                probability=probability,
                all_probabilities=all_probabilities,
                boxplots=boxplots,
                remove_outliers=remove_outliers,
                optimization=OptimizeSupervisedConfiguration(
                    optimize=optimize,
                    optimize_number=optimize_number,
                    max_features=max_features,
                    max_leaf_nodes=max_leaf_nodes,
                    max_depth=max_depth,
                    n_estimators=n_estimators)),
            UnsupervisedConfiguration(nclasses, trainfraction),
            AccuracyConfiguration(perform_assesment, testfraction))

    def test_read_config_file_outputasexpected(self):
        """Config file is correctly read in"""
        params = copy.deepcopy(PARAMETERS)
        config = json_to_config(json.dumps(params))
        self.assertEqual(self.ref_config, config)

    def test_read_config_file__raises(self):
        """Raises error due to invalid config file"""
        params = copy.deepcopy(PARAMETERS)
        params['app']['model'] = "C:///:/Documen"

        with self.assertRaises(SystemExit):
            json_to_config(json.dumps(params))

    def test_read_config_file__model_not_zip_raises(self):
        """Raises error due to invalid config file
        model not .zip"""
        params = copy.deepcopy(PARAMETERS)
        params['app']['model'] = os.path.join(WORKSPACE, "model")

        with self.assertRaises(SystemExit):
            json_to_config(json.dumps(params))

    def test_read_config_file__samples_not_csv_or_pkl_raises(self):
        """Raises error due to invalid config file
        samples is not .pkl or .csv"""
        params = copy.deepcopy(PARAMETERS)
        params['app']['samples'] = os.path.join(WORKSPACE, "samples.jpg")

        with self.assertRaises(SystemExit):
            json_to_config(json.dumps(params))
