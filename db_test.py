import sqlite3

connection = sqlite3.connect("bangla_dictionary.db")
cursor = connection.cursor()
val = 100
ch = 'ক'
values = [100,'ক']
#cursor.execute("update alphabet set count=? where character=?", values)
#cursor.execute("delete from alphabet where character='100'")
cursor.execute("select *from alphabet")
print(cursor.fetchall())
connection.close()
