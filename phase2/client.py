from socket import socket, AF_INET, SOCK_STREAM
from concurrent.futures import ThreadPoolExecutor as TPE
from threading import Thread
import pickle


class Client:
    WATCH_REQUEST_TYPES = {
        0: "COMMENT",
        1: "BORROW",
        2: "USER"
    }
    STATE = {
        0: "NOFRIEND",
        1: "CLOSEFRIEND",
        2: "FRIEND"
    }
    STATE_TYPE = {
        "CLOSED": 0,
        "CLOSEFRIEND": 1,
        "FRIEND": 2,
        "EVERYONE": 3
    }
    server_addr = '127.0.0.1'

    request_port = 21455
    notification_port = 12510
    meta_data = None
    is_login = False

    @classmethod
    def all_acts(cls):
        print('You can select the request that you want to make:  ')
        for act in cls.meta_data.keys():
            print(act, end='\n')

    @classmethod
    def request_handler(cls, request_sock, request_type):
        if request_type == 'verify':
            email = input("Email: ")
            verification_number = input("Verification number: ")
            params = (request_type, email, verification_number)
            params = pickle.dumps(params)
            request_sock.send(params)
            msg = request_sock.recv(1024)
            msg = pickle.loads(msg)
            if msg[0] == '+':
                Client.meta_data = {
                    'change password' : cls.request_handler,
                    'friend' : cls.request_handler,
                    'set friend': cls.request_handler,
                    'lookup' : cls.request_handler,
                    'list_items' : cls.request_handler,
                    'watch': cls.request_handler

                }
            print(msg[1])
        elif request_type == 'change password':
            old_password = input("Old Password (If you don't know your old password, skip it: ")
            new_password = input("New Password: ")
            if old_password == '':
                old_password = None
            params = ('change_password', new_password, old_password)
            params = pickle.dumps(params)
            request_sock.send(params)
            msg = request_sock.recv(1024)
            msg = pickle.loads(msg)
            print(msg)
        elif request_type == "lookup":
            email_list = input("Email List: ")
            params = (request_type, email_list)
            params = pickle.dumps(params)
            request_sock.send(params)
            msg = request_sock.recv(1024)
            msg = pickle.loads(msg)
            if msg:
                print(msg)
        elif request_type == 'list_items':
            email = input("which user's items would you like to see, Email:")
            params = (request_type, email)
            params = pickle.dumps(params)
            request_sock.send(params)
            msg = request_sock.recv(1024)
            msg = pickle.loads(msg)
            if msg:
                print(msg)
        elif request_type == 'friend':
            email = input("User's email who you want to send friendship request: ")
            params = ('friend', email)
            params = pickle.dumps(params)
            request_sock.send(params)
            msg = request_sock.recv(1024)
            msg = pickle.loads(msg)
            print(msg)
        elif request_type == 'set friend':
            email = input("User's email whose you want to set friendship state: ")
            state = input("NO FRIEND: 0, CLOSEFRIEND:1, FRIEND: 2  :")
            params = ('set_friend', email, cls.STATE[int(state)])
            params = pickle.dumps(params)
            request_sock.send(params)
            msg = request_sock.recv(1024)
            msg = pickle.loads(msg)
            print(msg)
        elif request_type == 'watch':
            email = input("User's email whose you want to watch: ")
            state = input("COMMENT: 0, BORROW:1, USER: 2  :")
            params = ('watch', email, cls.WATCH_REQUEST_TYPES[int(state)])
            params = pickle.dumps(params)
            request_sock.send(params)
            msg = request_sock.recv(1024)
            msg = pickle.loads(msg)
            print(msg)







    @classmethod
    def notification(cls, user_id):
        print('Notification Thread Started')
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((cls.server_addr, cls.notification_port))
        user_id = pickle.dumps(user_id)
        sock.send(user_id)
        while True:
            notification_msg = sock.recv(1024)
            if notification_msg == b'':
                print('Server closed')
                break
            if notification_msg == b'CLS':
                break
            notification_msg = pickle.loads(notification_msg)
            print(f'notification received: {notification_msg}')

    @classmethod
    def login(cls, request_sock, request_type):
        if not Client.is_login:
            email = input('Email: ')
            password = input("Password: ")

            params = ('login', email, password)
            print('login params', params)
            params = pickle.dumps(params)
            request_sock.send(params)

            msg = request_sock.recv(1024)
            print('recieved', pickle.loads(msg))

            # TODO
            # Check here
            if msg != b'':
                msg = pickle.loads(msg)
                print(msg[2])

                if msg[0] != '-':
                    notification_thread = Thread(target=cls.notification, args=(msg[1],))  # msh[0] is user_id
                    notification_thread.start()
                    cls.is_login = True
                    if msg[-1] == 0:
                        cls.meta_data = {
                            'verify': cls.request_handler,
                        }
                    else:
                        cls.meta_data = {
                            'change password' : cls.request_handler,
                            'friend' : cls.request_handler,
                            'set friend': cls.request_handler,
                            'lookup' : cls.request_handler,
                            'list_items' : cls.request_handler,
                            'watch': cls.request_handler

                        }

            else:
                print("there is an error")

    @classmethod
    def sign_up(cls, request_sock, request_type):
        name = input('Name: ')
        surname = input('Surname: ')
        email = input('Email: ')
        password = input('Password: ')

        params = ('sign_up', name, surname, email, password)
        params = pickle.dumps(params)
        request_sock.send(params)
        msg = request_sock.recv(1024)
        print(msg)
        msg = pickle.loads(msg)
        print(msg)


    @classmethod
    def connect(cls):
        request_socket = socket(AF_INET, SOCK_STREAM)
        request_socket.connect((cls.server_addr, cls.request_port))
        Client.meta_data = {
            'login': cls.login,
            'sign_up': cls.sign_up,
        }

        while True:
            cls.all_acts()
            request_type = input('\nRequest: ')
            if request_type in cls.meta_data:
                cls.meta_data[request_type](request_socket, request_type)


if __name__ == "__main__":
    client = Client()
    client.connect()
