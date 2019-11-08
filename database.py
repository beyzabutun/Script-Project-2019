import sqlite3

class DBConnection:

    def __init__(self, path = './data.db'):
        self.connection = sqlite3.connect(path)

    def insert(self, table_name, *data):
        cur = self.connection.cursor()
        cur.execute(f'INSERT INTO {table_name} VALUES {"?,"*len(data)}', data)
        self.connection.commit()

    def update(self, table_name, updated_mem, filtered_mem, *data ):
        cur = self.connection.cursor()
        cur.execute(
            f'UPDATE {table_name} SET {updated_mem} = ?, WHERE {filtered_mem} = ?', data)
        self.connection.commit()



