
class User():

    def __init__(self, email, name, surname, password):
        self.email = email
        self.name = name
        self.surname = surname
        self.password = password

    @staticmethod
    def verify(self, email, verification_number):
        pass

    def change_password(self, new_password, old_password = None):
        pass

    def look_up(self, email_list):
        pass

    def friend(self, email):
        pass

    def set_friend(self, user, state):
        pass

    def list_items(self, user):
        pass

    def watch(self, user, watch_method):
        pass

