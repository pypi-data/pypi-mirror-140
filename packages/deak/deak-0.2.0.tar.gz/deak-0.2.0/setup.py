# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deak']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'fire>=0.4.0,<0.5.0', 'mojimoji>=0.0.12,<0.0.13']

entry_points = \
{'console_scripts': ['han2zen = deak.converter:han2zen',
                     'json2yaml = deak.converter:json2yaml',
                     'yaml2json = deak.converter:yaml2json',
                     'zen2han = deak.converter:zen2han']}

setup_kwargs = {
    'name': 'deak',
    'version': '0.2.0',
    'description': "Deak: A Developer's Army Knife.",
    'long_description': None,
    'author': 'ryo.ishii',
    'author_email': 'ryoishii1101@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
