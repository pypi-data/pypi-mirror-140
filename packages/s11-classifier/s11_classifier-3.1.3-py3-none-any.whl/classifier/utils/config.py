""" Setup and load the configurations """
import json
import logging
import pathlib
import sys
from dataclasses import dataclass
from typing import List, Optional

import dacite
from marshmallow import Schema, ValidationError, fields, validate

from classifier.settings import (ALGORITHMS, IMPUTATION_STRATEGIES, LOG_LEVELS,
                                 OPTIMIZE_RANDOMFOREST_MAX_FEATURES,
                                 PARAMETERS)

UTILS_CONFIG_LOGGER = logging.getLogger(__name__)


class PathField(fields.Field):
    """ Field that serializes to a string and deserializes to a pathlib.Path."""

    def _deserialize(self, value, _attr, _obj, **_kwargs) -> pathlib.Path:
        if not isinstance(value, str):
            raise ValidationError(
                "Please provide the path as a string (with quotation marks)")
        return pathlib.Path(value)

    def _serialize(self, value, *_args, **kwargs) -> str:
        if value is None:
            return ""
        return str(value)


def validate_path(path):
    """Validates if file path exists"""
    path = pathlib.Path(path)
    if not path.exists():
        raise ValidationError('Not a valid path')


def validate_filepath_model(value):
    """Validates if model path ends on .zip"""
    path = pathlib.Path(value)
    if path.suffix != '.zip':
        raise ValidationError(
            'Model path should include a model.zip at the end')


def validate_filepath_samples(value):
    """Validates if samples path ends on .csv or .pkl"""
    path = pathlib.Path(value)
    if path.suffix not in ['.csv', 'pkl']:
        raise ValidationError('Not a valid path')


def validate_app_threads(n_threads):
    """Validates number of app threads"""
    if n_threads < -1 or n_threads == 0:
        raise ValidationError(
            "App threads can't be smaller than -1. or equal 0."
            "Choose either -1(flexible number of threads) "
            "or > 0 (fixed number of threads).")


@dataclass
class AppConfiguration:
    """Dataclass which stores app config"""

    algorithm: str
    # randomforest, xgboost, singleclass,kmeans
    window: int  # Any int, preferably within 2^x
    model: Optional[pathlib.Path]  # Model File location
    model_save: bool  # Save a model file which can be re-used
    samples: Optional[pathlib.Path]  # Samples file location (csv)
    log_level: str  # Logging level
    threads: int  # of threads
    imputation: bool  # Use simple imputation for missing values
    imputation_strategy: str  # Strategy for imputation. mean,
    imputation_constant: int  # constant for imputation
    # if constant was chosen as imputation method
    rasters_are_timeseries: bool  # Rasters are timeseries


class AppConfigurationSchema(Schema):
    """Schema for the App configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    algorithm = fields.Str(validate=validate.OneOf(ALGORITHMS))
    window = fields.Int(
        validate=validate.Range(min=1, error="Value must be greater than 0"))
    model = PathField(validate=[validate_path, validate_filepath_model],
                      allow_none=True)
    model_save = fields.Bool()
    samples = PathField(
        validate=[validate_path, validate_filepath_samples], allow_none=True)
    threads = fields.Int(validate=validate_app_threads)
    log_level = fields.Str(validate=validate.OneOf(LOG_LEVELS))
    imputation = fields.Bool()
    imputation_strategy = fields.Str(
        validate=validate.OneOf(IMPUTATION_STRATEGIES))
    imputation_constant = fields.Int()
    rasters_are_timeseries = fields.Bool()


@dataclass
class OptimizeSupervisedConfiguration():
    """Dataclass which stores the optimization parameters for
    the supervised classification"""

    optimize: bool  # Optimize the model parameters
    optimize_number: int  # Number of iterations for optimization
    max_features: List[str]
    max_leaf_nodes: List[int]
    max_depth: List[Optional[int]]
    n_estimators: List[int]


class OptimizeSupervisedConfigurationSchema(Schema):
    """Schema for the optimization part of the supervised classification
    configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    optimize = fields.Bool()
    optimize_number = fields.Int(validate=validate.Range(
        min=1,
        error="Value must be greater than 0. Better value is > 5."))
    max_features = fields.List(
        fields.Str(
            validate=validate.OneOf(OPTIMIZE_RANDOMFOREST_MAX_FEATURES)))
    max_leaf_nodes = fields.List(
        fields.Int(validate=validate.Range(
            min=1, error="Values must be greater than 0."),
            allow_none=True))
    max_depth = fields.List(
        fields.Int(validate=validate.Range(
            min=1, error="Values must be greater than 0 or NONE."),
            allow_none=True))
    n_estimators = fields.List(
        fields.Int(validate=validate.Range(
            min=1,
            error="Values must be greater than 0. Recommended is 100 "
            "(sklearn-default)."),
            allow_none=True))


