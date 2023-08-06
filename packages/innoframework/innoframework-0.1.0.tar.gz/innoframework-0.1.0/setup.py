# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['innoframework',
 'innoframework.data',
 'innoframework.utils',
 'innoframework.wrappers']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=1.1.0,<2.0.0',
 'h5py>=3.6.0,<4.0.0',
 'hydra-core>=1.1.1,<2.0.0',
 'pytorch-lightning>=1.5.10,<2.0.0',
 'segmentation-models-pytorch>=0.2.1,<0.3.0',
 'sklearn>=0.0,<0.1',
 'streamlit>=1.5.1,<2.0.0',
 'torch>=1.10.2,<2.0.0']

setup_kwargs = {
    'name': 'innoframework',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Kazybek Askarbek',
    'author_email': 'k.askarbek@innopolis.university',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
