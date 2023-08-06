# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['leap_model_parser', 'leap_model_parser.contract']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses==0.8',
 'keras-data-format-converter==0.0.4',
 'numpy>=1.19.5,<2.0.0',
 'onnx2kerastl==0.0.32',
 'onnx==1.6.0',
 'tensorflow-addons==0.14.0',
 'tensorflow-io-gcs-filesystem==0.21.0',
 'tensorflow==2.4.4']

setup_kwargs = {
    'name': 'leap-model-parser',
    'version': '0.1.2',
    'description': '',
    'long_description': '# Tensorleap model parser\nUsed to parse model to the import format \n',
    'author': 'idan',
    'author_email': 'idan.yogev@tensorleap.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tensorleap/leap-model-parser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<3.7',
}


setup(**setup_kwargs)
