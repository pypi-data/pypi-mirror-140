# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jmapc', 'jmapc.methods', 'jmapc.models']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json>=0.5.6,<0.6.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'jmapc',
    'version': '0.0.2',
    'description': 'A JMAP client library for Python. https://jmap.io',
    'long_description': '# A [JMAP][jmapio] client library for Python\n\njmapc is in initial development.\n\nCurrently implemented:\n\n* Basic models\n* Request methods:\n  * `Core/echo`\n  * `Email/get`\n  * `Email/query`\n  * `Identity/get`\n  * `Thread/get`\n  * `Mailbox/get`\n  * `Mailbox/query`\n* Combined requests with support for result references\n* Basic JMAP method response error handling\n* Unit tests for basic functionality and methods\n\nTodo list:\n\n* Implement `EmailSubmission` methods for sending email\n* Write documentation\n\n## Examples\n\nFirst, run `poetry install` to set up your local repository.\n\n[Any of the examples](/examples) can be invoked with `poetry run`:\n\n```sh\nJMAP_HOST=jmap.example.com \\\nJMAP_USER=ness \\\nJMAP_PASSWORD=pk_fire \\\npoetry run examples/identity_get.py\n```\n\nIf successful, `examples/identity_get.py` should output something like:\n\n```\nIdentity 12345 is for Ness at ness@onett.example.com\nIdentity 67890 is for Ness at ness-alternate@onett.example.com\n```\n\n## Development\n\nPrerequisites: [Poetry][poetry]\n\n* Setup: `poetry install`\n* Run all tests: `poetry run poe test`\n* Fix linting errors: `poetry run poe lint`\n\n---\n\nCreated from [smkent/cookie-python][cookie-python] using\n[cookiecutter][cookiecutter]\n\n[cookie-python]: https://github.com/smkent/cookie-python\n[cookiecutter]: https://github.com/cookiecutter/cookiecutter\n[jmapio]: https://jmap.io\n[poetry]: https://python-poetry.org/docs/#installation\n',
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
