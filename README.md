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

# 1 Creating an input file from a targetdb selection criteria

To do this you have to use _origin_ ='targetdb', and _write\_input = True. Then you have to make sure the file with the output name doesnt exist or that _overwrite_=True
Then you define a selection criteria with the arguments of _versions_, _forced\_versions_, _all\_cartons_, and _carton\_name\_pattern_.

_all\_cartons_ = True means that we will search for all carton names while _all\_cartons_=False means that only cartons with a name matching _carton\_name\_pattern_ will be searched
