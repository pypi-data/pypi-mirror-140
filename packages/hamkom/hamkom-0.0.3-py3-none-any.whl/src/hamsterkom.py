import socket 
import threading
import time as t
import msgpack
import random
import sys
import time

PORT = 5050
SERVER = "0.0.0.0"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!D"
FORWARD_MESSAGE = "!F"
TURN_MESSAGE = "!T"


def move_forward():
    t.sleep(2)
    print("moving forward")
#    pass
def turn():
    t.sleep(2)
    print("turning")

def maschinerie(conn, addr):
    serving = True
    while serving:
        msg = None
        try:
            msg = conn.recv(4096).decode(FORMAT)
        except Exception:
            print("[{}]: Connection Lost!".format(addr))
            break
            #conn.close()
            #need reconnect -> break out of maschinerie
        if msg == None:
            print("[{}]: Connection Problem?".format(addr))
            t.sleep(2)
            #break
            #conn.close()
            #connecting, 
        elif msg == DISCONNECT_MESSAGE:
            print("[{}]: Disconnected".format(addr))
            break
            #out of maschinerie to allow reconnect
        else:
            if msg == FORWARD_MESSAGE: 
                move_forward()
                print("forward message recieved")
                print("eppas got (it)")
                answer = FORWARD_MESSAGE.encode(FORMAT)
                try: conn.send(answer)
                except ConnectionResetError:
                    print("cheffe dced, breaking out of maschinerie for reconnect")
                    break
            if msg == TURN_MESSAGE: 
                turn()
                print("turn message recieved")
                print("eppas got ")
                answer = TURN_MESSAGE.encode(FORMAT)
                try: conn.send(answer)
                except ConnectionResetError:
                    print("cheffe dced, breaking out of maschinerie for reconnect")
                    break
            
            
            #packer = msgpack.Packer()
            #conn.sendall(packer.pack(message))        
    conn.close()



if __name__ == "__main__":
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()

    print("Radls Motorhamster lafft an!")
    #print("Da Server horcht auf alle IPs: {}".format(SERVER))
    try: 
        while True:
            conn, addr = server.accept()
            maschinerie(conn, addr)

    finally:
        print("clean!")
