# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jira_commands', 'jira_commands.cli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'jira>=3.1.1,<4.0.0', 'thelogrus>=0.6.2,<0.7.0']

entry_points = \
{'console_scripts': ['jc = jira_commands.cli.jc:jc_driver',
                     'jc-get-link-types = '
                     'jira_commands.cli.crudops:getLinkTypes',
                     'jc-link-tickets = jira_commands.cli.crudops:linkTickets',
                     'jc-ticket-assign = '
                     'jira_commands.cli.crudops:assignTicket',
                     'jc-ticket-close = jira_commands.cli.crudops:closeTicket',
                     'jc-ticket-comment = '
                     'jira_commands.cli.crudops:commentOnTicket',
                     'jc-ticket-comment-on-ticket = '
                     'jira_commands.cli.crudops:commentOnTicket',
                     'jc-ticket-create = '
                     'jira_commands.cli.crudops:createTicket',
                     'jc-ticket-examine = jira_commands.cli.vivisect:vivisect',
                     'jc-ticket-link = jira_commands.cli.crudops:linkTickets',
                     'jc-ticket-print = jira_commands.cli.print:printTicket',
                     'jc-ticket-transition-list = '
                     'jira_commands.cli.crudops:getTransitions',
                     'jc-ticket-transition-set = '
                     'jira_commands.cli.crudops:transitionTo',
                     'jc-ticket-vivisect = '
                     'jira_commands.cli.vivisect:vivisect']}

setup_kwargs = {
    'name': 'jira-commands',
    'version': '0.3.0',
    'description': 'Command line utilities for interacting with JIRA',
    'long_description': None,
    'author': 'Joe Block',
    'author_email': 'jblock@zscaler.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/unixorn/jira-commands',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
