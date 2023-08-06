# Simples Steps for PyDaisi SDK

## Preliminary Steps

Install with PIP:

- `pip install pydaisi`

Create your personal access token:

- https://app.daisi.io/settings/personal-access-tokens

## Using PyDaisi

Set your Personal Access Token:

- `import os`
- `os.environ["ACCESS_TOKEN"] = "6U6QVkBI3NOXgS1MElXn8ufK6ZglBY8B"`

Import the Daisi Class:

- `from pydaisi import Daisi`

Connect to a Daisi:

- `daisi = Daisi("Titanic")`

Check the schema of a Daisi:

- `daisi.schema()`

Compute a Daisi:

- `daisi.compute(func="raw", rows=5)`
