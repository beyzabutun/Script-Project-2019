import database as db

class User():

    STATE_TYPE = (
        (0, "CLOSED"),
        (1, "FRIEND"),
        (2, "CLOSEFRIEND"),
        (3, "EVERYONE")
    )

    db_conn = db.DBConnection()


    def __init__(self, name, surname, email, password):
        assert self.db_conn
        self.cur = self.db_conn.curs
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password

        self.db_conn.insert("Users", None, name, surname, email, password)
        user = self.cur.execute('select u.id from Users u where u.email = \'{uemail}\''.format(uemail=self.email))
        id = user.fetchone()
        self.id = id[0]

    @staticmethod
    def verify(self, email, verification_number):
        pass

    def change_password(self, new_password, old_password = None):
        if old_password != None:

            self.password = new_password
            self.db_conn.update("Users", "password", "email", (new_password, self.email))

        #if none generate a temporal password

    def look_up(self, email_list):

        fetched_mails = self.cur.execute('select email from Users u where u.email in {elist}'.format(elist = email_list))
        fetched_mails = fetched_mails.fetchall()
        if not fetched_mails:
            return "There are no email from the email_list in the database"
        result = []
        for mail in fetched_mails:
            result.append(mail[0])
        self.db_conn.connection.commit()
        return result

    def friend(self, email):

        user2 = self.cur.execute('select u.id from Users u where u.email like \'{uemail}\''.format(uemail=email))
        user2_id = user2.fetchone()
        self.db_conn.insert("Friends", self.id, int(user2_id[0]), self.STATE_TYPE[0][0], 0)
        self.db_conn.connection.commit()

    def set_friend(self, user, state):
        self.cur.execute(
            'update Friends set state = {fstate}, is_verified = 1 where (user_id1 = {fuserid1} and user_id2 = {fuserid2}) or (user_id1 = {fuserid2} and user_id2 = {fuserid1})'
            .format(fstate=state, fuserid1=self.id, fuserid2=user.id))
        self.db_conn.connection.commit()

    def list_items(self, user):
        pass

    def watch(self, user, watch_method):
        pass


user_obj = User("ahmet", "namik", "ahmetmetuedutr", "232552")
user_obj2 = User("ahmet", "kemal", "kemal@metu.edu.tr", "232555552")
user_obj.friend("kemal@metu.edu.tr")
print(user_obj.look_up(("kemal@metu.edu.tr", "beyzaaa@mit.com", "beste@standord.com","ahmetmetuedutr")))
user_obj.set_friend(user_obj2, 1)


