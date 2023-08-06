# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorch_common',
 'pytorch_common.callbacks',
 'pytorch_common.callbacks.mixin',
 'pytorch_common.callbacks.output',
 'pytorch_common.callbacks.output.plot',
 'pytorch_common.error',
 'pytorch_common.kfoldcv',
 'pytorch_common.kfoldcv.strategy',
 'pytorch_common.modules',
 'pytorch_common.util']

package_data = \
{'': ['*']}

install_requires = \
['bunch>=1.0.1,<2.0.0',
 'ipython>=7.31.0,<8.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.0,<2.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'torch>=1.10.1,<2.0.0']

setup_kwargs = {
    'name': 'pytorch-common',
    'version': '0.0.12',
    'description': 'Common torch tools and extension',
    'long_description': "# pytorch-common\n\nA [Pypi module](https://pypi.org/project/pytorch-common/) with pytorch common tools like:\n\n* **Callbacks** (keras style)\n  * **Validation**: Model validation.\n  * **ReduceLROnPlateau**:     \n    * Reduce learning rate when a metric has stopped improving. \n    * Models often benefit from reducing the learning rate by a factor\n      of 2-10 once learning stagnates. This scheduler reads a metrics\n      quantity and if no improvement is seen for a 'patience' number\n      of epochs, the learning rate is reduced.\n  * **EarlyStop**:\n    * Stop training when model has stopped improving a specified metric.\n  * **SaveBestModel**: \n    * Save model weights to file while model validation metric improve.\n  * **Logger**:\n    * Logs context properties. \n    * In general is used to log performance metrics every n epochs.\n  * **MetricsPlotter**:\n    * Plot evaluation metrics. \n    * This graph is updated every n epochs during training process.\n  * **Callback** and **OutputCallback**: \n    * Base classes.\n  * **CallbackManager**:\n    * Simplify callbacks support to fit custom models.\n* **StratifiedKFoldCV**: \n  * Support parallel fold processing on CPU.\n* **Mixins**\n  * FiMixin\n  * CommonMixin\n* **Utils**\n  * device management\n  * stopwatch\n  * data split\n  * os\n  * model\n  * LoggerBuilder\n\n",
    'author': 'adrianmarino',
    'author_email': 'adrianmarino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adrianmarino/pytorch-common/tree/master',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
