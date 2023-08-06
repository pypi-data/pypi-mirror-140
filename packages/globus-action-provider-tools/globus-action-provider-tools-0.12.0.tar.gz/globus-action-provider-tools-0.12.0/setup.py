# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['globus_action_provider_tools',
 'globus_action_provider_tools.flask',
 'globus_action_provider_tools.testing']

package_data = \
{'': ['*']}

install_requires = \
['cachetools>=4.2.4,<5.0.0',
 'globus-sdk>=3.3.0,<4.0.0',
 'isodate>=0.6.0,<0.7.0',
 'jsonschema>=3,<4',
 'pybase62>=0.4.0,<0.5.0',
 'pydantic>=1.7.3,<2.0.0',
 'pyyaml>=5.3.1,<6.0.0']

extras_require = \
{'flask': ['flask>=1,<2']}

entry_points = \
{'console_scripts': ['whattimeisit-provider = '
                     'examples.flask.whattimeisitrightnow.app.app:main']}

setup_kwargs = {
    'name': 'globus-action-provider-tools',
    'version': '0.12.0',
    'description': 'Tools to help developers build services that implement the Action Provider specification.',
    'long_description': 'Action Provider Tools Introduction\n==================================\n\n.. image:: https://github.com/globus/action-provider-tools/workflows/Action%20Provider%20Tools%20CI/badge.svg\n   :target: https://github.com/globus/action-provider-tools/workflows/Action%20Provider%20Tools%20CI/badge.svg\n   :alt: CI Status\n\n.. image:: https://readthedocs.org/projects/action-provider-tools/badge/?version=latest\n   :target: https://action-provider-tools.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n\n.. image:: https://badge.fury.io/py/globus-action-provider-tools.svg\n    :target: https://badge.fury.io/py/globus-action-provider-tools\n    :alt: PyPi Package\n\n.. image:: https://img.shields.io/pypi/pyversions/globus-action-provider-tools\n    :target: https://pypi.org/project/globus-action-provider-tools/\n    :alt: Compatible Python Versions\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/globus/action-provider-tools/workflows/Action%20Provider%20Tools%20CI/badge.svg\n    :alt: Code Style\n\nThis is an experimental toolkit to help developers build Action Providers for\nuse in Globus Automate including for invocation via Globus Flows.\n\nAs this is experimental, no support is implied or provided for any sort of use\nof this package. It is published for ease of distribution among those planning\nto use it for its intended, experimental, purpose.\n\nBasic Usage\n-----------\n\nInstall the base toolkit with ``pip install globus_action_provider_tools``\n\nYou can then import the toolkit\'s standalone components from\n``globus_action_provider_tools``. This is useful in instances where you want to\nuse pieces of the library to perform a function (such as token validation via\nthe TokenChecker or API schema validation via the ActionStatus or ActionRequest)\nand plug into other web frameworks.\n\n\n.. code-block:: python\n\n    from flask import Flask\n    from globus_action_provider_tools import ActionProviderDescription\n\n    description = ActionProviderDescription(              \n        globus_auth_scope="https://auth.globus.org/scopes/00000000-0000-0000-0000-000000000000/action_all",\n        title="My Action Provider",\n        admin_contact="support@example.org",\n        synchronous=True,\n        input_schema={\n            "$id": "whattimeisitnow.provider.input.schema.json",\n            "$schema": "http://json-schema.org/draft-07/schema#",\n            "title": "Exmaple Action Provider",\n            "type": "object",\n            "properties": {"message": {"type": "string"}},\n            "required": ["message"],\n            "additionalProperties": False,\n        },\n        api_version="1.0",\n        subtitle="Just an example",\n        description="",\n        keywords=["example", "testing"],\n        visible_to=["public"],\n        runnable_by=["all_authenticated_users"],\n        administered_by=["support@example.org"],\n    )\n\nTo install the Flask helpers as well for use specifically in developing Flask\nbased Action Providers, install this library using ``pip install\nglobus_action_provider_tools[flask]``\n\nReporting Issues\n----------------\n\nIf you\'re experiencing a problem using globus_action_provider_tools, or have an\nidea for how to improve the toolkit, please open an issue in the repository and\nshare your feedback.\n\nTesting, Development, and Contributing\n--------------------------------------\n\nWelcome and thank you for taking the time to contribute! \n\nThe ``globus_action_provider_tools`` package is developed using poetry so to get\nstarted you\'ll need to install `poetry <https://python-poetry.org/>`_. Once\ninstalled, clone the repository and run ``make install`` to install the package\nand its dependencies locally in a virtual environment (typically ``.venv``).\n\nAnd that\'s it, you\'re ready to dive in and make code changes. Once you\'re\nsatisfied with your changes, be sure to run ``make autoformat`` to run the\nproject\'s autoformatters on your changes and ``make test`` to validate there\nare no breaking changes introduced. Both these steps must be run for us to\naccept incoming changes. Once you feel your work is ready to be submitted, feel\nfree to create a PR.\n\nPyPi Releases\n-------------\n\nPlease follow the steps below when creating a new release of the toolkit:\n\n- Create a new release branch\n    - git checkout -b release/X.Y.Z\n- Update the project\'s dependencies\n    - poetry update\n- Update the project version (follow semantic versioning) in pyproject.toml\n    - poetry version patch|minor|major\n- Update the project version in `globus_action_provider_tools/__init__.py`\n- Create a pull request into the main branch, wait for CI tests to complete\n- Merge the passing pull request\n- Create and publish a git tag for the new release\n    - git tag v$(poetry version -s)\n    - git push --tags\n- Create a new GH release that references the recently created tag. Provide\n  release notes with information on the changeset. Once the release is created,\n  there\'s a GH workflow that will build the toolkit and publish it to pypi. \n\nLinks\n-----\n| Full Documentation: https://action-provider-tools.readthedocs.io\n| Rendered Redoc: https://globus.github.io/action-provider-tools/\n| Source Code: https://github.com/globus/action-provider-tools\n| Release History + Changelog: https://github.com/globus/action-provider-tools/releases\n',
    'author': 'Kurt McKee',
    'author_email': 'kurt@globus.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
