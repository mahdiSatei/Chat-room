def load_users():
    users = {}
    try:
        with open("users.txt", 'r') as file:
            for line in file:
                username, password = line.strip().split(":")
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