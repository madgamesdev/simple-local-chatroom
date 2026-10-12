import socket
import threading
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from incl.utils import *
from incl.protocols import *

def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024)
            if not msg:
                break

            msg = msg.decode("utf-8")
            with patch_stdout():
                print(msg)

        except (OSError, UnicodeDecodeError):
            break

def enter_server_ip():
    while True:
        server_ip = input("Enter server IP (default: local machine): ").strip()
        if not server_ip:
            return get_lan_ip()

        try:
            socket.inet_pton(socket.AF_INET, server_ip) # check ip
            return server_ip
        except OSError:
            print("Invalid IPv4 address")

def enter_server_port():
    while True:
        try:
            port = int(input("Enter server port (default: 9999): ") or 9999)
            if 0 < port < 65536:
                break
            else:
                print("Port must be between 1 and 65535")
        except ValueError:
            print("Invalid port number")
    return port

def enter_uname():
    print("Enter a username (3-18 chars): ")
    uname = input()
    if (3 <= len(uname) <= 18):
        return uname
    return enter_uname()

server_ip = enter_server_ip()
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
client_socket.sendall(join_protocol + len(uname_bytes).to_bytes(2, "big") + uname_bytes)
session = PromptSession()

try:
    while patch_stdout():
        while True:
            msg = session.prompt("> ")

            if 1 <= len(msg) <= 256:
                msg_bytes = msg.encode("utf-8")
                client_socket.sendall(
                    msg_protocol +
                    len(msg_bytes).to_bytes(2, "big") +
                    msg_bytes
                    )
                
except KeyboardInterrupt:
    print("Quitting...")
    client_socket.sendall(disconnect_protocol)
finally:
    client_socket.close()