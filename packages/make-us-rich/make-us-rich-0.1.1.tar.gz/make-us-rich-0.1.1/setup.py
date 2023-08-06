# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['make_us_rich',
 'make_us_rich.cli',
 'make_us_rich.client',
 'make_us_rich.interface',
 'make_us_rich.pipelines',
 'make_us_rich.pipelines.converting',
 'make_us_rich.pipelines.exporting',
 'make_us_rich.pipelines.fetching',
 'make_us_rich.pipelines.preprocessing',
 'make_us_rich.pipelines.training',
 'make_us_rich.serving',
 'make_us_rich.utils',
 'make_us_rich.worker']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.26,<4.0.0',
 'docker>=5.0.3,<6.0.0',
 'ipython>=7.10,<8.0',
 'isort>=5.0,<6.0',
 'jupyter-client>=5.1',
 'jupyter>=1.0,<2.0',
 'jupyterlab>=3.0,<4.0',
 'kedro-viz==3.16.0',
 'kedro[pandas.CSVDataSet]==0.17.6',
 'minio==7.1.2',
 'onnx==1.10.2',
 'onnxruntime==v1.10.0',
 'pandas>=1.4.0,<2.0.0',
 'prefect==0.15.13',
 'python-binance==v0.7.10',
 'python-dotenv>=0.19.2,<0.20.0',
 'pytorch-lightning==1.5.9',
 'scikit-learn==1.0.2',
 'torch==1.10.2',
 'typer[all]>=0.4.0,<0.5.0',
 'wandb==0.12.9']

entry_points = \
{'console_scripts': ['mkrich = make_us_rich.cli.main:app']}

setup_kwargs = {
    'name': 'make-us-rich',
    'version': '0.1.1',
    'description': 'Cryptocurrency forecasting 📈 training and serving models made automatic',
    'long_description': '# Make Us Rich\nDeep Learning applied to cryptocurrency forecasting. This project is a tool to help people to train, serve and use \ncryptocurrencies forecasting models. This project was build by @ChainYo to help people building their own MLOps \nprojects.\n\nFor more details on how to use this project, please refer to [documentation](https://chainyo.github.io/make-us-rich/).\n(🚧 Still in development)\n\nYou can inspect the training pipeline with the `Kedro Viz` tool, available [here](https://makeusrich-viz.chainyo.tech)\n\nHere is the simplified project architecture:\n\n![Project Architecture](./docs/img/project_architecture.png)\n\n---\n\n## Installation\n\n```bash\npip install make-us-rich\n```\n\n## Support\n\nIf you encounter any problems using this project, please open an issue [here](https://github.com/ChainYo/make-us-rich/issues).\n\nIf you find this project usefull, please consider supporting by sharing the repo and giving a ⭐! \n',
    'author': 'Thomas Chaigneau',
    'author_email': 't.chaigneau.tc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
