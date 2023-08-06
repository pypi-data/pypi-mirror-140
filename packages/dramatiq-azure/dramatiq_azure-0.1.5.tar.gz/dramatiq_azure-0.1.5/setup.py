# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dramatiq_azure']

package_data = \
{'': ['*']}

install_requires = \
['azure-core>=1.20.1,<2.0.0',
 'azure-storage-queue>=12.1.6,<13.0.0',
 'dramatiq>=1.12.0,<2.0.0',
 'pre-commit>=2.17.0,<3.0.0']

setup_kwargs = {
    'name': 'dramatiq-azure',
    'version': '0.1.5',
    'description': 'Azure Queue Brokers for Dramatiq',
    'long_description': '# dramatiq-azure\n[![CI](https://github.com/bidossessi/dramatiq-azure/actions/workflows/ci.yml/badge.svg)](https://github.com/bidossessi/dramatiq-azure/actions/workflows/ci.yml)\n[![Pypi](https://github.com/bidossessi/dramatiq-azure/actions/workflows/python-publish.yml/badge.svg)](https://github.com/bidossessi/dramatiq-azure/actions/workflows/python-publish.yml)\n[![codecov](https://codecov.io/gh/bidossessi/dramatiq-azure/branch/main/graph/badge.svg?token=6LLEDAM3SG)](https://codecov.io/gh/bidossessi/dramatiq-azure)\n[![BCH compliance](https://bettercodehub.com/edge/badge/bidossessi/dramatiq-azure?branch=main)](https://bettercodehub.com/)\n[![Total alerts](https://img.shields.io/lgtm/alerts/g/bidossessi/dramatiq-azure.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/bidossessi/dramatiq-azure/alerts/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)\n\n\nA [Dramatiq](https://dramatiq.io) broker that can be used with [Microsoft Azure](https://azure.microsoft.com/en-us/) queue services.\n\nHeavily inspired by [Dramatiq SQS](https://github.com/Bogdanp/dramatiq_sqs), this package currently implements a broker for [Azure Storage Queue](https://docs.microsoft.com/en-us/azure/storage/queues/).\nAn implementation for [Azure Service Bus](https://docs.microsoft.com/en-us/azure/service-bus-messaging/) is planned... eventually.\n\n\n## Installation\n\n```shell\n    pip install dramatiq-azure\n```\n## Usage\n\n### ASQBroker\n\nThe broker looks for `AZURE_STORAGE_CONNECTION_STR` in the environment, to authenticate on Azure Storage.\nYou need to make sure that the variable exists at runtime.\n\nCreating a connection string for your Azure account is documented [here](https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string).\n\n\n```python\nimport os\nimport dramatiq\n\nfrom dramatiq.middleware import AgeLimit, TimeLimit, Callbacks, Pipelines, Prometheus, Retries\nfrom dramatiq_azure import ASQBroker\n\n\nbroker = ASQBroker(\n    dead_letter=True,\n    middleware=[\n        Prometheus(),\n        AgeLimit(),\n        TimeLimit(),\n        Callbacks(),\n        Pipelines(),\n        Retries(min_backoff=1000, max_backoff=900000, max_retries=96),\n    ],\n)\ndramatiq.set_broker(broker)\n```\n\n## Tests\n\nTests require a running [Azurite](https://github.com/Azure/Azurite) instance. You can easily launch `azurite` through [Docker](https://www.docker.com/).\n\n```shell\ndocker run -p 10000:10000 -p 10001:10001 -p 10002:10002 mcr.microsoft.com/azure-storage/azurite\n```\n\nRun the test suite\n\n```shell\npytest\n```\n\n## Contributions\n\nFound an itch you know how to scratch? PR welcome\n',
    'author': 'Stanislas H.B. Sodonon',
    'author_email': 'stanislas.sodonon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bidossessi/dramatiq-azure',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
