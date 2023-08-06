# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['yamk']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'tomli>=2.0.0,<3.0.0']

entry_points = \
{'console_scripts': ['yam = yamk.main:main', 'yamk = yamk.main:main']}

setup_kwargs = {
    'name': 'yamk',
    'version': '2.3.0',
    'description': 'Yet another make',
    'long_description': "=====================\nyam: yet another make\n=====================\n\n.. image:: https://github.com/spapanik/yamk/actions/workflows/build.yml/badge.svg\n  :alt: Build\n  :target: https://github.com/spapanik/yamk/actions/workflows/build.yml\n.. image:: https://img.shields.io/lgtm/alerts/g/spapanik/yamk.svg\n  :alt: Total alerts\n  :target: https://lgtm.com/projects/g/spapanik/yamk/alerts/\n.. image:: https://img.shields.io/github/license/spapanik/yamk\n  :alt: License\n  :target: https://github.com/spapanik/yamk/blob/main/LICENSE.txt\n.. image:: https://img.shields.io/pypi/v/yamk\n  :alt: PyPI\n  :target: https://pypi.org/project/yamk\n.. image:: https://pepy.tech/badge/yamk\n  :alt: Downloads\n  :target: https://pepy.tech/project/yamk\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n  :alt: Code style\n  :target: https://github.com/psf/black\n\n``yam`` offers an alternative tool to control the housekeeping tasks of\na project, as well as the creation of executables and non-source files\nfrom source files.\n\nIn a nutshell\n-------------\n\nInstallation\n^^^^^^^^^^^^\n\nThe easiest way is to use pip to install ``yam``.\n\n.. code:: console\n\n   $ pip install --user yamk\n\nPlease make sure that the correct directory is added to your path. This\ndepends on the OS.\n\nUsage\n^^^^^\n\n``yam``'s behaviour is defined in a toml file, called a cookbook. The default name is ``make.toml``,\nbut you can specify a different file if you want. Specifying a name ``<name.toml>`` will also parse all the ``.toml``\nfiles in the directory named ``<name.toml>.d``.\n\n``yam`` can be invoked by using the command ``yam``, which is also\naliased to ``yamk``. ``yam`` follows the GNU recommendations for command\nline interfaces.\n\nLinks\n-----\n\n- `Documentation`_\n- `Changelog`_\n\n\n.. _Changelog: https://github.com/spapanik/yamk/blob/main/CHANGELOG.rst\n.. _Documentation: https://yamk.readthedocs.io/en/latest/\n",
    'author': 'Stephanos Kuma',
    'author_email': 'stephanos@kuma.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/spapanik/yamk',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
