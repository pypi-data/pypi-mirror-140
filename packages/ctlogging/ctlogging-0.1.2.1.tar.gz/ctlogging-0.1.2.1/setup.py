# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ctlogging']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0', 'mysql-connector-python>=8.0.18,<9.0.0']

setup_kwargs = {
    'name': 'ctlogging',
    'version': '0.1.2.1',
    'description': 'Wrapper of Logging module for handling database and middlerware scenarios',
    'long_description': '# Ctlogging\n\nMiddleware for loading or generating correlation IDs for each run. Correlation IDs can be added to your logs, making it simple to retrieve all logs generated from a single run.\n\nIt also help in logging message in mysql database\n\nWhen the process starts a correlation ID is set in the contextvar and retrieve using the filter during logging and inject into log record.\n\n\n## 1. How to install\n\nUsing pip\n \n`pip install ctlogging`\n\nUsing poetry\n \n`poetry add ctlogging`\n\n\n## 2. How to use\nThere are main three step requires -\n\n* Initalize the logger at starting point of application \n  ```\n  from ctlogging.config import set_logger_from_yaml, set_logger\n\n  logger = set_logger_from_yaml(logconfig_yaml) # using file\n  logger = set_logger(config) # using dict\n  ```  \n\n* get logger at module/file level and start logging using logger built-in method\n  ```\n  from ctlogging.config import get_logger\n\n  logger = get_logger(__name__)\n  logger.info(message...)\n  logger.debug(message...)\n  ```\n\n* for correlation_id, set it at entry level of pipeline \n  ```\n  from uuid import uuid4\n  from ctlogging.context import correlation_id\n\n  def pipeline():\n      uid = uuid4().hex\n      correlation_id.set(uid) # uid is string\n      "do task....."\n  ```\n\n## 3. Configuration\nusing config.yaml file\n```\nversion: 1\nformatters:\n  simple:\n    format: \'%(asctime)s - %(correlation_id)s - %(levelname)s - %(name)s - %(message)s\'\nfilters:\n  correlation_id:\n    (): ctlogging.CorrelationId\nhandlers:\n  console:\n    class: logging.StreamHandler\n    level: DEBUG\n    formatter: simple\n    filters: [correlation_id]\n    stream: ext://sys.stdout\n  file:\n    class : logging.handlers.RotatingFileHandler\n    formatter: simple\n    filename: extraction.log\n    maxBytes: 3000000\n    backupCount: 3\n    filters: [correlation_id]\n  db:\n    class : ctlogging.MysqlHandler\n    level: DEBUG\n    host: localhost\n    database: ares\n    user: root\n    password: root\n    port: 3306\nloggers:\n  root:\n    level: DEBUG\n    handlers: [console, db]\n    propagate: true\nroot_logger_name: root\n```\n\n## 3. for Developement\nSteps: -\n1. git clone the repo\n2. install poetry from `https://python-poetry.org/docs/master/#installing-with-the-official-installer`\n3. goto `ctlogging` directory\n4. poetry install\n\n\n\n\n\n\n',
    'author': 'Rohit Choudhary',
    'author_email': 'rohitchoudhary19398@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rohitchoudhary19398/ctlogging',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
