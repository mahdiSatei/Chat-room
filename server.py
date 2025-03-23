import socket
import threading
import os
from crypto import encrypt_message, decrypt_message

HOST = "127.0.0.1"
PORT = 15000
ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(5)

users = {}
online_users = {}

def handle_client(client_socket):
    key = os.urandom(32)
    try:
        client_socket.send(key)
        while True:
            encrypted_message = client_socket.recv(4096)
            if not encrypted_message:
                break
            message = decrypt_message(key, encrypted_message)
            if not message:
                continue

            if message.startswith("Registration"):
                _, username, password = message.split(' ')
                if not password:
                    response = "Password can not be empty"
                elif username in users:
                    response = "User already exists."
                else:
                    users[username] = password
                    save_users(username, password)
                    response = "Successfully registered!"
                client_socket.send(encrypt_message(key, response))
                client_socket.close()
                break

            elif message.startswith("Login"):
                _, username = message.split(' ')
                if username not in users:
                    response = "User not found."
                else:
                    if username in online_users:
                        old_socket, old_key = online_users[username]
                        old_socket.send(encrypt_message(old_key, "You have been logged out."))
                        old_socket.close()
                        del online_users[username]
                    session_key = key.hex()[:10] + "..."  
                    response = f"Login successful\r\nKey {session_key}"
                    online_users[username] = (client_socket, key)
                client_socket.send(encrypt_message(key, response))

            elif message.startswith("Hello"):
                username = is_logged_in(client_socket, online_users)
                if username:
                    broadcast(f"{username} joined the chat room.", online_users)
                    response = f"Hi {username}, welcome to the chat room."
                else:
                    response = "Please login."
                client_socket.send(encrypt_message(key, response))

            elif message == "List":
                username = is_logged_in(client_socket, online_users)
                if username:
                    response = "Here is the list of attendees:\n" + ",".join(online_users.keys())
                else:
                    response = "Please login first."
                client_socket.send(encrypt_message(key, response))

            elif message.startswith("Public"):
                username = is_logged_in(client_socket, online_users)
                if username:
                    encrypted_body = client_socket.recv(4096)
                    message_body = decrypt_message(key, encrypted_body)
                    if message_body:
                        broadcast(f"Public message from {username}\r\n{message_body}", online_users)
                    else:
                        response = "Message can not be empty"
                        client_socket.send(encrypt_message(key, response))
                else:
                    response = "Please login first."
                    client_socket.send(encrypt_message(key, response))

            elif message.startswith("Private"):
                username = is_logged_in(client_socket, online_users)
                if username:
                    parts = message.split(' ')
                    if len(parts) >= 3:
                        receivers = parts[2].split(',')
                        print(receivers)
                        encrypted_body = client_socket.recv(4096)
                        message_body = decrypt_message(key, encrypted_body)
                        if message_body:
                            for receiver in receivers:
                                send_private_message(client_socket, receiver, message_body, receivers, online_users, users)
                        else:
                            response = "Message can not be empty"
                            client_socket.send(encrypt_message(key, response))
                    else:
                        response = "Invalid command format. Use: Private to user1,user2,..."
                        client_socket.send(encrypt_message(key, response))
                else:
                    response = "Please login first."
                    client_socket.send(encrypt_message(key, response))

            elif message.startswith("Bye"):
                username = is_logged_in(client_socket, online_users)
                if username:
                    broadcast(f"{username} left the chatroom.", online_users)
                    del online_users[username]
                    response = "You have left the chatroom."
                    client_socket.send(encrypt_message(key, response))
                    client_socket.close()
                    break
                else:
                    response = "Please login first"
                    client_socket.send(encrypt_message(key, response))

            else:
                response = "Invalid option."
                client_socket.send(encrypt_message(key, response))

    except Exception as e:
        username = is_logged_in(client_socket, online_users)
        if username:
            print(f"User {username} disconnected unexpectedly: {e}")
            if username in online_users:
                del online_users[username]
        client_socket.close()


def broadcast(message):
    for user, (socket, _) in online_users.items():
        try:
            socket.send(message.encode())
        except:
            print(f"User {user} disconnected.")
            del online_users[user]
            socket.close()

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

def is_logged_in(client_socket, online_users):
    for username, (socket, _) in online_users.items():
        if socket == client_socket:
            return username
    return None

def send_private_message(sender, reciver, message, recivers):
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