# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pymtheg']
install_requires = \
['spotdl>=3.9.3,<4.0.0']

entry_points = \
{'console_scripts': ['pymtheg = pymtheg:main']}

setup_kwargs = {
    'name': 'pymtheg',
    'version': '1.0.0',
    'description': 'A Python script to share songs from Spotify/YouTube as a 15 second clip.',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
