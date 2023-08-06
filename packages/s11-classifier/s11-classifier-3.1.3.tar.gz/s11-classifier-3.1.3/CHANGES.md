Changelog of Classifier
======================

3.1.3 (2022-02-25)
------------------

- Updated config doc and deleted unused parameters in config file


3.1.2 (2022-02-18)
------------------

- Fix changelog
- Fix build image name when tagged


3.1.1 (2022-02-18)
------------------

- Fix ci/cd for pages and singularity 

3.1.0 (2022-02-17)
------------------

- new config.py with a configuration dataclass. Access on config now by config. .
- New nested configuration file
- Integration tests
- Removed numpy from reqs (already in pandas reqs)
- Up requirements and loosen them in setup.py
- Fix CI/CD tagging
- Create singularity sif images on tag

3.0.1 (2022-02-10)
------------------

- Get rid of docker-in-docker in gitlab ci. use shell instead
- json dump serializes to str in default case
- Timeseries sampling expects rois to be path or file on training and prediction respectively
- Fix single class prediction
- Delete main in accuracy
- Disable matplotlib font manager as debug info was printed out

3.0.0 (2022-01-13)
------------------

- No more segmentation, Get rid of RSGISLIB
- Docker image now uses GDAL Ubuntu small (3.4.1)
- Upped all dependencies
- Upped sk-learn to 1.0.2
- Changed parallel backend from MP to joblib.
- Added support for outputs over 4GB

2.4.4 (2020-10-20)
------------------

- Fix reading labels of stored models

2.4.3 (2020-07-08)
------------------

- Fix labels of output tifs

2.4.2 (2020-07-01)
------------------

- Version not taken from env variable in settings

2.4.1 (2020-07-01)
------------------

- Use proper tempfiles for storing intermediate model files

2.4.0 (2020-06-26)
------------------

- Added accuracy asssessment independent of classifier run
- Custom configuration file location
- Made Unsupervised Classification Multithreaded
- Added K-means mini batch as an option for unsupervised classification

2.3.2 (2020-06-15)
------------------

- Dependencies fix for pypi
- Switch CI/CD configuration to use rules: https://docs.gitlab.com/ee/ci/yaml/#rules
- Fixed bug in documentation.
- Fixed links to example data in tuturial docs
- Changed Default imputation to False, because was causing issues in usage

2.3.3 (2020-06-18)
------------------

- Fix pytest dependency on hub by upping version
- Change method of how classifier stores version in models

2.3.2 (2020-06-15)
------------------

- Dependencies fix for pypi
- Switch CI/CD configuration to use rules: https://docs.gitlab.com/ee/ci/yaml/#rules
- Fixed bug in documentation.
- Fixed links to example data in tuturial docs
- Changed Default imputation to False, because was causing issues in usage

2.3.1 (2019-11-29)
------------------

- Fix: change version key in exported model

2.3.0 (2019-11-27)
------------------

- Updated documentation (theme + content)
- Models are now stored as zipfiles (Not backward compatible)
- Removed (unnecessary) LabelEncoder
- Input of timeseries and timeseries imputation
- Use of Custom segments tif for segment classfication
- Added hyperparameters lists for more custom RandomizedSearchCV
- Bugfix for classifying segments with unsupervised classification
- Store version information in `setup.py` and `__version__`

2.2.2 (2019-07-19)
------------------

- Bugfixes related to classifying segments using single class classification
- Changed outlier removal parameters to 'auto' instead of removing a fixed percentage
- Upped output from int16 to int32 to deal with higher class nrs
- Bugfix for imputation with inf values.

2.2.1 (2019-05-23)
------------------

- Fix for getting wrong data windows for unsupervised classification
- Fix for RF models getting too large
- Fix for empty single class probability

2.2.0 (2019-02-26)
------------------

- Added removal of outliers in the samples
- Added extent and Classifier version to model file
- Upped some libraries in requirements
- Output all class probabilities separately
- Classification of segments

2.1.1 (2019-01-29)
------------------

- Several Imputation bugfixes
- Samples reader bugfix
- Imputation Bugfix when imputing completely empty windows.
- Imputation Bugfix when not all columns can be imputed

2.1.0 (2018-11-29)
------------------

- Add imputation of missing values
- Sorting of parameters in config file and logging
- Fixed bug with reading of model files

2.0.1 (2018-11-14)
------------------

- Bugfix for raster paths. Only selects rasters with known extension now

2.0.0 (2018-11-08)
------------------

- Changed CLI interface to use click
- Added Sphinx for Documentation
- Added Config File option in CLI for automatic creation of config file
- Added simple segmentation