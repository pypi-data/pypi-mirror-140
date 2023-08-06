# kedroio
A module extending the datasets that come shipped with `kedro`

[![](https://img.shields.io/badge/python-3.8-blue.svg)](https://github.com/pyenv/pyenv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Example usage
```sql
-- example.sql
select *
from "database"."table_name"
limit 5;
```

```yaml
# conf/base/catalog.py
my_athena_dataset:
  type: kedroio.datasets.aws.athena.AthenaQueryDataSet
  filepath: data/01_raw/example.csv
  sql_filepath: example.sql
  bucket: example-bucket
  workgroup: primary
  subfolder: data
  region_name: eu-west-2
  read_result: true # read into pandas DataFrame
  overwrite: false # skip download if filepath exists
```

## Testing

Start `moto` server for mocked AWS resources
```sql
moto_server
```

Run tests
```sql
pytest tests/
```