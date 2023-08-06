# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['useis',
 'useis.ai',
 'useis.core',
 'useis.processors',
 'useis.sandbox',
 'useis.sandbox.demo_kafka',
 'useis.sandbox.tomography',
 'useis.services',
 'useis.services.file_server',
 'useis.services.grid_service',
 'useis.services.models',
 'useis.settings',
 'useis.tomography']

package_data = \
{'': ['*']}

install_requires = \
['confluent-kafka>=1.7.0,<2.0.0',
 'docker>=5.0.3,<6.0.0',
 'dynaconf>=3.1.4,<4.0.0',
 'fastapi>=0.68.1,<0.69.0',
 'furl>=2.1.2,<3.0.0',
 'myst-parser>=0.15.1,<0.16.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'rinohtype>=0.5.3,<0.6.0',
 'scikit-learn>=1.0.1,<2.0.0',
 'sklearn>=0.0,<0.1',
 'torch>=1.10.0,<2.0.0',
 'torchaudio>=0.10.0,<0.11.0',
 'torchvision>=0.11.1,<0.12.0',
 'uquake>=0.10.1,<0.11.0',
 'uvicorn>=0.15.0,<0.16.0']

extras_require = \
{':extra == "docs"': ['Sphinx>=4.1.2,<5.0.0', 'sphinx-rtd-theme>=0.5.2,<0.6.0']}

setup_kwargs = {
    'name': 'useis',
    'version': '0.9.23',
    'description': '',
    'long_description': None,
    'author': 'jpmercier',
    'author_email': 'jpmercier01@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
