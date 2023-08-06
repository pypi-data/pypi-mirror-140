# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['spawndb']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy[asyncio]>=1.4.31,<2.0.0']

setup_kwargs = {
    'name': 'spawndb',
    'version': '0.1.15',
    'description': '',
    'long_description': "# TestDB\n\nThis is a simple library that helps in the creation of test databases for Python\nprojects that use SQLAlchemy.\n\nIt's aim it's to seamlessly handle creation of a separate test database, including\nthe creation of all schema objects and finally, handling the destruction of the test\ndatabase when it's no longer needed.\n\n# Usage\nTo create a test database, use the init_test_db function.\n\nThis function expects two arguments:  \n   - *database_url*: sqlalchemy.engine.URL  \n   - *metadata*: sqlalchemy.schema.MetaData\n\nIt will return an instantiated Engine for the test database which you can use for \nyour database logics.\n\n```python\n# Sample usage for Pytest\nfrom testdb import init_test_db, destroy_test_db\n\ndef my_cool_test():\n    db_engine = init_test_db(database_url, sqla_metadata)\n    \n    try:\n        # your stuff goes here\n    \n    finally:\n        destroy_test_db(database_url)\n```\n\n",
    'author': 'Pablo Prieto',
    'author_email': 'pabloprieto@live.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
