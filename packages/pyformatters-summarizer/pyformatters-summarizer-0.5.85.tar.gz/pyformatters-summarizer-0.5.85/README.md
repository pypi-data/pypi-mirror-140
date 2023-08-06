# pyformatters_summarizer

[![license](https://img.shields.io/github/license/oterrier/pyformatters_summarizer)](https://github.com/oterrier/pyformatters_summarizer/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyformatters_summarizer/workflows/tests/badge.svg)](https://github.com/oterrier/pyformatters_summarizer/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyformatters_summarizer)](https://codecov.io/gh/oterrier/pyformatters_summarizer)
[![docs](https://img.shields.io/readthedocs/pyformatters_summarizer)](https://pyformatters_summarizer.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyformatters_summarizer)](https://pypi.org/project/pyformatters_summarizer/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyformatters_summarizer)](https://pypi.org/project/pyformatters_summarizer/)

Formatter based on Facebook's Summarizer

## Installation

You can simply `pip install pyformatters_summarizer`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyformatters_summarizer
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
