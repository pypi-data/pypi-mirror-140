# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['risk_model_tool',
 'risk_model_tool.analysis',
 'risk_model_tool.model',
 'risk_model_tool.preprocess',
 'risk_model_tool.utils']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.0.1,<10.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.2,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.4.1,<2.0.0',
 'python-highcharts>=0.4.2,<0.5.0',
 'scikit-learn>=1.0.2,<2.0.0']

setup_kwargs = {
    'name': 'risk-model-tool',
    'version': '0.1.1',
    'description': 'This is a package help analyzing, preprocessing, and modeling in credit default projects.',
    'long_description': '# risk_model_tool\n\nThis is a package help analyzing, preprocessing, and modeling in credit default projects.\n\n## Installation\n\n```bash\n$ pip install risk_model_tool\n```\n\n## Usage\n\nThe whole package is consisted of 4 parts: `analysis`, `preprocess`, `model`, `utils`.\n\n  - `analysis`: \n  - `preprocess`:\n  - `model`: \n  - `utils`: [Doc of Utils](https://github.com/PANDASANG1231/risk_model_tool/blob/master/docs/example.ipynb)\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`risk_model_tool` was created by Wenjia Zhu, Jianhong Jiang, Jingcheng Qiu. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`risk_model_tool` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Wenjia Zhu, Jianhong Jiang, Jingcheng Qiu',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
