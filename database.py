import sqlite3


class DBConnection:

    def __init__(self, path='./data.db'):
        self.connection = sqlite3.connect(path)
        self.curs = self.connection.cursor()
        self.curs.execute("DROP TABLE IF EXISTS Users;")
        self.curs.execute("DROP TABLE IF EXISTS Items;")
        self.curs.execute("DROP TABLE IF EXISTS Borrows;")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Users(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "name char(50)," +
                          "surname char(50)," +
                          "email char(256) UNIQUE," +
                          "password char(256)," +
                          "is_verified integer," +
                          "verification_number char(50)" +
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
                          "view integer ," +
                          "detail integer ," +
                          "borrow integer ," +
                          "comment integer ," +
                          "search integer ," +
                          "FOREIGN KEY (owner) REFERENCES Users(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Friends(" +
                          "sender_user integer," +
                          "receiver_user integer," +
                          "state integer ," +
                          "PRIMARY KEY(sender_user, receiver_user)," +
                          "FOREIGN KEY (sender_user) REFERENCES Users(id)," +
                          "FOREIGN KEY (receiver_user) REFERENCES Users(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Comments(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "user_id  integer," +
                          "item_id integer ," +
                          "comment text," +
                          "date text," +
                          "FOREIGN KEY (user_id) REFERENCES Users(id)," +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Announcements(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "item_id integer ," +
                          "friend_state integer ," +
                          "msg text, " +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS WatchRequests(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "user_id integer," +
                          "item_id integer ," +
                          "watch_method integer ," +
                          "followed_id integer," +
                          "FOREIGN KEY (user_id) REFERENCES Users(id)," +
                          "FOREIGN KEY (followed_id) REFERENCES Users(id), " +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS Borrows(" +
                          "id integer PRIMARY KEY AUTOINCREMENT," +
                          "user_id integer," +
                          "item_id integer ," +
                          "taking_date text," +
                          "return_date text," +
                          "rate text," +
                          "is_returned integer," +
                          "FOREIGN KEY (user_id) REFERENCES Users(id)," +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.curs.execute("CREATE TABLE IF NOT EXISTS BorrowRequests(" +
                          "user_id integer," +
                          "item_id integer ," +
                          "request_date text," +
                          "PRIMARY KEY(user_id, item_id)," +
                          "FOREIGN KEY (user_id) REFERENCES Users(id)," +
                          "FOREIGN KEY (item_id) REFERENCES Items(id)" +
                          ");")
        self.connection.commit()

    def get_cursor(self):
        return self.connection.cursor()

    def insert(self, table_name, field_names, *data):
        cur = self.connection.cursor()
        f_string = f'INSERT INTO {table_name} {field_names} VALUES ( {"?,"*(len(data)-1) + "?"} )'
        cur.execute(f_string, data)
        self.connection.commit()

    def update(self, table_name, updated_mem, filtered_mem, *data ):
        cur = self.connection.cursor()
        f_string = f'UPDATE {table_name} SET {updated_mem} = ? WHERE {filtered_mem} = ?'
        cur.execute(
            f'UPDATE {table_name} SET {updated_mem} = ? WHERE {filtered_mem} = ?;', data)
        self.connection.commit()


#
db = DBConnection()
#db.insert("Users", ('name', 'surname', 'email', 'password'), "beste", "burhan", "email", "password")
# db.update("Users", "name", "name", "beste", "beste")