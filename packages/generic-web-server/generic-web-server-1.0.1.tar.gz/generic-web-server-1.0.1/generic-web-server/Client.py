from datetime import datetime
from termcolor import colored
from threading import Thread

class Client(Thread):
    """A class that represents a Client conection, inheriting a thread of control.
    To execute this class, was necessary to overring the run() method.
    ----------
    Attributes
    socket_client : Socket
        represents the socket created by server. Contains basic informations about connection between client.
    ip_adress: Tuple
        represents the IP of the client.
    """

    def __init__(self,socket_client,ip_adress, encoding = 'utf-8'):
        Thread.__init__(self)
        self.methods = ["GET", "HEAD"]
        self.socket_client = socket_client
        self.ip_adress = ip_adress 
        self.encoding = encoding
        

    def run(self):#called when type Thread.start()
        self.socket_client.setblocking(True)
        while True:
            try:
                msg = self.socket_client.recv(2000)  
            except:
                break
            data = msg.decode().split(" ")
            resposta , arq = self.response(data) #retrives response body and resource
            self.socket_client.sendall(resposta.encode())
            if(arq!=None):
                self.socket_client.sendall(arq)       
            self.socket_client.close()
            
    def response(self,data):
        response = (self.response_builder('HTTP', '1.1', '405', 'Method Not Allowed'), None)
        if(data[0] in self.methods): #it's a allowed method
            if(data[0]=="GET"): #handle GET
                response = self.get(data[1:])

            elif(data[0]=="HEAD"): #handle HEAD
                response = self.head(data[1:],False) 
        else:
            print(self.request_builder_log(data[0], self.ip_adress[0], data[1], '405'))
            return response

        print(self.request_builder_log(data[0], data[1], self.ip_adress[0], response[0].split(' ')[1]))
        return response

    def get(self, dado):
        response, readFile = self.head(dado, True) #retrives request headers and requested resource
                                                    #True: that's means the server needs return the requested file
        
        if(readFile!=None): #check if path contains '/' on start
            diretorio = str.rpartition(dado[0], ".")#create list with path to file
            if(diretorio[2].find("html")==-1):
                return (response, readFile) #send response and requested file     
            else:
                response = response + readFile.decode("utf-8") 
                return (response, None) #send page in response body
        
        return (self.response_builder('HTTP', '1.1', '404', 'File not found'), None)


    
    def head(self, dado, flag):
        #returns headers and resource of request call
        directory = str.rpartition(dado[0], ".") #create list with path to file
        if(dado[0][0]=="/"): #check if path contains '/' on start
            if(len(dado[0])==1):#returns index.html from root path
                try:
                    read_file = open('index.html', 'rb').read()
                except:
                    return (response_builder('HTTP', '1.1', '404', 'File not found'), None)
            else: 
                try:
                    directory = str.rpartition(dado[0], ".")
                    read_file = open(directory[0][1:] + "." + directory[2], 'rb').read()
                except:
                    return (response_builder('HTTP', '1.1', '404', 'File not found'), None)

            if(read_file!=None):
                response = "HTTP/1.1 200 OK\r\n" + "Connection: close\r\n" + \
                    "Content Lenght:" + str(len(read_file)) + "\r\nContent Type:" + \
                        directory[1] + directory[2] + "\r\n\r\n"
                if flag:
                    return (response, read_file) #returning response and read file
                else:
                    return (response, None) #returning only response content
                
        return (self.response_builder('HTTP', '1.1', '404', 'File not found'), None)
    
    def response_builder(self, protocol, version, status_code, mesage):
        return f'{protocol}/{version} {status_code} - {mesage}\r\n\r\n'

    def request_builder_log(self, method_name, ip_address, path, status_code):
        color = 'green'
        if(int(status_code[0]) == 3):
            color = 'yellow'
        elif(int(status_code[0]) > 3):
            color = 'red'

        return colored(f'{datetime.now()} {method_name} {ip_address} {path} - {status_code}', color)
        
