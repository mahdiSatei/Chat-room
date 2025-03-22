import socket
import threading

HOST = "127.0.0.1"
PORT = 15000
ADRR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADRR)
server.listen(5)

users = {}
online_users = {}

def load_users():
    users = {}
    try:
        with open("users.txt", 'r') as file:
            for line in file:
                username, password = line.split(":")
                users[username] = password
    except FileNotFoundError:
        pass
    
    return users

def save_users(username, password):
    with open("users.txt", 'a') as file:
        file.write(f"{username}:{password}\n")

def handle_client(client_socket):
    while True:
        try :
            message = client_socket.recv(1024).decode()
            if not message:
                break
            
            if message.startswith("Registration"):
                _, username, password = message.split(' ')
                if not password:
                    client_socket.send("Password can not be empty".encode())
                if username in users:
                    client_socket.send("User already exists.".encode())
                else:
                    users[username] = password
                    save_users(username, password)
                    client_socket.send("Succseefuly registred!".encode())
                client_socket.close()
                break
            
            elif message.startswith("Login"):
                _, username = message.split(' ')
                if username not in users:
                    client_socket.send("User not found.".encode())
                else:
                    if username in online_users:
                        old_socket, _ = online_users[username]
                        old_socket.send("You have been logged out.".encode())
                        old_socket.close()
                        del online_users[username]
                    client_socket.send("key 1".encode())
                    online_users[username] = (client_socket, "1")

            elif message.startswith("Hello"):
                username = is_logged_in(client_socket)
                if username in online_users and username:
                    broadcast(f"{username} joined the chat room.\r\n")
                    client_socket.send(f"Hi {username}, welcome to the chat room.".encode())
                else:
                    client_socket.send("Please login.".encode())

            elif message == "List":
                username = is_logged_in(client_socket)
                if username:
                    client_socket.send("Here is the list of attendees:\n\r".encode())
                    client_socket.send(",".join(online_users.keys()).encode())
                else:
                    client_socket.send("Please login first.".encode())

            elif message.startswith("Public"):
                username = is_logged_in(client_socket)
                if username:
                    message_body = client_socket.recv(1024).decode()
                    broadcast(f"Public message from {username}\r\n{message_body}")
                else:
                    client_socket.send("Please login first.".encode())
       
            elif message.startswith("Private"):
                username = is_logged_in(client_socket)
                if username:
                    recivers = message.split(' ')[2].split(',')       
                    message_body = client_socket.recv(1024).decode()
                    for reciver in recivers:
                        send_private_massage(client_socket, reciver, message_body, recivers)

            elif message.startswith("Bye"):
                username = is_logged_in(client_socket)
                if username:
                    broadcast(f"{username} left the chatroom.")
                    del online_users[username]
                    client_socket.send("You have left the chatroom.".encode())
                    client_socket.close()
                    break
                else:
                    client_socket.send("Please login first".encode())

            else:
                client_socket.send("Invalid option.".encode())
                
        except Exception as e:
            username = is_logged_in(client_socket)
            if username:
                print(f"User {username} disconnected unexpectedly: {e}")
                del online_users[username]
            client_socket.close()
            break

def broadcast(message):
    for user, (socket, _) in online_users.items():
        try:
            socket.send(message.encode())
        except:
            print(f"User {user} disconnected.")
            del online_users[user]
            socket.close()

def is_logged_in(client_socket):
    for username, (socket, _) in online_users.items():
        if socket == client_socket:
            return username
    return None

def send_private_massage(sender, reciver, message, recivers):
    sender_username = is_logged_in(sender)
    if reciver not in users:
        sender.send(f"User {reciver} dose not exist.".encode())
    elif reciver in online_users:
        reciver_socket = online_users[reciver][0]
        try:
            usernames = ",".join(recivers)
            reciver_socket.send(f"Private message from {sender_username} to {usernames}\r\n".encode())
            reciver_socket.send(f"{message}".encode())
        except:
            sender.send(f"Error: Could not send message to {reciver}.".encode())
    else:  
        sender.send(f"Error: User {reciver} is not online.".encode())    

def main():
    global users
    users = load_users()
    print("Server is running...")
    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr} established.")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()