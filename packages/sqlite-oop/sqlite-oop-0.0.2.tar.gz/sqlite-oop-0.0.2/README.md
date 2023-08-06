# sqlite oop

### sqlite Object Oriented

```python
from sqliteoop import sqlite
db = sqlite("./demo.db")

# create table
createtable = db.table("user_name").create_table({
    "id":"INTEGER PRIMARY KEY AUTOINCREMENT",
    "name":"VARCHAR(80) NOT NULL"
})
print(createtable)

# create datas
insert = db.table("user_name").insert([{"name": "davie"}, {"name": "johan"}])

# create data
insert = db.table("user_name").create({"name": "davie"})

# delete
db.table("user_name").where("id",1).delete()
db.table("user_name").where("name","davie").delete()

# update
db.table("user_name").where("name","davie").updata({"name":"lisa"})

# select
db.table("user_name").where("name","<>","davie").limit(5).select("*")

# find
db.table("user_name").where("name","johan").find("*")

```
