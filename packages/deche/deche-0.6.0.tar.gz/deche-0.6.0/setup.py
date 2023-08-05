# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deche', 'deche.test_utils']

package_data = \
{'': ['*']}

install_requires = \
['cloudpickle>=2.0.0,<3.0.0', 'donfig>=0.7.0,<0.8.0', 'fsspec>=2021.10.1']

extras_require = \
{'s3': ['s3fs>=2021.7.0']}

setup_kwargs = {
    'name': 'deche',
    'version': '0.6.0',
    'description': '',
    'long_description': None,
    'author': 'Bradley McElroy',
    'author_email': 'bradley.mcelroy@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
