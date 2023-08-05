# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['localizer']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0.2,<5.0.0',
 'django-filter>=21.1,<22.0',
 'djangorestframework>=3.13.1,<4.0.0']

setup_kwargs = {
    'name': 'localizer',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Алмас Бактубаев',
    'author_email': 'a.baktubayev@mycar.kz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
