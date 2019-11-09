import sqlite3


class DBConnection:

    def __init__(self, path='./data.db'):
        self.connection = sqlite3.connect(path)
        self.curs = self.connection.cursor()
        self.curs.execute("CREATE TABLE IF NOT EXISTS Users(" +
                          "id integer PRIMARY KEY," +
                          "name char[50]," +
                          "surname char[50]," +
                          "email char[256]," +
                          "password char[256]);")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Items(" +
                          "id integer PRIMARY KEY," +
                          "owner integer," +
                          "type char[150]," +
                          "title char[256]," +
                          "uniqueid integer UNIQUE" +
                          "artist char[256]," +
                          "genre char[150]," +
                          "year integer," +
                          "location char[256]," +
                          "rate integer" +
                          ");")

    def insert(self, table_name, *data):
        cur = self.connection.cursor()
        cur.execute(f'INSERT INTO {table_name} VALUES {"?,"*len(data)}', data)
        self.connection.commit()

    def update(self, table_name, updated_mem, filtered_mem, *data ):
        cur = self.connection.cursor()
        cur.execute(
            f'UPDATE {table_name} SET {updated_mem} = ?, WHERE {filtered_mem} = ?', data)
        self.connection.commit()



