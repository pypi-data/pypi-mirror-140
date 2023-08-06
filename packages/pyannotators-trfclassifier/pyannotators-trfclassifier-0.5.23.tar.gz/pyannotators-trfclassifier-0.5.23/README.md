# pyannotators_trfclassifier

[![license](https://img.shields.io/github/license/oterrier/pyannotators_trfclassifier)](https://github.com/oterrier/pyannotators_trfclassifier/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyannotators_trfclassifier/workflows/tests/badge.svg)](https://github.com/oterrier/pyannotators_trfclassifier/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyannotators_trfclassifier)](https://codecov.io/gh/oterrier/pyannotators_trfclassifier)
[![docs](https://img.shields.io/readthedocs/pyannotators_trfclassifier)](https://pyannotators_trfclassifier.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyannotators_trfclassifier)](https://pypi.org/project/pyannotators_trfclassifier/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyannotators_trfclassifier)](https://pypi.org/project/pyannotators_trfclassifier/)

Classifier based on Huggingface Text Classification pipeline

## Installation

You can simply `pip install pyannotators_trfclassifier`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyannotators_trfclassifier
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
