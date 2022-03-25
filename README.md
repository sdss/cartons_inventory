# cartons_inventory

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/cartons_inventory/badge/?version=latest)](https://cartons_inventory.readthedocs.io/en/latest/?badge=latest)

## Overview

Cartons\_inventory is package to track the content of SDSS cartons in targetdb database.
It can take as an input an rsconfig file, a curstom file or a targetdb selection criteria.
As an output it can create an input carton list (from a targetdb selection criteria), a list of CartonInfo objects with the information of the content of the cartons,
a Pandas dataframe with the parameters of every target in the carton, a Pandas dataframe with the informaion of inexisting carton versions searched along with existing
versions/categories for that carton name, and it can create an output .csv file with the information of the content of the cartons. 
The main method is process\_cartons which wraps practically all the other methods in cartons\_inventory

## Installation

To install `target_selection` do

```console
$ pip install sdss-cartons-inventory
```

## Development

New code must follow the [SDSS Coding Standards](https://sdss-python-template.readthedocs.io/en/latest/standards.html). Linting checks run as a GitHub workflow after each commit. The workflow also check that the package and dependencies can be installed. Pull Requests that don't pass the checks cannot be merged.

To test the code offline, you must install [flake8](https://flake8.pycqa.org/en/latest/) and [isort](https://pycqa.github.io/isort/) and run the following commands from the root of the package

```console
$ flake8 . --count --show-source --statistics
$ isort -c python/ bin/
```

If the command exit without error, everything should be fine.

## Usage

In this section we will review examples for using all the aplications of the cartons\_inventory package

### 1 Creating an input file from a targetdb selection criteria

To do this you have to use _origin_ ='targetdb', and _write\_input = True. Then you have to make sure the file with the output name doesnt exist or that _overwrite_=True
Then you define a selection criteria with the arguments of _versions_, _forced\_versions_, _all\_cartons_, and _carton\_name\_pattern_.

_all\_cartons_ = True means that we will search for all carton names while _all\_cartons_=False means that only cartons with a name matching _carton\_name\_pattern_ 
(which has to be defined) will be searched. The \* character can be used as a wildcard in the _carton\_name\_pattern_ string.

The _versions_ parameter can be 'all' to retrieve all the versions from each carton, 'latest' to retrieve the newest version of each carton, or 'single' to retrieve only
the versions matching the _unique\_version_ int, which has to be defined. Then you can also use the _forced\_versions_ dictionary to override the previous version criteria
for specific cartons where the keys are the name of the cartons for which you want to use a specific version, and the values are the version you want to use for each of those
cartons.

For example in the following block code we create input file ['./files/targetdb/Cartons\_sample\_Versions\_single\_and\_forced.txt'](https://github.com/sdss/cartons_inventory/blob/main/python/cartons_inventory/files/targetdb/Cartons_sample_Versions_single_and_forced.txt) with a list of cartons starting with 'bm\_rm' with _version\_pk_
49 except for carton 'bhm\_rm\_core' for which we search _version_ 83. This file can then be used as the input file for process\_cartons by copying it to the './files/custom/' folder and using
_origin_='custom' and _inputname_='Cartons\_sample\_Versions\_single\_and\_forced.txt'. The name assigned in these cases is 'Cartons\_' followed by 'all' or 'sample' depending on whether we are
searching all carton names or not, then '_Versions_' followed by the value of _versions_ or the value of _unique\_version_ if _version_='single', finally a suffix '_and\_forced' is added if the
_forced\_versions_ dictionary was used.

```
[INFO]: ############################################################
[INFO]: ###               STARTING CODE EXECUTION                ###
[INFO]: ############################################################
[INFO]: Ran process_cartons using the following arguments
[INFO]: origin=targetdb
[INFO]: files_folder=./files/
[INFO]: inputname=None
[INFO]: delim=|
[INFO]: check_exists=False
[INFO]: verb=True
[INFO]: return_objects=False
[INFO]: write_input=True
[INFO]: write_output=False
[INFO]: assign_sets=False
[INFO]: assign_placeholders=False
[INFO]: visualize=False
[INFO]: overwrite=True
[INFO]: all_cartons=False
[INFO]: cartons_name_pattern=bhm_rm*
[INFO]: versions=single
[INFO]: forced_versions={'bhm_rm_core': 83}
[INFO]: unique_version=49
[INFO]:  
[INFO]: Wrote file ./files/targetdb/Cartons_sample_Versions_single_and_forced.txt
```

### 2 Check the existence in targetdb of all the cartons in a custom list or an rsconfig file

To do this you have to use _check\_exists_=True _origin_= 'rsconfig' or 'custom' and you have to provide the inputname of the file to read which has to be in the folder './files/\{origin\}'.
