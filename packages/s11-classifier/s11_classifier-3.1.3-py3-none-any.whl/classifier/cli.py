"The command line interface and entry point for classifier"
import logging
import os

import click

from classifier.accuracy import assess_accuracy
from classifier.classify import classify_, classify_timeseries
from classifier.settings import WORKSPACE
from classifier.utils.general import cli_init, save_config_as_json

CLI_LOGGER = logging.getLogger(__name__)


@click.group()
def cli():
    """---Classifier---
     Classification of rasters using ground truth"""


@cli.command()
@click.argument(
    'rasters',
    nargs=-1,
    type=click.Path(),
)
@click.option('--rois',
              default=None,
              type=click.Path(),
              help="""OGR supported polygon file""")
@click.option('--name',
              type=click.STRING,
              help="""Name of the output folder""")
@click.option('--overwrite',
              default=False,
              type=click.BOOL,
              help="""Overwrite Existing output folder"""
              )
@click.option('--config_location',
              default=os.path.join(WORKSPACE, 'config.json'),
              type=click.Path(),
              help="""Use a custom location for configuration file""")
def classification(name, rasters, rois, overwrite, config_location):
    """Do a traditional (un)supervised classification

    Raster input paths can be added like arguments without a prefix.
    Multiple raster paths can be added

    For additional options, create a config file in your workspace. Also see
    https://satelligence.gitlab.io/classifier/usage/configfile.html.

    """
    out_dir, rasters, rois, config = \
        cli_init(
            name,
            rasters,
            overwrite,
            config_location,
            rois
        )
    config.name = name
    if config.app.rasters_are_timeseries:
        classify_timeseries(rasters, config, out_dir, rois)
    else:
        classify_(rasters, config, out_dir, rois)


@ cli.command()
@ click.option('--name',
               type=click.STRING,
               help="""Name of the output folder""")
@ click.option('--raster',
               default=None,
               type=click.Path(),
               help="""Raster file with classification result""")
@ click.option('--rois',
               default=None,
               type=click.Path(),
               help="""OGR supported polygon file""")
@ click.option('--subset',
               default=None,
               type=click.Path(),
               help="""OGR supported polygon file""")
@ click.option('--overwrite',
               default=False,
               type=click.BOOL,
               help="""Overwrite Existing output folder""")
@ click.option('--config_location',
               default=os.path.join(WORKSPACE, 'config.json'),
               type=click.Path(),
               help="""Use a custom location for configuration file""")
def accuracy_assessment(name, raster, rois, subset, overwrite,
                        config_location):
    """Accuracy assessment.
    """
    out_dir, rasters, _, _ = cli_init(name, [raster], overwrite,
                                      config_location)

    cm_fn = os.path.join(out_dir, 'confusion_matrix_total')
    assess_accuracy(rasters[0], rois, cm_fn, subset)


@ cli.command()
def make_config():
    """Make a config file with default values in your workspace directory
    and exit"""
    save_config_as_json()


if __name__ == '__main__':
    cli()
