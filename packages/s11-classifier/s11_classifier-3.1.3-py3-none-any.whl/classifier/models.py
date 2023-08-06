"""File containing all model classes necessary to run the classifier"""
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBClassifier

# initiate logger
MODELS_LOGGER = logging.getLogger(__name__)


class BaseMixin:
    """A mixin class for all models. This allows for each algorithm to use the
    optimise and plotting functions"""

    def plot_time_vs_accuracy(self, out_dir: Path) -> None:
        """Plotting the training time vs the accuracy.

        Args:
            time (array): The time values to plot
            accuracy(array) The accuracy values to plot
            out_dir (Path): Output directory

        Returns:
            None
        """
        time = self.cv_df['mean_fit_time']
        accuracy = self.cv_df['mean_test_score']
        fig = plt.figure()
        axis = fig.add_subplot(111)
        axis.scatter(time, accuracy)
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Accuracy (-) ")
        plt.tight_layout()
        plt.savefig(out_dir, 'Optimisation_time.png', dpi=300)

    def random_optimise(
            self, trainx: np.ndarray, trainy: np.ndarray, out_dir: Path,
            optimise_iters=10):
        """Optimization of a parameter space using random samples from the
        parameter space

        Args:
            trainx (np.ndarray):   Training dataset features (X-values)
            trainy (np.ndarray):   Training dataset outputs
                (class names, y values)
            out_dir (Path):  The output directory path
            optimise_iters (int): The number of iterations for the optimisation.

        Returns:
            The best performing parameter combination  (dict)

        """
        MODELS_LOGGER.info("\n####-----Optimisation----#####\n")
        MODELS_LOGGER.info(
            "Starting Optimisation. This might take a while....")
        clf = RandomizedSearchCV(self,
                                 self.parameter_matrix,
                                 verbose=0,
                                 refit=True,
                                 cv=3,
                                 return_train_score=True,
                                 n_jobs=-1,
                                 n_iter=optimise_iters
                                 )
        clf.fit(trainx, trainy)
        MODELS_LOGGER.info("Best estimator: \n %s", clf.best_estimator_)
        self.cv_df = pd.DataFrame(clf.cv_results_)
        MODELS_LOGGER.debug("--Optimisation Results--\n %s",
                            self.cv_df[['mean_train_score', 'mean_test_score',
                                        'mean_fit_time']])
        parameter_set = self.cv_df['params'][self.cv_df['rank_test_score'] ==
                                             1].values[0]
        MODELS_LOGGER.debug("\nThe best parameter combination is:\n %s",
                            parameter_set)
        self.plot_time_vs_accuracy(out_dir)
        return parameter_set

# pylint: disable=too-many-ancestors


class RandomForest(RandomForestClassifier, BaseMixin):
    """RandomForest class; child of RandomForestClassifier from sk-learn"""

    def __init__(self,
                 criterion="gini",
                 max_depth=None,
                 min_samples_split=2,
                 min_samples_leaf=1,
                 min_weight_fraction_leaf=0.,
                 max_features="auto",
                 max_leaf_nodes=None,
                 min_impurity_decrease=0.,
                 min_impurity_split=None):
        super().__init__()

        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease
        self.min_impurity_split = min_impurity_split

        self.parameter_matrix = {'max_features': ['auto', 'sqrt', 'log2'],
                                 'max_depth': [None, 1, 3, 10, 20000]}


class XGBoost(XGBClassifier, BaseMixin):
    """XGBoost class, child of XGBoostclassifier model from sk-learn"""

    def __init__(self):
        super().__init__()
        self.parameter_matrix = {'learning_rate': [0.1, 0.2, 0.3],
                                 "n_estimators": [10, 20, 50, 100, 200],
                                 'max_depth': [1, 3, 5, 10]
                                 }


class SingleClass(IsolationForest, BaseMixin):

    """Singleclass class, child of IsolationForest model from sk-learn"""

    def __init__(self):
        super().__init__()

        self.parameter_matrix = {"n_estimators": [10, 20, 50, 100, 200],
                                 'max_samples': ['auto', 10, 50, 100, 200],
                                 "max_features": [0.1, 0.3, 0.5, 1.0]
                                 }
