"""Settings file for Classifier"""
from sklearn.cluster import KMeans, MiniBatchKMeans

from classifier.models import RandomForest, SingleClass, XGBoost

WORKSPACE = '/workspace/'

RASTER_EXTENSIONS = frozenset(['.tif', '.vrt', '.jp2'])

US_ALGORITHMS = ['us_kmeans', 'us_kmeans_minibatch']

# ##----THE ALGORITHMS---###
ALGORITHMS = [
    "randomforest", "xgboost", "singleclass", "us_kmeans",
    "us_kmeans_minibatch"
]
CLASSIFIERS = [RandomForest, XGBoost, SingleClass, KMeans, MiniBatchKMeans]
ALGORITHM_DICT = dict(zip(ALGORITHMS, CLASSIFIERS))

PARAMETERS = {
    "app": {
        "algorithm": "randomforest",
        "window": 1024,
        "model": None,
        "model_save": False,  # Save a model file which can be re-used
        "samples": None,
        "log_level": "INFO",
        "threads": -1,
        "imputation": True,
        "imputation_strategy": "mean",
        "imputation_constant": -9999,
        "rasters_are_timeseries": False
    },
    "supervised": {
        "probability": True,
        "all_probabilities": False,
        "boxplots": False,  # Plot Boxplots for samples
        "remove_outliers": True,  # Remove outliers from the training data
        "optimization": {
            "optimize": False,  # Optimize the model parameters
            "optimize_number": 10,  # Number of iterations for optimization
            "max_features": ['auto', 'sqrt', 'log2'],
            "max_leaf_nodes": [3, 5, 7],
            "max_depth": [None, 1, 3, 10, 20000],
            "n_estimators": [10, 50, 100]
        }
    },
    "unsupervised": {
        "nclasses": 2,  # Number of classes for unsupervised
        "trainfraction": 1.0  # Fraction of raster used for training
    },
    "accuracy": {
        "perform_assesment": True,  # Perform accuracy assessment
        "testfraction": 0.25,  # Fraction of data to use for training
    }
}

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
IMPUTATION_STRATEGIES = ["mean", "median",
                         "most_frequent", "constant", "interpolate"]

OPTIMIZE_RANDOMFOREST_MAX_FEATURES = ["auto", "sqrt", "log2"]
