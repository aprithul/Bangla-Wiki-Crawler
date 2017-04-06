import sqlite3
from datetime import datetime, date
connection = sqlite3.connect("bangla_dictionary.db")
cursor = connection.cursor()
val = 100
ch = 'ক'
values = [100,'ক']
#digests = cursor.execute("select * from history")
cursor.execute("insert into history (digest,time) values (?,?)", ["slkfjsdlskdfjslfkjsldkfj", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
connection.commit()
connection.close()
