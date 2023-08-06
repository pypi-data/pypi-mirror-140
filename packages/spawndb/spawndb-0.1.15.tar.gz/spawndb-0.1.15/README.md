# TestDB

This is a simple library that helps in the creation of test databases for Python
projects that use SQLAlchemy.

It's aim it's to seamlessly handle creation of a separate test database, including
the creation of all schema objects and finally, handling the destruction of the test
database when it's no longer needed.

# Usage
To create a test database, use the init_test_db function.

This function expects two arguments:  
   - *database_url*: sqlalchemy.engine.URL  
   - *metadata*: sqlalchemy.schema.MetaData

It will return an instantiated Engine for the test database which you can use for 
your database logics.

```python
# Sample usage for Pytest
from testdb import init_test_db, destroy_test_db

def my_cool_test():
    db_engine = init_test_db(database_url, sqla_metadata)
    
    try:
        # your stuff goes here
    
    finally:
        destroy_test_db(database_url)
```

