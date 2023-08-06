# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jmapc', 'jmapc.types', 'jmapc.types.jmap']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json>=0.5.6,<0.6.0', 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'jmapc',
    'version': '0.0.0',
    'description': 'A JMAP client library for Python. https://jmap.io',
    'long_description': '# jmapc\n\nA [JMAP][jmapio] client library for Python\n\n## Development\n\nPrerequisites: [Poetry][poetry]\n\n* Setup: `poetry install`\n* Test template rendering and run rendered project tests: `poetry run poe test`\n* Fix linting errors: `poetry run poe lint`\n\n[jmapio]: https://jmap.io\n[poetry]: https://python-poetry.org/docs/#installation\n',
    'author': 'Stephen Kent',
    'author_email': 'smkent@smkent.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
