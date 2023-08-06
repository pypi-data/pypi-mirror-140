# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apipe']

package_data = \
{'': ['*']}

install_requires = \
['cloudpickle>=2.0.0,<3.0.0',
 'dask[delayed]>=2021.01.1,<2022.0.0',
 'loguru>=0.5.0,<0.6.0',
 'numpy>=1.16.5,<2.0.0',
 'pandas>=1.2.0,<2.0.0',
 'pyarrow>=5.0.0,<6.0.0',
 'xxhash>=2.0.2,<3.0.0']

setup_kwargs = {
    'name': 'apipe',
    'version': '0.1.4',
    'description': 'Data pipelines with lazy computation and caching',
    'long_description': '# A-Pipe\n\n**A-Pipe** allows to create data pipelines with lazy computation and caching.\n\n**Features:**\n- Lazy computation and cache loading\n- Pickle and parquet serialization\n- Support for hashing of `numpy` arrays and `pandas` DataFrames\n- Support for `dask.Delayed` objects\n\n## Installation\n\n```shell\npip install apipe\n```\n\n## Examples\n\n### Simple function caching\n\n```python\nimport time\nimport apipe\nimport numpy as np\nfrom loguru import logger\n\n@apipe.eager_cached()\ndef load_data(table: str):\n    time.sleep(1)\n    arr = np.ones(5)\n    logger.debug(f"transferred array data from table={table}")\n    return arr\n\nlogger.info("start loading data")\n\n# --- First pass: transfer data and save on disk\ndata = load_data("weather-ldn")\nlogger.info(f"finished loading data: {load_data()}")\n\n# --- Second pass: load data from disk\ndata = load_data("weather-ldn")\nlogger.info(f"finished loading data: {load_data()}")\n```\n\n\n### Data pipeline with lazy execution and caching\n\n```python\nimport apipe\nimport pandas as pd\nimport numpy as np\nfrom loguru import logger\n\n# --- Define data transformations via step functions (similar to dask.delayed)\n\n@apipe.delayed_cached()  # lazy computation + caching on disk\ndef load_1():\n    df = pd.DataFrame({"a": [1., 2.], "b": [0.1, np.nan]})\n    logger.debug("Loaded {} records".format(len(df)))\n    return df\n\n@apipe.delayed_cached()  # lazy computation + caching on disk\ndef load_2(timestamp):\n    df = pd.DataFrame({"a": [0.9, 3.], "b": [0.001, 1.]})\n    logger.debug("Loaded {} records".format(len(df)))\n    return df\n\n@apipe.delayed_cached()  # lazy computation + caching on disk\ndef compute(x, y, eps):\n    assert x.shape == y.shape\n    diff = ((x - y).abs() / (y.abs()+eps)).mean().mean()\n    logger.debug("Difference is computed")\n    return diff\n\n# --- Define pipeline dependencies\nts = pd.Timestamp(2019, 1, 1)\neps = 0.01\ns1 = load_1()\ns2 = load_2(ts)\ndiff = compute(s1, s2, eps)\n\n# --- Trigger pipeline execution (first pass: compute everything and save on disk)\nlogger.info("diff: {:.3f}".format(apipe.delayed_compute((diff, ))[0]))\n\n# --- Trigger pipeline execution (second pass: load from disk the end result only)\nlogger.info("diff: {:.3f}".format(apipe.delayed_compute((diff, ))[0]))\n```\n\nSee more examples in a [notebook](https://github.com/mysterious-ben/ds-examples/blob/master/dataflows/dask_delayed_with_caching.ipynb).',
    'author': 'Mysterious Ben',
    'author_email': 'datascience@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mysterious-ben/apipe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
