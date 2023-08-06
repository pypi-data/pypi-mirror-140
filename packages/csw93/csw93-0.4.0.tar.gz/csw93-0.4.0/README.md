# csw93 - Chen, Sun and Wu (1993)
[![PyPI](https://img.shields.io/pypi/v/csw93)](https://pypi.org/project/csw93/)
[![Documentation Status](https://readthedocs.org/projects/csw93/badge/?version=latest)](https://csw93.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://app.travis-ci.com/ABohynDOE/csw93.svg?branch=main)](https://app.travis-ci.com/ABohynDOE/csw93)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Coverage Status](https://coveralls.io/repos/github/ABohynDOE/csw93/badge.svg?branch=main)](https://coveralls.io/github/ABohynDOE/csw93?branch=main)

CSW93 is a Python package that makes availalble the design matrices of all regular fractional factorial two-level designs from the 1993 paper of Chen, Sun and Wu: ["A catalogue of two-level and three-level fractional factorial designs with small runs"][1].
For more information about the package and its functions, see the [documentation](https://csw93.readthedocs.io/en/latest/).

[1]: <https://www.jstor.org/stable/1403599>

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install csw93.

```bash
pip install csw93
```

## Usage

The pakage provides three functions to get

- The design matrix,
- The word length pattern,
- The number of clear two-factor interactions,

using only the number of runs and the index of the design.
This index corresponds to the first column in all tables of all tables from the paper.

```python
import csw93

# Design matrix of the 16-run design with index 8-4.1
csw93.get_design(16, "8-4.1")

# Word length pattern of the 32-run design with index 15-10.2
csw93.get_wlp(32, "8-4.1")

# Number of clear two-factor interactions for the 64-run design 11-5.10
csw93.get_cfi(64, "11-5.10")
```

## Contributing

### Code style

Try to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. 
A useful tool for automated formatting is [black](https://black.readthedocs.io/en/stable/index.html).

### Submitting code

If you would like to contribute, please submit a pull request.
See the [Github Hello World](https://guides.github.com/activities/hello-world/) example, if you are new to Github.
For major changes, please open an issue first to discuss what you would like to change.
By contributing to the repository you state you own the copyright to those contributions and agree to include your contributions as part of this project under the MIT license.

### Testing

If you contribute, please make sure to update the tests aproprietly.
Continuous integration is performed on [Travis-CI](https://app.travis-ci.com/github/ABohynDOE/csw93).
To perform tests run [`pytest`](https://docs.pytest.org/en/latest/).
To obtain a [coverage](https://coverage.readthedocs.io) report in html, run
```
$ coverage run -m pytest .
$ coverage html
```

### Contact

For further information please contact Alexandre Bohyn, alexandre.bohyn at kuleuven.be


## License

[MIT](https://choosealicense.com/licenses/mit/)

## Roadmap

List of the changes that will be implemented later on:

- Write detailled documentation for readthedocs

## Changelog

- 0.4: fix wrong column numbers and added Xu 2009 to the database (not available as 
  function yet)
- 0.3: Integration to readthedocs.io
- 0.2: Correct WLP
- 0.1: initial version
