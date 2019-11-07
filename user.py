
class User():

    db_conn = None

    def __init__(self, email, name, surname, password):
        assert self.db_conn
        self.email = email
        self.name = name
        self.surname = surname
        self.password = password

        self.db_conn.insert("Users", (email, name, surname, password) )

    @staticmethod
    def verify(self, email, verification_number):
        pass

    def change_password(self, new_password, old_password = None):
        if old_password != None:

            self.password = new_password
            self.db_conn.update("Users", "password", "email", (new_password, self.email))

        #if none generate a temporal password

    def look_up(self, email_list):

        cur = self.db_conn.cursor()
        cur.execute("select email from Users u where u.email in ?", (email_list,))
        fetched = curr.fetchall()
        if not fetched:
            return "There are no email from the email_list in the database"
        self.db_conn.commit()
        return fetched

    def friend(self, email):
        pass

    def set_friend(self, user, state):
        pass

    def list_items(self, user):
        pass

    def watch(self, user, watch_method):
        pass

