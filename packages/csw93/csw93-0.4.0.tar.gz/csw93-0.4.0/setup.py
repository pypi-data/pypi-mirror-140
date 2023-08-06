# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['csw93', 'csw93.data']

package_data = \
{'': ['*'], 'csw93.data': ['raw_data/*']}

install_requires = \
['graphviz>=0.19.1,<0.20.0',
 'm2r2>=0.3.2,<0.4.0',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.0,<2.0.0']

setup_kwargs = {
    'name': 'csw93',
    'version': '0.4.0',
    'description': 'Regular Fractional Factorial two-level designs from the paper of Chen, Sun and Wu (1993)',
    'long_description': '# csw93 - Chen, Sun and Wu (1993)\n[![PyPI](https://img.shields.io/pypi/v/csw93)](https://pypi.org/project/csw93/)\n[![Documentation Status](https://readthedocs.org/projects/csw93/badge/?version=latest)](https://csw93.readthedocs.io/en/latest/?badge=latest)\n[![Build Status](https://app.travis-ci.com/ABohynDOE/csw93.svg?branch=main)](https://app.travis-ci.com/ABohynDOE/csw93)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Coverage Status](https://coveralls.io/repos/github/ABohynDOE/csw93/badge.svg?branch=main)](https://coveralls.io/github/ABohynDOE/csw93?branch=main)\n\nCSW93 is a Python package that makes availalble the design matrices of all regular fractional factorial two-level designs from the 1993 paper of Chen, Sun and Wu: ["A catalogue of two-level and three-level fractional factorial designs with small runs"][1].\nFor more information about the package and its functions, see the [documentation](https://csw93.readthedocs.io/en/latest/).\n\n[1]: <https://www.jstor.org/stable/1403599>\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install csw93.\n\n```bash\npip install csw93\n```\n\n## Usage\n\nThe pakage provides three functions to get\n\n- The design matrix,\n- The word length pattern,\n- The number of clear two-factor interactions,\n\nusing only the number of runs and the index of the design.\nThis index corresponds to the first column in all tables of all tables from the paper.\n\n```python\nimport csw93\n\n# Design matrix of the 16-run design with index 8-4.1\ncsw93.get_design(16, "8-4.1")\n\n# Word length pattern of the 32-run design with index 15-10.2\ncsw93.get_wlp(32, "8-4.1")\n\n# Number of clear two-factor interactions for the 64-run design 11-5.10\ncsw93.get_cfi(64, "11-5.10")\n```\n\n## Contributing\n\n### Code style\n\nTry to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. \nA useful tool for automated formatting is [black](https://black.readthedocs.io/en/stable/index.html).\n\n### Submitting code\n\nIf you would like to contribute, please submit a pull request.\nSee the [Github Hello World](https://guides.github.com/activities/hello-world/) example, if you are new to Github.\nFor major changes, please open an issue first to discuss what you would like to change.\nBy contributing to the repository you state you own the copyright to those contributions and agree to include your contributions as part of this project under the MIT license.\n\n### Testing\n\nIf you contribute, please make sure to update the tests aproprietly.\nContinuous integration is performed on [Travis-CI](https://app.travis-ci.com/github/ABohynDOE/csw93).\nTo perform tests run [`pytest`](https://docs.pytest.org/en/latest/).\nTo obtain a [coverage](https://coverage.readthedocs.io) report in html, run\n```\n$ coverage run -m pytest .\n$ coverage html\n```\n\n### Contact\n\nFor further information please contact Alexandre Bohyn, alexandre.bohyn at kuleuven.be\n\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)\n\n## Roadmap\n\nList of the changes that will be implemented later on:\n\n- Write detailled documentation for readthedocs\n\n## Changelog\n\n- 0.4: fix wrong column numbers and added Xu 2009 to the database (not available as \n  function yet)\n- 0.3: Integration to readthedocs.io\n- 0.2: Correct WLP\n- 0.1: initial version\n',
    'author': 'Alexandre Bohyn',
    'author_email': 'alexandre.bohyn@kuleuven.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://abohyndoe.github.io/csw93/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
