import sqlite3


class DBConnection:

    def __init__(self, path='./data.db'):
        self.connection = sqlite3.connect(path)
        self.curs = self.connection.cursor()
        self.curs.execute("DROP TABLE IF EXISTS Users;")
        self.curs.execute("DROP TABLE IF EXISTS Items;")
        self.curs.execute("DROP TABLE IF EXISTS Borrows;")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Users("
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "name char(50)," +
                          "surname char(50)," +
                          "email char(256) UNIQUE," +
                          "password char(256)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Items(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "owner integer," +
                          "type char(150)," +
                          "title char(256)," +
                          "uniqueid integer UNIQUE," +
                          "artist char(256)," +
                          "genre char(150)," +
                          "year integer," +
                          "location char(256)," +
                          "rate integer,"
                          "FOREIGN KEY (owner) REFERENCES Users(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Friends(" +
                          "user_id1 integer," +
                          "user_id2  integer," +
                          "state integer ," +
                          "is_verified integer," +
                          "PRIMARY KEY(user_id1, user_id2)," +
                          "FOREIGN KEY (user_id1) REFERENCES Users(id)," +
                          "FOREIGN KEY (user_id2) REFERENCES Users(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Comments(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "user_id  integer," +
                          "item_id integer ," +
                          "FOREIGN KEY (user_id) REFERENCES Users(id)," +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS StateItem(" +
                          "item_id integer PRIMARY KEY," +
                          "view integer ," +
                          "detail integer ," +
                          "borrow integer ," +
                          "comment integer ," +
                          "search integer ," +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Requests(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "user_id integer," +
                          "item_id integer ," +
                          "request_datetime text ," +
                          "type integer," +
                          "FOREIGN KEY (user_id) REFERENCES Users(id)," +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Borrows(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "user_id integer," +
                          "item_id integer ," +
                          "taking_date text," +
                          "return_date text," +
                          "is_returned integer," +
                          "FOREIGN KEY (user_id) REFERENCES Users(id)," +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.connection.commit()

    def insert(self, table_name, *data):
        cur = self.connection.cursor()
        print(data)
        f_string = f'INSERT INTO {table_name} VALUES ( {"?,"*(len(data)-1) + "?"} )'
        cur.execute(f_string, data)
        self.connection.commit()

    def update(self, table_name, updated_mem, filtered_mem, *data ):
        cur = self.connection.cursor()
        f_string = f'UPDATE {table_name} SET {updated_mem} = ? WHERE {filtered_mem} = ?'
        cur.execute(
            f'UPDATE {table_name} SET {updated_mem} = ? WHERE {filtered_mem} = ?;', data)
        self.connection.commit()


#
# db = DBConnection()
# db.insert("Users", None, "beste", "burhan", "email", "password")
# db.update("Users", "name", "name", "beste", "beste")