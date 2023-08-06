# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['artefacts']

package_data = \
{'': ['*']}

install_requires = \
['packaging>=21.3,<22.0', 'pydantic>=1.9.0,<2.0.0', 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'artefacts',
    'version': '1.2.0',
    'description': 'Deserialization for dbt artifacts',
    'long_description': '# artefacts\n\n[![PyPI version](https://badge.fury.io/py/artefacts.svg)](https://badge.fury.io/py/artefacts) ![badge](https://img.shields.io/badge/dbt-%3E%3D1.0-orange?style=flat&logo=dbt) ![badge](https://img.shields.io/pypi/pyversions/artefacts?logo=python) \n\n![badge](https://img.shields.io/github/workflow/status/tjwaterman99/artefacts/CI/main?label=CI) [![Coverage Status](https://coveralls.io/repos/github/tjwaterman99/artefacts/badge.svg?branch=main)](https://coveralls.io/github/tjwaterman99/artefacts?branch=main)\n\n_A deserialization library for dbt artifacts._\n\n```\npip install artefacts\n```\n\nThe `artefacts.api` module aims to provide simple, easy to use python objects for interacting with your dbt project. Here\'s an example that identifies models in your project that are missing tests or descriptions.\n\n```py\n>>> import artefacts.api\n>>> for model in artefacts.api.models():\n...     if model.description is None or len(model.tests) == 0:\n...         print(f"Incomplete model: {model.name}")\n\n```\n\n### Usage\n\nAfter installing artefacts, you first need to _compile_ your dbt project.\n\n```\ndbt compile\n```\n\nYou can then start using the api.\n\n```py\n>>> import artefacts.api\n```\n\n### Docs\n\nDocumentation for the project is available on the Github Pages site.\n\n> https://tjwaterman99.github.io/artefacts/\n\nAll methods exposed by the api are documented with usage examples in the API section.\n\n> https://tjwaterman99.github.io/artefacts/api.html\n\nReferences for the objects returned by the api are available in the References section.\n\n> https://tjwaterman99.github.io/artefacts/reference.html\n\n### Development Setup\n\nOpen this repository in a Github Codespace. (Click the green `Code` button in the repository\'s [Github page](https://github.com/tjwaterman99/artefacts) and select `New Codespace`).\n\n#### Testing\n\n```\npoetry run pytest\n```\n\nBy default, pytest will test against the dbt project located at `ARTEFACTS_DBT_PROJECT_DIR`. To test against a different dbt project, update that environment variable and build the project.\n\n```\nexport ARTEFACTS_DBT_PROJECT_DIR=$PWD/dbt_projects/dbt-starter-project\npoetry run dbt build --project-dir $ARTEFACTS_DBT_PROJECT_DIR\npoetry run pytest\n```\n\nTo run the doctests use the `--doctest-modules` flag. Note that the doctests are intended to pass only when using the [`poffertjes_shop`](https://github.com/tjwaterman99/poffertjes_shop) project.\n\n```\npoetry run pytest --doctest-modules\n```\n\n#### Documentation site\n\nUse `sphinx-livereload` to run the docs site on port `8000`.\n\n```\npoetry run sphinx-autobuild docs/ docs/_build --watch artefacts\n```\n',
    'author': 'Tom Waterman',
    'author_email': 'tjwaterman99@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
