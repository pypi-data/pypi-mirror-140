# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['viewdom']

package_data = \
{'': ['*']}

install_requires = \
['MarkupSafe>=2.0.1,<3.0.0',
 'hopscotch>=0.1.2,<0.3.0',
 'htm>=0.1.1,<0.2.0',
 'tagged>=0.0.2,<0.0.3',
 'venusian>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'viewdom',
    'version': '0.6.2',
    'description': 'ViewDOM',
    'long_description': "# ViewDOM: Component-Driven Development for Python\n\n[![Coverage Status][codecov-badge]][codecov-link]\n[![Documentation Status][rtd-badge]][rtd-link]\n[![Code style: black][black-badge]][black-link]\n[![PyPI][pypi-badge]][pypi-link]\n[![Python Version][pypi-badge]][pypi-link]\n[![PyPI - Downloads][install-badge]][install-link]\n[![License][license-badge]][license-link]\n[![Test Status][tests-badge]][tests-link]\n[![pre-commit][pre-commit-badge]][pre-commit-link]\n[![black][black-badge]][black-link]\n\n[codecov-badge]: https://codecov.io/gh/pauleveritt/viewdom/branch/main/graph/badge.svg\n[codecov-link]: https://codecov.io/gh/pauleveritt/viewdom\n[rtd-badge]: https://readthedocs.org/projects/viewdom/badge/?version=latest\n[rtd-link]: https://viewdom.readthedocs.io/en/latest/?badge=latest\n[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg\n[black-link]: https://github.com/ambv/black\n[pypi-badge]: https://img.shields.io/pypi/v/viewdom.svg\n[pypi-link]: https://pypi.org/project/viewdom\n[install-badge]: https://img.shields.io/pypi/dw/viewdom?label=pypi%20installs\n[install-link]: https://pypistats.org/packages/viewdom\n[license-badge]: https://img.shields.io/pypi/l/viewdom\n[license-link]: https://opensource.org/licenses/MIT\n[tests-badge]: https://github.com/pauleveritt/viewdom/workflows/Tests/badge.svg\n[tests-link]: https://github.com/pauleveritt/viewdom/actions?workflow=Tests\n[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n[pre-commit-link]: https://github.com/pre-commit/pre-commit\n\nViewDOM brings modern frontend templating patterns to Python:\n\n- [tagged](https://github.com/jviide/tagged) to have language-centered templating (like JS tagged templates)\n- [htm](https://github.com/jviide/htm.py) to generate virtual DOM structures from a template run (like the `htm` JS package)\n- ViewDOM for components which render a VDOM to a markup string, along with other modern machinery\n- Optionally, [Hopscotch](https://github.com/pauleveritt/hopscotch) for a component registry with dependency injection\n\n## Features\n\n- Component-driven development.\n- Intermediate VDOM.\n- Pass in data either via props (simple) or DI (rich).\n- Emphasis on modern Python dev practices: explicit, type hinting,\n  static analysis, testing, docs, linting, editors.\n\n## Requirements\n\n- Python 3.9+.\n- viewdom\n- tagged\n- htm.py\n- Markupsafe\n\n## Installation\n\nYou can install ViewDOM via [pip](https://pip.pypa.io/) from [PyPI](https://pypi.org/):\n\n```shell\n$ pip install viewdom\n```\n\n## Quick Examples\n\n# Contributing\n\nContributions are very welcome.\nTo learn more, see the [contributor's guide](contributing).\n\n# License\n\nDistributed under the terms of the [MIT license](https://opensource.org/licenses/MIT), ViewDOM is free and open source software.\n\n# Issues\n\nIf you encounter any problems,\nplease [file an issue](https://github.com/pauleveritt/viewdom/issues) along with a detailed description.\n\n# Credits\n\nThis project was generated from [@cjolowicz's](https://github.com/cjolowicz) [Hypermodern Python Cookiecutter](https://github.com/cjolowicz/cookiecutter-hypermodern-python) template.\n",
    'author': 'Paul Everitt',
    'author_email': 'pauleveritt@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pauleveritt/viewdom',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.1,<4.0.0',
}


setup(**setup_kwargs)
