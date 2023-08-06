# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbupgrade']

package_data = \
{'': ['*']}

install_requires = \
['sqlalchemy>=1.4,<2.0', 'sqlparse>=0.3.0']

entry_points = \
{'console_scripts': ['dbupgrade = dbupgrade.main:main']}

setup_kwargs = {
    'name': 'dbupgrade',
    'version': '2.3.0',
    'description': 'Database Migration Tool',
    'long_description': '# dbupgrade\n\nDatabase Migration Tool\n\n[![MIT License](https://img.shields.io/pypi/l/dbupgrade.svg)](https://pypi.python.org/pypi/dbupgrade/)\n[![GitHub](https://img.shields.io/github/release/srittau/dbupgrade/all.svg)](https://github.com/srittau/dbupgrade/releases/)\n[![pypi](https://img.shields.io/pypi/v/dbupgrade.svg)](https://pypi.python.org/pypi/dbupgrade/)\n[![GitHub Actions](https://img.shields.io/github/workflow/status/srittau/dbupgrade/Test%20and%20lint)](https://github.com/srittau/dbupgrade/actions)\n\n## Basic Usage\n\nUsage: `dbupgrade [OPTIONS] [-l API_LEVEL|-L] DBNAME SCHEMA DIRECTORY`\n\nUpgrade the given `SCHEMA` in the database specified as `DBNAME` with SQL\nscripts from `DIRECTORY`. `DIRECTORY` is searched for all files with the\n`.sql` suffix. These files are SQL scripts with a special header sections:\n\n```sql\n-- Schema: my-db-schema\n-- Version: 25\n-- API-Level: 3\n-- Dialect: postgres\n\nCREATE TABLE ...\n```\n\nThe following headers are required:\n\n- **Schema**  \n   Name of the schema to update.\n- **Dialect**  \n   Database dialect of this script. Use SQLalchemy\'s database\n  URL scheme identifier, e.g. `postgres` or `sqlite`.\n- **Version**  \n   The new version of the schema after this script was applied.\n  It is an error if two scripts have the same schema, dialect, and version.\n- **API-Level**  \n   The new API level of the schema after this script was applied.\n  For a given schema, the API level of a subsequent version must either be\n  equal or higher by one than the API level of the preceding version. For\n  example, if script version 44 has API level 3, script version 45 must\n  have API level 3 or 4.\n- **Transaction** _(optional)_  \n   Possible values are `yes` (default) and `no`. When this\n  header is yes, all statements of a single upgrade file and the\n  corresponding version upgrade statements are executed within a single\n  transaction. Otherwise each statement is executed separately. The former\n  is usually preferable so that all changes will be rolled back if a\n  script fails to apply, but the latter is required in some cases.\n\nThe database must contain a table `db_config` with three columns: `schema`,\n`version`, and `api_level`. If this table does not exist, it is created.\nThis table must contain exactly one row for the given schema. If this row\ndoes not exist, it is created with version and api_level initially set to 0.\n\nThe current version and API level of the schema are requested from the\ndatabase and all scripts with a higher version number are applied, in order.\nIf there are any version numbers missing, the script will stop after the\nlast version before the missing version.\n\nUnless the `-l` or `-L` option is supplied, only scripts that do not\nincrease the API level will be applied. If the `-l` option is given, all\nscripts up to the given API level will be applied. `-L` will apply all\nscripts without regard to the API level.\n\nEach script is executed in a seperate transaction. If a script fails, all\nchanges in that script will be rolled back and the script will stop with\nan error message and a non-zero return status.\n\n## JSON Output\n\nWhen supplying the `--json` option, `dbupgrade` will information about the\napplied scripts as JSON to the standard output. Sample output:\n\n```json\n{\n  "success": true,\n  "oldVersion": {\n    "version": 123,\n    "apiLevel": 15\n  },\n  "newVersion": {\n    "version": 125,\n    "apiLevel": 16\n  },\n  "appliedScripts": [\n    {\n      "filename": "0124-create-foo.sql",\n      "version": 124,\n      "apiLevel": 15\n    },\n    {\n      "filename": "0125-delete-bar-sql",\n      "version": 125,\n      "apiLevel": 16\n    }\n  ],\n  "failedScript": {\n    "filename": "0126-change-stuff.sql",\n    "version": 126,\n    "apiLevel": 16\n  }\n}\n```\n\n`success` is `true` if all scripts were applied successfully or no scripts\nwere to be applied. In this case, the `failedScript` key is not defined.\nThe `appliedScripts` key is always defined. In case no scripts were applied,\nit\'s an empty array.\n',
    'author': 'Sebastian Rittau',
    'author_email': 'srittau@rittau.biz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/srittau/dbupgrade',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
