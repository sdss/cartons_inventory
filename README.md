# cartons_inventory

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/cartons_inventory/badge/?version=latest)](https://cartons_inventory.readthedocs.io/en/latest/?badge=latest)

### Cartons\_inventory is package to track the content of SDSS cartons in targetdb database.

It can take as an input an rsconfig file, a curstom file or a targetdb selection criteria.

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
