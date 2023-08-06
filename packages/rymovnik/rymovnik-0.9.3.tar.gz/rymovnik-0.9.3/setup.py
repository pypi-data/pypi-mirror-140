# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rymovnik']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['rymovnik = rymovnik.rymovnik:main']}

setup_kwargs = {
    'name': 'rymovnik',
    'version': '0.9.3',
    'description': 'A simple script to search for words in the dictionary based on criteria.',
    'long_description': None,
    'author': 'Lukáš Růžička',
    'author_email': 'lruzicka@redhat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
