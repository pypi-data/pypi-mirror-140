<a href="https://github.com/aqur1n-lab/aqur1n-tools/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg"/>
</a>
<a href="https://github.com/aqur1n-lab/aqur1n-tools/blob/main/atools/__init__.py">
    <img src="https://img.shields.io/badge/version-2022.2.25-green.svg"/>
</a>
<a href="https://github.com/aqur1n-lab/aqur1n-tools/blob/main/atools/__init__.py">
    <img src="https://img.shields.io/badge/python-3.5+-blue.svg"/>
</a>

# aqur1n-tools
Collection of modules for convenient work.

# Installation:
[pip](https://pypi.org/project/aqur1n-tools/#description):
```python
pip install aqur1n-tools
```

# Simple examples:
```python
from atools.basic import *
print(get_directory()) # Get the directory of the current file.
```
```python
from atools.path import Path

print(str(Path("exaples") + Path("test"))) # exaples\test
```
```python
from atools.sqlite3 import *

sql = sql("my name") # Initializes the class.
sql.connect("db\\my_db.db") # Connecting to db

sql.execute(f"CREATE TABLE IF NOT EXISTS my_table (test TEXT)", func=sql.commit) # Executes the query and calls the sql.commit function
```
You can see more on the wiki: [click](https://github.com/aqur1n-lab/aqur1n-tools/wiki)