@dataclass
class SupervisedConfiguration:
    """Dataclass which stores supervised classification config"""

    probability: bool  # output probability map
    all_probabilities: bool
    boxplots: bool  # Plot Boxplots for samples
    remove_outliers: bool  # Remove outliers from the training data
    optimization: OptimizeSupervisedConfiguration


class SupervisedConfigurationSchema(Schema):
    """Schema for the supervised classification configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    probability = fields.Bool()
    all_probabilities = fields.Bool()
    boxplots = fields.Bool()  # Plot Boxplots for samples
    remove_outliers = fields.Bool()  # Remove outliers from the training data
    optimization = fields.Nested(OptimizeSupervisedConfigurationSchema)


@dataclass
class UnsupervisedConfiguration:
    """Dataclass which stores unsupervised classification config"""

    nclasses: int  # Number of classes for unsupervised
    trainfraction: float  # Fraction of raster used for training


class UnsupervisedConfigurationSchema(Schema):
    """Schema for the unsupervised classification configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    nclasses = fields.Int(validate=validate.Range(
        min=2, error="Value must be > 1 . This results in at least 2 classes.")
    )  # Number of classes for unsupervised
    trainfraction = fields.Float(validate=validate.Range(
        min=0.01,
        max=1.0,
        error="Fraction of data used for training should be at least 0.01 "
        "and <= 1.0(use all data for training)")
    )  # Fraction of raster used for training


@dataclass
class AccuracyConfiguration:
    """Dataclass which stores accuracy config"""

    perform_assesment: bool  # Perform accuracy assessment
    testfraction: float  # Fraction of data to use for training


class AccuracyConfigurationSchema(Schema):
    """Schema for the accuracy configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    perform_assesment = fields.Bool()  # Perform accuracy assessment
    testfraction = fields.Float(validate=validate.Range(
        min=0,
        max=1.0,
        error="Fraction of data used for testing should be > 0 when "
        "perform_assessment is True and < 1.0")
    )  # Fraction of data to use for training


class ConfigurationSchema(Schema):
    """ConfigurationSchema for nested json.
    Each section in the json will get validated with a different schema"""

    app = fields.Nested(AppConfigurationSchema)
    supervised = fields.Nested(SupervisedConfigurationSchema)
    unsupervised = fields.Nested(UnsupervisedConfigurationSchema)
    accuracy = fields.Nested(AccuracyConfigurationSchema)


@dataclass
class Configuration:
    """Main Configuration dataclass.
    Has sub dataclasses for the different parts"""
    app: AppConfiguration
    supervised: SupervisedConfiguration
    unsupervised: UnsupervisedConfiguration
    accuracy: AccuracyConfiguration


def update_config_dict(config_dict_to_update: dict, updates: dict) -> dict:
    """Updates the nested default config dict with the user
    provided nested config dict

    Args:
        config_dict_to_update (dict): nested default config dict
        updates (dict): nested dict with updates

    Returns:
        dict: updated nested dict
    """
    updated_dict = {}
    for key, value in config_dict_to_update.items():
        if key in updates:
            # key is in the updates
            if isinstance(value, dict):
                # call function recursively with sub dict to find the key
                # to be updated
                updated_dict[key] = update_config_dict(value, updates[key])
            else:
                # update the key
                updated_dict[key] = updates[key]
        else:
            # set the default value for the key, if it is not in the
            # update keys
            updated_dict[key] = config_dict_to_update[key]
    return updated_dict


def setup_config(config_path: Optional[pathlib.Path] = None):
    """Setup method for the Configuration Dataclass.
    Uses marshmallow schemas to load the json and validate
    types and values. Dacite creates dataclass from that.

    Args:
        config_path (pathlib.Path): path to json config file

    Returns:
        [dataclass]: dataclass containing configs
    """
    if config_path and config_path.is_file():
        # loads json from path
        with open(config_path, encoding='UTF-8') as file:
            config_dict = json.load(file)
            updated_config_dict = update_config_dict(PARAMETERS, config_dict)
            config_json = json.dumps(updated_config_dict)
    else:
        UTILS_CONFIG_LOGGER.info(
            "No local config file found. Using default config")
        # Use default config dictionary
        config_json = json.dumps(PARAMETERS)

    config = json_to_config(config_json)
    return config


def json_to_config(config_json: str) -> Configuration:
    """Converts the json object to a dataclass with type and value validation

    Args:
        config_json (str): JSON formatted string

    Returns:
        [dataclass]: dataclass containing configs
    """
    # validates the type and range of the config Values
    try:
        result = ConfigurationSchema().load(json.loads(config_json))
    except ValidationError as error:
        UTILS_CONFIG_LOGGER.error(error)
        sys.exit(1)

    # creates the Configuration dataclass instance from the checked data
    return dacite.from_dict(data_class=Configuration,
                            data=result
                            # config=dacite.Config(type_hooks=converters),
                            )
