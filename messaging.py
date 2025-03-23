from crypto import encrypt_message, decrypt_message

def broadcast(message, online_users):
    for user, (socket, key) in list(online_users.items()):
        try:
            encrypted_message = encrypt_message(key, message)
            socket.send(encrypted_message)
        except Exception as e:
            print(f"Error broadcasting to {user}: {e}")
            if user in online_users:
                del online_users[user]
                socket.close()

def send_private_message(sender, receiver, message, receivers, online_users, users):
    sender_username = None
    for username, (socket, _) in online_users.items():
        if socket == sender:
            sender_username = username
            break
    if not sender_username:
        return

    sender_key = online_users[sender_username][1]
    if receiver not in users:
        response = f"User {receiver} does not exist."
        sender.send(encrypt_message(sender_key, response))
    elif receiver in online_users:
        receiver_socket, receiver_key = online_users[receiver]
        try:
            usernames = ",".join(receivers)
            private_message = f"Private message from {sender_username} to {usernames}\r\n{message}"
            receiver_socket.send(encrypt_message(receiver_key, private_message))
        except Exception as e:
            response = f"Error: Could not send message to {receiver}. {str(e)}"
            sender.send(encrypt_message(sender_key, response))
    else:
        response = f"Error: User {receiver} is not online."
        sender.send(encrypt_message(sender_key, response))