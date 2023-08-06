# serializeDB

serializeDB is

* a lightweight key-value database based on serialization



## Quickstart

```python
import json
import serializedb

db = serializeDB.load('test.db', serializer=json, auto_dump=False)

db['key'] = 'value'

db.dump()
```



### Install serializeDB

```python
$ pip install serializeDB
```
