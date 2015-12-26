import sqlite3
from _config import DATABASE_PATH

with sqlite3.connect(DATABASE_PATH) as connection:
    # get a curspr object to execute SQL commands
    c = connection.cursor()

    # create the table
    c.execute("""CREATE TABLE tasks(task_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, due_date TEXT NOT NULL, priority INTEGER NOT NULL, status INTEGER NOT NULL)""")
    # insert dummy data into table
    c.execute('INSERT INTO tasks(name, due_date, priority, status)'
              'values("Finish tutorial", "03/25/2015", 10, 1)')
    c.execute('INSERT INTO tasks(name, due_date, priority, status)'
              'values("Finish Real Python - 2 cource", "03/25/2015", 10, 1)')
