# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['teams_logger']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'teams-logger',
    'version': '0.4.1',
    'description': 'Microsoft Teams logging handler for Python',
    'long_description': 'teams-logger\n===================\n\nPython logging handler for Microsoft Teams webhook integration with both simple and dictionary configurations.\n\nInstallation\n------------\n.. code-block:: bash\n\n    pip install teams-logger\n\nExamples\n--------\nSimple configuration\n\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\n.. code-block:: python\n\n  import logging\n  from teams_logger import TeamsHandler\n\n  th = TeamsHandler(url=\'YOUR_WEB_HOOK_URL\', level=logging.INFO)\n  logging.basicConfig(handlers=[th])\n  logging.warning(\'warn message\')\n\nSimple configuration and non blocking handler\n\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\n.. code-block:: python\n\n  import logging\n  from teams_logger import TeamsQueueHandler\n  th = TeamsQueueHandler(url=\'YOUR_WEB_HOOK_URL\', level=logging.INFO)\n  logging.basicConfig(handlers=[th])\n  logging.info("info message")\n\nSimple configuration and Card Formatter\n\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\n.. code-block:: python\n\n  import logging\n  from teams_logger import TeamsHandler, Office365CardFormatter\n\n  logger = logging.getLogger(__name__)\n  logger.setLevel(logging.DEBUG)\n\n  th = TeamsHandler(url=\'YOUR_WEB_HOOK_URL\', level=logging.INFO)\n  th.setLevel(logging.DEBUG)\n  logger.addHandler(th)\n\n  cf = Office365CardFormatter(facts=["name", "levelname", "lineno"])\n  th.setFormatter(cf)\n  logger.debug(\'debug message\')\n  logger.info(\'info message\')\n  logger.warning(\'warning message\')\n  logger.error(\'error message\')\n  logger.critical(\'critical message\')\n\n  try:\n      2/0\n  except ZeroDivisionError as e:\n      logger.error(\'Oops !\', exc_info=True)\n\nDictionary configuration and Card Formatter\n\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\n.. code-block:: python\n\n  import logging\n  import logging.config\n  from teams_logger import TeamsHandler, Office365CardFormatter\n\n  url = \'YOUR_WEB_HOOK_URL\'\n  logging_dict = {\n      \'version\': 1, \n      \'disable_existing_loggers\': False,\n      \'formatters\': {\n          \'teamscard\': {\n              \'()\': Office365CardFormatter,\n              \'facts\': ["name", "levelname", "lineno"],\n          },\n      },\n      \'handlers\': {\n          \'msteams\': {\n              \'level\': logging.INFO,\n              \'class\': \'teams_logger.TeamsHandler\',\n              \'url\': url,\n              \'formatter\': \'teamscard\',\n          },\n      },\n      \'loggers\': {\n          __name__: {\n              \'handlers\': [\'msteams\'],\n              \'level\': logging.DEBUG,\n          }\n      },\n  }\n  logging.config.dictConfig(logging_dict)\n  logger = logging.getLogger(__name__)\n  logger.info(\'Info message\')\n',
    'author': 'Anes Foufa',
    'author_email': 'anes.foufa@upply.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AnesFoufa/python-teams-logger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
