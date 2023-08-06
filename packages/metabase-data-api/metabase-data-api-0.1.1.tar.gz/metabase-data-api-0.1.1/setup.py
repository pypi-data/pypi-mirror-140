# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['metabase_data_api']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.23.0,<3.0.0']

setup_kwargs = {
    'name': 'metabase-data-api',
    'version': '0.1.1',
    'description': 'A package for querying metabase data via api.',
    'long_description': '# Usage\nThis is a python package meant to query metabase datasources via api.\n\ninstall the package:\n`pip install mbdata`\n\nusage:\n\n```\nimport pandas as pd\nfrom metabase_data_api import MetabaseApi as M\nimport json\n\nsession_params = dict(user=\'name@company.ai\',\n                      password=\'demopass1\',\n                      url=\'https://yourteam.metabaseapp.com/\'\n                      )\n\nmb_api = M(**session_params)\n\nquery = \'SELECT 12 as col\'\n\n#get raw file data via export\nd = mb_api.export_from_query(query, database_id=4)\n\njson.loads(d.decode("utf-8"))\n\ndf = pd.DataFrame.from_records(d)\n\n\nprint(df)\n#   col\n#0   12\n```\n\n\n# Limits\nThe get_ methods are calling the same endpoints that are used by metabase for its own charting and are limited to 2k rows of results\n\nThe export method uses the file download functionality which is limited to 1m rows.\n',
    'author': 'Adrian Brudaru',
    'author_email': 'adrian@scalevector.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/scale-vector/metabase_data_api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
