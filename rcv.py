import numpy as np
import socket
import struct

class Server:
    def __init__(self,host,port):
        self.host=host
        self.port=port

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print("Server listening on port ", self.port)
            while True:
                conn,addr=s.accept()
                with conn:
                    print("Connessione instaurata col clinet ",addr)
                    received_data = b''
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        received_data += data

                    float_data =[]
                    for i in range(0,len(received_data),4):
                        #print(data)
                        
                        if(i+4 <= len(received_data)):
                            unpacked_data = struct.unpack('f' ,received_data[i:i+4])
                        else:
                            unpacked_data = struct.unpack('f' ,received_data[i:len(received_data)])
                        
                        float_data.append(unpacked_data)
                    
                    print("Data received: ", float_data)
                    print("len: ", len(float_data))

                    
                    

s=Server("127.0.0.1",port=65435)
s.receive()                
                    