<p align="center">
  <img src="./docs/logo.png" alt="Pngme" width="100" height="100">
</p>

<h3 align="center">Python API Client</h3>

This package exposes a synchronous and asynchronous client used to interact with Pngme's financial data APIs.

## Install

Install the latest version with:

```bash
pip3 install pngme-api
```

## Quick start

Create a `Client` instance using your API `token` found in the [Pngme Dashboard](https://admin.pngme.com):

```python
from pngme.api import Client

token = "" # your API token
client = Client(token)
```

> If you're using [`asyncio`](https://docs.python.org/3/library/asyncio.html), you can import and use the `AsyncClient` instead.

We can list or search the available [`/users`](https://developers.api.pngme.com/reference/get_users-1):

```python
users = client.users.get()
users = client.users.get(search="2343456789012")
```

For a user of interest, we can get a list of the user's [`/accounts`](https://developers.api.pngme.com/reference/get_users-user-uuid-accounts-1):

```python
user_uuid = "33b6215d-3d75-4271-801c-6da27603a8be"

accounts = client.accounts.get(user_uuid=user_uuid)
```

Then for a given account, we can get a list of the user's [`/transactions`](https://developers.api.pngme.com/reference/get_users-user-uuid-accounts-acct-uuid-transactions-1), [`/balances`](https://developers.api.pngme.com/reference/get_users-user-uuid-accounts-acct-uuid-balances-1), or [`/alerts`](https://developers.api.pngme.com/reference/get_users-user-uuid-accounts-acct-uuid-alerts-1):

```python
user_uuid = "33b6215d-3d75-4271-801c-6da27603a8be"
account_uuid = "zenithbank"

transactions = client.transactions.get(user_uuid=user_uuid, account_uuid=account_uuid)
balances = client.balances.get(user_uuid=user_uuid, account_uuid=account_uuid)
alerts = client.alerts.get(user_uuid=user_uuid, account_uuid=account_uuid)
```

## Development environment

We use [Poetry](https://python-poetry.org) to build, package, and publish this project. You'll need to [install Poetry](https://python-poetry.org/docs/#installation) to use the development tools.

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

### Dependencies

Production dependencies are listed in [setup.cfg](./setup.cfg) under `options.install_requires`, see [`setuptools` dependency management](https://setuptools.pypa.io/en/latest/userguide/quickstart.html#dependency-management).

Development dependencies are listed in [requirements.txt](./requirements.txt).

Running `make install` will install **both** production and development dependencies. Running `pip install .` (where `.` is the path to the directory containing [pyproject.toml](./pyproject.toml)) will install only the production dependencies.
