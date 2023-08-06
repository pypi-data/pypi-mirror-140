# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['track_viz']

package_data = \
{'': ['*'], 'track_viz': ['static/*', 'templates/*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'altair>=4.2.0,<5.0.0',
 'click>=8.0.1,<9.0.0',
 'defusedxml>=0.7.1,<0.8.0',
 'geopy>=2.2.0,<3.0.0',
 'lxml>=4.6.4,<5.0.0',
 'matplotlib>=3.5.0,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'poetry>=1.1.12,<2.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'seaborn>=0.11.2,<0.12.0']

entry_points = \
{'console_scripts': ['track-viz = track_viz.__main__:main']}

setup_kwargs = {
    'name': 'track-viz',
    'version': '0.3.0',
    'description': 'Visualize Tracking Data',
    'long_description': "Track Visualization\n===================\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/track-viz.svg\n   :target: https://pypi.org/project/track-viz/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/track-viz.svg\n   :target: https://pypi.org/project/track-viz/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/track-viz\n   :target: https://pypi.org/project/track-viz\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/track-viz\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/track-viz/latest.svg?label=Read%20the%20Docs\n   :target: https://track-viz.readthedocs.io/\n   :alt: Read the documentation at https://track-viz.readthedocs.io/\n.. |Tests| image:: https://github.com/JulienMBABD/track-viz/workflows/Tests/badge.svg\n   :target: https://github.com/JulienMBABD/track-viz/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/JulienMBABD/track-viz/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/JulienMBABD/track-viz\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* TODO\n\n\nRequirements\n------------\n\n* TODO\n\n\nInstallation\n------------\n\nYou can install *Football Track* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install track-viz\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*Football Track* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/JulienMBABD/track-viz/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://track-viz.readthedocs.io/en/latest/usage.html\n",
    'author': 'Julien Rossi',
    'author_email': 'mr.julien.rossi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JulienMBABD/track-viz',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
