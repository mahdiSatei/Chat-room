import socket
import threading

HOST = "127.0.0.1"
PORT = 15000
ADRR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADRR)
server.listen(5)

users = {}
onlinUsers = {}

def handle_client(client_socket):
    while True:
        try :
            message = client_socket.recv(1024).decode()
            if not message:
                break
            
            if message.startswith("R"):
                _, username, password = message.split(' ')
                if username in users:
                    client_socket.send("User already exists.".encode())
                else:
                    users[username] = password
                    client_socket.send("Succseefuly registred!".encode())
            
            if message.startswith("L"):
                _, username = message.split(' ')
                if username in users:
                    client_socket.send("Key 1".encode())
                    onlinUsers[username] = (client_socket, "1")
                else:
                    client_socket.send("User not found.".encode())

            if message.startswith("H"):
                _, username = message.split(' ')
                if username in onlinUsers and username in users:
                    broadcast(f"{username} joined the chat room.")
                    client_socket.send(f"\nHi {username}, welcome to the chat room.".encode())
                else:
                    client_socket.send("Please login.".encode())

            if message == "list":
                client_socket.send("Here is the list of attendees:\n\r".encode())
                client_socket.send(",".join(onlinUsers.keys()).encode())
                
                                       
        except Exception as e:
            print(e)

def broadcast(message):
    for user, (socket, _) in onlinUsers.items():
        try:
            socket.send(message.encode())
        except:
            print(f"User {user} disconnected.")
            del onlinUsers[user]
            socket.close()

while True:
    client_socket, addr = server.accept()
    print(f"Connection from {addr} established.")
    # clients.append(client_socket)
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()