import socket
import threading
from incl.utils import *
from incl.protocols import *

clients = []
unames = {}

def handle_client(client_socket):
    while True:
        try:    
            msg = client_socket.recv(1024)

            if not msg:
                remove_client(client_socket)
                break
        
            recv_msg_protocol = msg[0:1]

            if recv_msg_protocol == msg_protocol:
                recv_msg_bytes_len = int.from_bytes(msg[1:3], "big")
                decoded_msg = msg[3:3+recv_msg_bytes_len].decode("utf-8").strip()
                decoded_msg_len = len(decoded_msg) 
                if  1 <= decoded_msg_len <= 256:
                    send_message(decoded_msg, client_socket)
                
            elif recv_msg_protocol == join_protocol:
                uname_length = int.from_bytes(msg[1:3], "big")
                uname = msg[3:3+uname_length].decode("utf-8").strip()
                unames[client_socket] = uname

                send_message(f"{uname} joined the chat room!")
            elif recv_msg_protocol == disconnect_protocol:
                remove_client(client_socket)
                break
        except:
            remove_client(client_socket)
            break

def remove_client(client_socket):
    if client_socket in clients:
        uname = unames.get(client_socket, "Unknown")

        clients.remove(client_socket)
        del unames[client_socket]

        send_message(f"{uname} left the room!")
    client_socket.close()

def send_message(msg = "", sender_socket=None):
    for c in clients.copy():
        if sender_socket is None: # if its a server message
            formatted_msg = f"[Server]: {msg}"
            
            c.send(formatted_msg.encode("utf-8"))
            print(formatted_msg)
        elif c != sender_socket:
            try:
                sender_uname = unames[sender_socket]
                formatted_msg = f"{sender_uname}: {msg}"

                c.send(formatted_msg.encode("utf-8"))
                print(formatted_msg)
            except:
                remove_client(c)

server_ip = get_lan_ip()
server_port = 9999 # <--- SERVER PORT

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((server_ip, server_port))
server.listen()

while True:
    client_socket, addr = server.accept()

    clients.append(client_socket)

    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()