# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vae_anomaly_detection']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.0',
 'numpy>=1.18',
 'path>=15.0',
 'pytorch-ignite>=0.4',
 'tensorboard>=0.20',
 'torch>=1.8.0',
 'tqdm>=4.0']

setup_kwargs = {
    'name': 'vae-anomaly-detection',
    'version': '1.0.0',
    'description': 'Pytorch/TF1 implementation of Variational AutoEncoder for anomaly detection following the paper "Variational Autoencoder based Anomaly Detection using Reconstruction Probability by Jinwon An, Sungzoon Cho"',
    'long_description': None,
    'author': 'Michele De Vita',
    'author_email': 'mik3dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Michedev/VAE_anomaly_detection',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2',
}


setup(**setup_kwargs)
