# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sfctools',
 'sfctools.automation',
 'sfctools.bottomup',
 'sfctools.core',
 'sfctools.datastructs',
 'sfctools.misc']

package_data = \
{'': ['*']}

install_requires = \
['attrs==19.3.0',
 'cattrs==1.0.0',
 'graphviz>=0.19,<0.20',
 'matplotlib>=3.4,<4.0',
 'networkx>=2.6.3,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pandas>=1.0,<2.0',
 'pip>=21.1.1,<22.0.0',
 'poetry>=1.1.6,<2.0.0',
 'pyyaml>=6.0,<7.0',
 'seaborn>=0.11.2,<0.12.0',
 'setuptools>=60.0.0,<61.0.0',
 'wheel>=0.36.2,<0.37.0']

setup_kwargs = {
    'name': 'sfctools',
    'version': '0.4.1',
    'description': 'Framework for stock-flow consistent agent-based modeling, being developed at the German Aerospace Center (DLR) for and in the scientific context of energy systems analysis, however, it is widely applicable in other scientific fields.',
    'long_description': '# sfctools - A toolbox for stock-flow consistent, agent-based models\n\nSfctools is a lightweight and easy-to-use Python framework for agent-based macroeconomic, stock-flow consistent (ABM-SFC) modeling. It concentrates on agents in economics and helps you to construct agents, helps you to manage and document your model parameters, assures stock-flow consistency, and facilitates basic economic data structures (such as the balance sheet).\n\n\n| Author Thomas Baldauf, German Aerospace Center (DLR), Curiestr. 4 70563 Stuttgart | thomas.baldauf@dlr.de | version: 0.4 (Beta) | date: February 2022\n',
    'author': 'Thomas Baldauf, Benjamin Fuchs',
    'author_email': 'thomas.baldauf@dlr.de, benjamin.fuchs@dlr.de',
    'maintainer': 'Thomas Baldauf',
    'maintainer_email': 'thomas.baldauf@dlr.de',
    'url': 'https://gitlab.com/dlr-ve/esy/sfctools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
