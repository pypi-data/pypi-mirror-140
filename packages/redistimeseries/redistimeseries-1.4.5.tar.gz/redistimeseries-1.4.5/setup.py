# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redistimeseries']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.0.1,<5.0.0', 'redis==3.5.3']

setup_kwargs = {
    'name': 'redistimeseries',
    'version': '1.4.5',
    'description': 'RedisTimeSeries Python Client',
    'long_description': "[![license](https://img.shields.io/github/license/RedisTimeSeries/redistimeseries-py.svg)](https://github.com/RedisTimeSeries/redistimeseries-py)\n[![PyPI version](https://badge.fury.io/py/redistimeseries.svg)](https://badge.fury.io/py/redistimeseries)\n[![CircleCI](https://circleci.com/gh/RedisTimeSeries/redistimeseries-py/tree/master.svg?style=svg)](https://circleci.com/gh/RedisTimeSeries/redistimeseries-py/tree/master)\n[![GitHub issues](https://img.shields.io/github/release/RedisTimeSeries/redistimeseries-py.svg)](https://github.com/RedisTimeSeries/redistimeseries-py/releases/latest)\n[![Codecov](https://codecov.io/gh/RedisTimeSeries/redistimeseries-py/branch/master/graph/badge.svg)](https://codecov.io/gh/RedisTimeSeries/redistimeseries-py)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/RedisTimeSeries/redistimeseries-py.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/RedisTimeSeries/redistimeseries-py/context:python)\n[![Known Vulnerabilities](https://snyk.io/test/github/RedisTimeSeries/redistimeseries-py/badge.svg?targetFile=pyproject.toml)](https://snyk.io/test/github/RedisTimeSeries/redistimeseries-py?targetFile=pyproject.toml)\n\n# redistimeseries-py\n[![Forum](https://img.shields.io/badge/Forum-RedisTimeSeries-blue)](https://forum.redislabs.com/c/modules/redistimeseries)\n[![Discord](https://img.shields.io/discord/697882427875393627?style=flat-square)](https://discord.gg/KExRgMb)\n\n## Deprecation notice\n\nAs of [redis-py 4.0.0](https://pypi.org/project/redis/) this library is deprecated. It's features have been merged into redis-py. Please either install it [from pypy](https://pypi.org/project/redis) or [the repo](https://github.com/redis/redis-py).\n\n--------------------------------\n\nredistimeseries-py is a package that gives developers easy access to RedisTimeSeries module. The package extends [redis-py](https://github.com/andymccurdy/redis-py)'s interface with RedisTimeSeries's API.\n\n## Installation\n```\n$ pip install redistimeseries\n```\n\n## Development\n\n1. Create a virtualenv to manage your python dependencies, and ensure it's active.\n   ```virtualenv -v venv```\n2. Install [pypoetry](https://python-poetry.org/) to manage your dependencies.\n   ```pip install poetry```\n3. Install dependencies.\n   ```poetry install```\n\n[tox](https://tox.readthedocs.io/en/latest/) runs all tests as its default target. Running *tox* by itself will run unit tests. Ensure you have a running redis, with the module loaded.\n\n\n\n## API\nThe complete documentation of RedisTimeSeries's commands can be found at [RedisTimeSeries's website](http://redistimeseries.io/).\n\n## Usage example\n\n```python\n# Simple example\nfrom redistimeseries.client import Client\nrts = Client()\nrts.create('test', labels={'Time':'Series'})\nrts.add('test', 1, 1.12)\nrts.add('test', 2, 1.12)\nrts.get('test')\nrts.incrby('test',1)\nrts.range('test', 0, -1)\nrts.range('test', 0, -1, aggregation_type='avg', bucket_size_msec=10)\nrts.range('test', 0, -1, aggregation_type='sum', bucket_size_msec=10)\nrts.info('test').__dict__\n\n# Example with rules\nrts.create('source', retention_msecs=40)\nrts.create('sumRule')\nrts.create('avgRule')\nrts.createrule('source', 'sumRule', 'sum', 20)\nrts.createrule('source', 'avgRule', 'avg', 15)\nrts.add('source', '*', 1)\nrts.add('source', '*', 2)\nrts.add('source', '*', 3)\nrts.get('sumRule')\nrts.get('avgRule')\nrts.info('sumRule').__dict__\n```\n\n## Further notes on back-filling time series\n\nSince [RedisTimeSeries 1.4](https://github.com/RedisTimeSeries/RedisTimeSeries/releases/tag/v1.4.5) we've added the ability to back-fill time series, with different duplicate policies.\n\nThe default behavior is to block updates to the same timestamp, and you can control it via the `duplicate_policy` argument. You can check in detail the [duplicate policy documentation](https://oss.redislabs.com/redistimeseries/configuration/#duplicate_policy).\n\nBellow you can find an example of the `LAST` duplicate policy, in which we override duplicate timestamps with the latest value:\n\n```python\nfrom redistimeseries.client import Client\nrts = Client()\nrts.create('last-upsert', labels={'Time':'Series'}, duplicate_policy='last')\nrts.add('last-upsert', 1, 10.0)\nrts.add('last-upsert', 1, 5.0)\n# should output [(1, 5.0)]\nprint(rts.range('last-upsert', 0, -1))\n```\n\n## License\n[BSD 3-Clause](https://github.com/ashtul/redistimeseries-py/blob/master/LICENSE)\n",
    'author': 'RedisLabs',
    'author_email': 'oss@redislabs.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
