# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['os_image_builder']
install_requires = \
['click>=8.0.3,<9.0.0',
 'requests>=2.27.1,<3.0.0',
 'ruamel.yaml>=0.17.20,<0.18.0']

entry_points = \
{'console_scripts': ['os-image-builder = os_image_builder:main']}

setup_kwargs = {
    'name': 'os-image-builder',
    'version': '0.1.4',
    'description': 'Helper for image isos',
    'long_description': None,
    'author': 'Martin Ortbauer',
    'author_email': 'mortbauer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
