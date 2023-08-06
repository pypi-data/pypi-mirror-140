# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['opreport',
 'opreport.helpers',
 'opreport.opsramp',
 'opreport.reports',
 'opreport.reportutil']

package_data = \
{'': ['*'],
 'opreport': ['conf/sample-logo.jpeg'],
 'opreport.reports': ['fonts/*']}

install_requires = \
['DateTime>=4.4,<5.0',
 'PyYAML>=6.0,<7.0',
 'appdirs>=1.4.4,<2.0.0',
 'argparse>=1.4.0,<2.0.0',
 'fpdf2>=2.5.0,<3.0.0',
 'json5>=0.9.6,<0.10.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.1,<2.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['opreport = opreport.reportutil:main']}

setup_kwargs = {
    'name': 'opreport',
    'version': '0.1.16',
    'description': 'Some useful multi-tenant pdf reports for OpsRamp',
    'long_description': '# Multi-Client Reporting Utility for OpsRamp  \n\n## Purpose\n\nThis is a utility intended for use by OpsRamp customers needing to batch-generate some useful reports across all tenants in their partner instance.\n\n## First time execution\nThe first time it is run, it will look to see if the default environment config directory exists, and if it\'s not there it will create it.\n\nAfter that, you can either update the environments.yml file in the environment config directory with your partner-level OpsRamp API credentials, or you can specify API credentials on the command line.\n\n## Available Reports\nThe following reports are currently available.  Each report generates a separate report file for each tenant unless ptherwise specified:\n\n### Server Utilization Comparison\nThis report contains a page for each Windows or Linux server in the environment, with time-series graphs for the speficied period for CPU Utilization, File System Utilization, and Memory Utilization.  A table at the bottom of each page shows min, max, and average for the current period and increase/decrease trend from the baseline period.\n\n### Network Utilization\nThis is a fairly standard Top N report for Cisco device CPU Utilization, Memory Utilization, and Interface Utilization, Errors, etc.  It shows a time series only for the Top N items, followed by a detail report of all items sorted from highest to lowest.\n\n## Patch Management\nSummary of patches installed in the reporting period.\n\n\n## Remote Control Usage\nHistogram and detailed list of remote control console sessions that occurred in the reporting period.\n\n\n## Command line help:\n\n\n    usage: opreport [-h] [--env ENV] [--envfile ENVFILE] [--api_url API_URL] [--key KEY] [--secret SECRET] [--tenant TENANT] [--start START] [--end END] [--outdir OUTDIR]\n                    [--logo LOGO] [--secure SECURE] [--tenant_criteria TENANT_CRITERIA]\n                    {uc,nu,pm,rcu} ...\n\n        Multi-Client Reporting Utility for OpsRamp\n\n    positional arguments:\n    {uc,nu,pm,rcu}        Available commands\n        uc                  Generate Server Utilization Comparison Reports\n        nu                  Generate Network Utilization Reports\n        pm                  Generate Patch Management Reports\n        rcu                 Generate Remote Control Usage Reports\n\n    optional arguments:\n    -h, --help            show this help message and exit\n    --start START         Start date of reporting period in YYYY-MM-DD format (default=1st of prior month)\n    --end END             End date of reporting period in YYYY-MM-DD format (default=Last day of prior month)\n    --outdir OUTDIR       Directory where report output will be written (Default: ./output)\n    --logo LOGO           Logo image file for report headers (Default: /Users/michael.friedhoff/Library/Application Support/OpsRamp/logo.jpeg)\n    --secure SECURE       Whether or not to verify SSL cert (Default: True)\n    --tenant_criteria TENANT_CRITERIA\n                            Search criteria for which tenants to include as per https://develop.opsramp.com/tenancy-access-controls/tenants-orgid-clients-search (Default:\n                            "activeStatus:true", which will include all active tenants)\n\n    Use yaml environment file credentials:\n    --env ENV             Name of environment to use, referencing a named set of API credentials in environments.yml\n    --envfile ENVFILE     Location of environments YAML file to be used (Default: /Users/michael.friedhoff/Library/Application Support/OpsRamp/environments.yml)\n\n    Use command line credentials:\n    --api_url API_URL     Customer-specific API URL such as https://mycompany.api.opsramp.com\n    --key KEY             Authentication key\n    --secret SECRET       Authentication secret\n    --tenant TENANT       Authentication secret',
    'author': 'Michael Friedhoff',
    'author_email': 'michael.friedhoff@opsramp.com',
    'maintainer': 'Michael Friedhoff',
    'maintainer_email': 'michael.friedhoff@opsramp.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
