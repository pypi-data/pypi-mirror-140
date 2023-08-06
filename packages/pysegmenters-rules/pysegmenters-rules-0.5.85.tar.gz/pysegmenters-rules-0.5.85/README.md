# pysegmenters_rules

[![license](https://img.shields.io/github/license/oterrier/pysegmenters_rules)](https://github.com/oterrier/pysegmenters_rules/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pysegmenters_rules/workflows/tests/badge.svg)](https://github.com/oterrier/pysegmenters_rules/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pysegmenters_rules)](https://codecov.io/gh/oterrier/pysegmenters_rules)
[![docs](https://img.shields.io/readthedocs/pysegmenters_rules)](https://pysegmenters_rules.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pysegmenters_rules)](https://pypi.org/project/pysegmenters_rules/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysegmenters_rules)](https://pypi.org/project/pysegmenters_rules/)

Rule based segmenter based on Spacy

## Installation

You can simply `pip install pysegmenters_rules`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pysegmenters_rules
```

### Running the test suite

You can run the full test suite against all supported versions of Python (3.8) with:

```
tox
```

### Building the documentation

You can build the HTML documentation with:

```
tox -e docs
```

The built documentation is available at `docs/_build/index.html.
