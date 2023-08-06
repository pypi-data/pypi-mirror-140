# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kedroio',
 'kedroio.connectors',
 'kedroio.connectors.aws',
 'kedroio.connectors.util',
 'kedroio.datasets',
 'kedroio.datasets.aws']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.20.17,<2.0.0', 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'kedroio',
    'version': '0.1.1',
    'description': 'Extension for `kedro` datasets',
    'long_description': '# kedroio\nA module extending the datasets that come shipped with `kedro`\n\n[![](https://img.shields.io/badge/python-3.8-blue.svg)](https://github.com/pyenv/pyenv)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n## Example usage\n```sql\n-- example.sql\nselect *\nfrom "database"."table_name"\nlimit 5;\n```\n\n```yaml\n# conf/base/catalog.py\nmy_athena_dataset:\n  type: kedroio.datasets.aws.athena.AthenaQueryDataSet\n  filepath: data/01_raw/example.csv\n  sql_filepath: example.sql\n  bucket: example-bucket\n  workgroup: primary\n  subfolder: data\n  region_name: eu-west-2\n  read_result: true # read into pandas DataFrame\n  overwrite: false # skip download if filepath exists\n```\n\n## Testing\n\nStart `moto` server for mocked AWS resources\n```sql\nmoto_server\n```\n\nRun tests\n```sql\npytest tests/\n```',
    'author': 'atsangarides',
    'author_email': 'andreas_tsangarides@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/atsangarides/kedroio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
