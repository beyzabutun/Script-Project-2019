from socket import socket, AF_INET, SOCK_STREAM
from concurrent.futures import ThreadPoolExecutor as TPE
from threading import Thread
import pickle


class Client:
    server_addr = '127.0.0.1'

    request_port = 20454
    notification_port = 19214
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

                }
            print(msg[1])




    @classmethod
    def notification(cls, user_id):
        print('Notification Thread Started')
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((cls.server_addr, cls.notification_port))
        user_id = pickle.dumps(user_id)
        sock.send(user_id)
        while True:
            notification_msg = sock.recv(1024)
            notification_msg = pickle.loads(notification_msg)
            if notification_msg == b'':
                print('Server closed')
                break
            if notification_msg == b'CLS':
                break
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
                    cls.meta_data = {
                        'verify': cls.request_handler,
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
