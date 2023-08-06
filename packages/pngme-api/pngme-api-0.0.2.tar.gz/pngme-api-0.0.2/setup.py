# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['api', 'api.resources']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.22.0,<0.23.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pngme-api',
    'version': '0.0.2',
    'description': "API client used to access Pngme's financial data APIs.",
    'long_description': '<p align="center">\n  <img src="./docs/logo.png" alt="Pngme" width="100" height="100">\n</p>\n\n<h3 align="center">Python API Client</h3>\n\n\n<p align="center">\n  <a href="https://github.com/pngme/pngme-api/actions">\n    <img src="https://github.com/pngme/pngme-api/actions/workflows/test.yaml/badge.svg" alt="CI status" />\n  </a>\n</p>\n\nThis packages a synchronous and asynchronous client used to interact with Pngme\'s financial data APIs.\n\n## Install\n\nInstall the latest version with:\n\n```bash\npip3 install pngme-api\n```\n\n## Development environment\n\nWe use [Poetry] to build, package, and publish this project. You\'ll need to [install Poetry](https://python-poetry.org/docs/#installation) to use the development tools.\n\nClone this repo and install the development dependencies:\n\n```bash\nmake install\n```\n\n> You may need to configure your IDE to point to the newly created virtual environment after running install.\n\nThis will create a virtual environment in the `.venv` directory, which is the convention Pipenv and poetry both use for in-project virtual environments.\n\nYou can type `make help` to see a list of other options, which aren\'t strictly necessary as part of our day-to-day development practices.\n\n### Integration tests\n\nYou can replicate the integration tests (which run in a GitHub action on every push) locally:\n\n```bash\nmake ci\n```\n\n## Dependencies\n\nProduction dependencies are listed in [setup.cfg](./setup.cfg) under `options.install_requires`, see [`setuptools` dependency management](https://setuptools.pypa.io/en/latest/userguide/quickstart.html#dependency-management).\n\nDevelopment dependencies are listed in [requirements.txt](./requirements.txt).\n\nRunning `make install` will install **both** production and development dependencies. Running `pip install .` (where `.` is the path to the directory containing [pyproject.toml](./pyproject.toml)) will install only the production dependencies.\n',
    'author': 'Ben Fasoli',
    'author_email': 'ben@pngme.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://developers.api.pngme.com/reference/getting-started-with-your-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
