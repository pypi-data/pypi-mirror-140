# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torchminer',
 'torchminer.plugins',
 'torchminer.plugins.Logger',
 'torchminer.plugins.Metrics',
 'torchminer.plugins.Recorder']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'google-api-python-client>=2.31.0,<3.0.0',
 'ipython>=7.18.0,<8.0.0',
 'matplotlib>=3.5.0,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pylint>=2.12.1,<3.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'sklearn>=0.0,<0.1',
 'tensorboardX>=2.4.1,<3.0.0',
 'torch>=1.8.0,<2.0.0',
 'tqdm>=4.50.0,<5.0.0']

setup_kwargs = {
    'name': 'torchminer',
    'version': '0.4.8',
    'description': 'Run Torch With A Simple Miner',
    'long_description': 'Published on [pypi](https://pypi.org/project/torchminer/)\n\nPackaged Using [Poetry](https://python-poetry.org/)\n\n# Description\nTorchMiner is designed to automatic process the training ,evaluating and testing process for PyTorch DeepLearning,with a simple API.\n\nYou can access all Functions of MineTorch simply use `Miner`.\n\n## Quick Start\n\n```python\nimport TorchMiner\nfrom TorchMiner import Miner\nfrom TorchMiner.plugins.Logger.Jupyter import JupyterLogger, JupyterTqdm\nfrom TorchMiner.plugins.Metrics import MultiClassesClassificationMetric\nfrom TorchMiner.plugins.Recorder import TensorboardDrawer\n\nminer = Miner(\n    alchemistic_directory=\'/the/route/to/log\', \n    train_dataloader=train_dataloader, \n    val_dataloader=val_dataloader,  \n\n    model=model, \n    loss_func=MSELoss,  \n    optimizer=optimizer,  \n    experiment="the-name-of-experiment",  # Subdistribution in the experimental directory\n    resume=True,  # Whether to automatically load the previous model\n    eval_epoch=1,  # How many rounds are evaluated\n    persist_epoch=2,  # How many rounds are saved once a checkpoint\n    accumulated_iter=1,  # How many times iterates the parameter update after accumulation\n    in_notebook=True,\n    amp=True,  # Whether to use amp\n    plugins=[\n        # Use the plugins to extend the function of miner\n        JupyterLogger(),\n        JupyterTqdm(),\n        # The two above plugins are designed to get better output in Jupyter Enviroment\n        MultiClassesClassificationMetric(),\n        # This Plugin can automaticly calculate Accuracy, kappa score and Confusion Matrix in Classification problems.\n        TensorboardDrawer(input_to_model),\n        # This Plugin can record the informations generate by training process or by other plugins in Tensorboard.\n    ],\n)\n\n# And then, trigger the training process by\nminer.train()',
    'author': 'InEase',
    'author_email': 'inease28@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
