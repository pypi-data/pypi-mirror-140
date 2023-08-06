# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['daaja',
 'daaja.augmentors',
 'daaja.augmentors.sentence',
 'daaja.augmentors.sequence_labeling',
 'daaja.flows',
 'daaja.methods.eda',
 'daaja.methods.ner_sda']

package_data = \
{'': ['*']}

install_requires = \
['SudachiDict-core>=20211220,<20211221',
 'SudachiPy>=0.6.3,<0.7.0',
 'fugashi>=1.1.2,<2.0.0',
 'ipadic>=1.0.0,<2.0.0',
 'numpy>=1.3',
 'pandas>=1.2',
 'requests>=2.27.1,<3.0.0',
 'sentencepiece>=0.1.96,<0.2.0',
 'torch>=1.10.2,<2.0.0',
 'tqdm>=4.62.3,<5.0.0',
 'transformers>=4.16.2,<5.0.0']

setup_kwargs = {
    'name': 'daaja',
    'version': '0.0.5',
    'description': 'NLP data augmentation tool',
    'long_description': 'None',
    'author': 'Koga Kobayashi',
    'author_email': 'kajyuuen@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
