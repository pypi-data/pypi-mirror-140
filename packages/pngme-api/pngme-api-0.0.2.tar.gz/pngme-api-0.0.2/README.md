<p align="center">
  <img src="./docs/logo.png" alt="Pngme" width="100" height="100">
</p>

<h3 align="center">Python API Client</h3>


<p align="center">
  <a href="https://github.com/pngme/pngme-api/actions">
    <img src="https://github.com/pngme/pngme-api/actions/workflows/test.yaml/badge.svg" alt="CI status" />
  </a>
</p>

This packages a synchronous and asynchronous client used to interact with Pngme's financial data APIs.

## Install

Install the latest version with:

```bash
pip3 install pngme-api
```

## Development environment

We use [Poetry] to build, package, and publish this project. You'll need to [install Poetry](https://python-poetry.org/docs/#installation) to use the development tools.

Clone this repo and install the development dependencies:

```bash
make install
```

> You may need to configure your IDE to point to the newly created virtual environment after running install.

This will create a virtual environment in the `.venv` directory, which is the convention Pipenv and poetry both use for in-project virtual environments.

You can type `make help` to see a list of other options, which aren't strictly necessary as part of our day-to-day development practices.

### Integration tests

You can replicate the integration tests (which run in a GitHub action on every push) locally:

```bash
make ci
```

## Dependencies

Production dependencies are listed in [setup.cfg](./setup.cfg) under `options.install_requires`, see [`setuptools` dependency management](https://setuptools.pypa.io/en/latest/userguide/quickstart.html#dependency-management).

Development dependencies are listed in [requirements.txt](./requirements.txt).

Running `make install` will install **both** production and development dependencies. Running `pip install .` (where `.` is the path to the directory containing [pyproject.toml](./pyproject.toml)) will install only the production dependencies.
