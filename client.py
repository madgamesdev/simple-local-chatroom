import socket
import threading
import sys
from incl.utils import *
from incl.protocols import *

def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode("utf-8")
            if not msg:
                print("\nServer closed connection")
                break

            sys.stdout.write("\r" + " " * 100 + "\r")

            print(msg)

            sys.stdout.write("> ")
            sys.stdout.flush()
        except:
            break

def enter_server_port():
    while True:
        try:
            port = int(input("Enter server port (default: 9999)") or 9999)
            if 0 < port < 65536:
                break
            else:
                print("Port must be between 1 and 65535")
        except ValueError:
            print("Invalid port number")
    return port

def enter_uname():
    print("Enter a username (3-18 chars)")
    uname = input()
    if (3 <= len(uname) <= 18):
        return uname
    return enter_uname()

server_ip = get_lan_ip()
server_port = enter_server_port()
uname = enter_uname()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    

thread = threading.Thread(target=receive_messages, 
                          args=(client_socket,), 
                          daemon=True
                          )

client_socket.connect((server_ip, server_port))
thread.start()

uname_bytes = uname.encode("utf-8")
client_socket.send(join_protocol + len(uname_bytes).to_bytes(2, "big") + uname_bytes)

try:
    while True:
        msg = input()

        if 1 <= len(msg) <= 256:
            msg_bytes = msg.encode("utf-8")
            client_socket.send(msg_protocol + len(msg_bytes).to_bytes(2, "big") + msg_bytes)
except KeyboardInterrupt:
    print("Quitting...")
    client_socket.send(disconnect_protocol)
finally:
    client_socket.close()