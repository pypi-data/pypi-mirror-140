# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['driva_python_sdk', 'driva_python_sdk.core', 'driva_python_sdk.messages']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'kafka-python>=2.0.2,<3.0.0',
 'pydantic-avro>=0.2.4,<0.4.0',
 'pydantic[dotenv]>=1.9.0,<2.0.0',
 'python-schema-registry-client>=2.2.2,<3.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['driva-python-sdk = driva_python_sdk.__main__:main']}

setup_kwargs = {
    'name': 'driva-python-sdk',
    'version': '0.3.1',
    'description': 'Driva Python Sdk',
    'long_description': "Driva Python Sdk\n================\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/driva-python-sdk.svg\n   :target: https://pypi.org/project/driva-python-sdk/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/driva-python-sdk.svg\n   :target: https://pypi.org/project/driva-python-sdk/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/driva-python-sdk\n   :target: https://pypi.org/project/driva-python-sdk\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/driva-python-sdk\n   :target: https://opensource.org/licenses/GPL-3.0\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/driva-python-sdk/latest.svg?label=Read%20the%20Docs\n   :target: https://driva-python-sdk.readthedocs.io/\n   :alt: Read the documentation at https://driva-python-sdk.readthedocs.io/\n.. |Tests| image:: https://github.com/victordriva/driva-python-sdk/workflows/Tests/badge.svg\n   :target: https://github.com/victordriva/driva-python-sdk/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/victordriva/driva-python-sdk/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/victordriva/driva-python-sdk\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* TODO\n\n\nRequirements\n------------\n\n* TODO\n\n\nInstallation\n------------\n\nYou can install *Driva Python Sdk* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install driva-python-sdk\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `GPL 3.0 license`_,\n*Driva Python Sdk* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _GPL 3.0 license: https://opensource.org/licenses/GPL-3.0\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/victordriva/driva-python-sdk/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://driva-python-sdk.readthedocs.io/en/latest/usage.html\n",
    'author': 'Victor Hugo',
    'author_email': 'victor@datadriva.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/victordriva/driva-python-sdk',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
