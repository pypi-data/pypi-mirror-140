# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clovars',
 'clovars.IO',
 'clovars.abstract',
 'clovars.bio',
 'clovars.gui',
 'clovars.scientific',
 'clovars.simulation',
 'clovars.simulation.analysis',
 'clovars.simulation.fit',
 'clovars.simulation.run',
 'clovars.simulation.view',
 'clovars.utils',
 'clovars.utils.mixins']

package_data = \
{'': ['*'], 'clovars': ['default_settings/*']}

install_requires = \
['ete3>=3.1.2,<4.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.1,<2.0.0',
 'scipy>=1.8.0,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['clovars = clovars.main:main']}

setup_kwargs = {
    'name': 'clovars',
    'version': '0.2.0',
    'description': 'Clonal Variability Simulation',
    'long_description': '# CloVarS: a clonal variability simulation of single cells\nThis repository contains the source code accompanying the article "CloVarS: a simulation of clonal variability in single cells" (in preparation).\n\n<p align="center" width="100%">\n    <img src="docs/_static/clovars_overview.png" alt="CloVarS basic workflow">\n</p>\n\n## What is CloVarS\nThe **Clo**nal **Var**iability **S**imulation (CloVarS) is a cell culture simulation that generates synthetic single-cell lineage data, as normally obtained from time-lapse microscopy experiments.\n\nThe example below depicts a single colony, starting from a single cell, which grows over 7 days:\n\n<p align="center" width="100%">\n    <img width="80%" src="docs/_static/family_tree_01.gif" alt="Simulation Family Tree">\n</p>\n\n## Installation\nCloVarS requires **Python version 3.8+** in order to run. You can install CloVarS in your Python environment with the command:\n```shell\npip install clovars\n```\nThis adds the `clovars` command to your Python environment, and also installs the necessary [dependencies](#dependencies).\n\n## How to use CloVarS\nCloVarS can be executed in the following modes: \n- `run` - run a simulation with the given settings;\n- `view` - visualize the results of a previous simulation run (figures, images, videos);\n- `analyse` - run analytical tools on the result of a previous simulation run;\n- `fit` - fut experimental data to a variety of curves.\n\nYou also need to provide the necessary **settings files** as command-line arguments. \n\nThese files use the [TOML](https://toml.io/en/) syntax, which makes it easy to open and edit them in any text editor. [This folder](examples) has examples for the structure of the settings files.\n\nBe sure to pay attention: CloVarS will likely **run into errors** if the setting files have **incorrect or missing values!**\n\nFor more information on the settings and their meaning, please [read the docs here](http://www.ufrgs.br/labsinal/clovars/docs).\n\n### Run\n```shell\nclovars run <run-settings-file> <colonies-file>\n```\nwhere: \n- `run-settings-file` is the path for a TOML file with the run settings;\n- `colonies-file` is the path for a TOML file with the colony description.\n\n### View\n```shell\nclovars view <view-settings-file>\n```\nwhere:\n- `view-settings-file` is the path for a TOML file with the view settings.\n\n### Analyse\n```shell\nclovars analyse <analysis-settings-file>\n```\nwhere: \n- `analysis-settings-file` is the path for a TOML file with the analysis settings.\n\n### Fit experimental data\n```shell\nclovars fit <fit-settings-file>\n```\nwhere:\n- `fit-settings-file` is the path for a TOML file with the fit settings.\n\nPlease refer to the [this folder](examples) for examples on how this data should be formatted. \n\n## Dependencies\nCloVarS depends on the following third-party Python packages:\n- [ete3](http://etetoolkit.org/)\n- [matplotlib](https://matplotlib.org/)\n- [numpy](https://numpy.org/)\n- [pandas](https://pandas.pydata.org/)\n- [scipy](https://scipy.org/)\n- [seaborn](https://seaborn.pydata.org/)\n\n## License\nCloVarS is distributed under the MIT license. Read the [`LICENSE.md`](LICENSE.md) file for details.\n\n## Cite us\nIf you use CloVarS, cite us: *Faccioni, JL; Lenz, G.* (in preparation).\n',
    'author': 'Juliano Faccioni',
    'author_email': 'julianofaccioni@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://www.ufrgs.br/labsinal/clovars/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
