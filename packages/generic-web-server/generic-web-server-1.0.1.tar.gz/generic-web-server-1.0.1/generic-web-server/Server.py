import socket
from datetime import datetime
from termcolor import colored
from Client import Client


class Server():
    """A class that represents a Server listening your Clients.
    ----------
    Attributes
    port : int
        represents the port used to bind. The default value is 5001
    address : str
        represents the address used to make requests. The default value is http://localhost

    max_connections : int
        represents the number of the max simultaneous connections on server

    timeout : int
        represents the inactivity time that the server will be online
    """

    def __init__(self, port = 5001, address = 'localhost', max_connections = 5, timeout = 20) -> None:
        print(colored('Generic Web Server - version 1.0', attrs=['bold']))
        self.port = port
        self.max_connections = max_connections
        self.address = address
        self.timeout = timeout
        self.is_ready = self.__create_socket()

    def run(self):
        """Starts the server if the socket was created successfully."""
        
        if self.is_ready is False:
            raise Exception('Server cannot be started. Please, check the attributes values inserted.')

        print(f'Started server on: http://{self.address}:{self.port}')
        print(f'Inactivity Timeout: {self.timeout} seconds\n-----------------------------------------------')
        start_time = datetime.now()

        try:
            while 1 > 0:
                connection, address  = self.server_socket.accept() #return socket and user address
                new_process = Client(connection, address) #creating new instance of Client class
                new_process.start() #start proccess with conection received   
        except:
            if(self.server_socket.timeout):
                print(colored('Timed out! Closing server...', 'red'))
            self.server_socket.close()
            end_time = datetime.now()
            print(f'Finished execution. Duration: {end_time - start_time}')


    def __create_socket(self) -> bool:
        try:
            print('Starting server...')
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.address, self.port))
            self.server_socket.listen(self.max_connections)
            self.server_socket.settimeout(self.timeout)
            return True
        except Exception as ex:
            print(f'Error during server initialization: {ex}') 
            return False
        