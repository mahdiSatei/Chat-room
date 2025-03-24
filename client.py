import socket
import threading
from crypto import encrypt_message, decrypt_message

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

def receive_messages(client_socket, key, running):
    while running[0]:
        try:
            encrypted_message = client_socket.recv(4096)
            if not encrypted_message:
                print(f"{RED}🚫 Server disconnected.{RESET}")
                running[0] = False
                break
            message = decrypt_message(key, encrypted_message)
            if message:
                print(f"{CYAN}📩 {message}{RESET}")
                if "You have left the chatroom." in message or "EXIT" in message:
                    print(f"{YELLOW}👋 Exiting chat...{RESET}")
                    running[0] = False
                    break
        except Exception as e:
            print(f"{RED}⚠️ Connection error: {e}{RESET}")
            running[0] = False
            break

def show_help():
    print(f"{PURPLE}📋 Commands Menu:{RESET}")
    print(f"{GREEN}Registration [username] [password] 🌟 - Register a new user{RESET}")
    print(f"{GREEN}Login [username] 🔑 - Login with your username{RESET}")
    print(f"{GREEN}Hello 👋 - Join the chat room{RESET}")
    print(f"{GREEN}List 📜 - Show all online users{RESET}")
    print(f"{GREEN}Public 📢 - Send a public message{RESET}")
    print(f"{GREEN}Private to [user1,user2,...] 🤫 - Send a private message{RESET}")
    print(f"{GREEN}Bye 🚪 - Exit the chat{RESET}")
    print(f"{GREEN}Help ❓ - Show this menu{RESET}")

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 15000))
        print(f"{GREEN}✅ Connected to the server.{RESET}")
        
        key = client.recv(32)
        print(f"{BLUE}🔒 Secure connection established.{RESET}")
        
        running = [True]
        receive_thread = threading.Thread(target=receive_messages, args=(client, key, running))
        receive_thread.daemon = True
        receive_thread.start()
        
        show_help()
        
        while running[0]:
            user_input = input()
            try:
                if user_input == "Help":
                    show_help()
                elif user_input.startswith("Public") or user_input.startswith("Private"):
                    client.send(encrypt_message(key, user_input))
                    message_body = input(f"{BLUE}💬 Enter your message: {RESET}")
                    client.send(encrypt_message(key, message_body))
                else:
                    client.send(encrypt_message(key, user_input))
                if user_input == "Bye":
                    print(f"{YELLOW}👋 Disconnecting...{RESET}")
                    running[0] = False
                    break
            except Exception as e:
                print(f"{RED}❌ Failed to send message: {e}{RESET}")
                running[0] = False
                break
    
    except Exception as e:
        print(f"{RED}⚠️ Error: {e}{RESET}")
    
    finally:
        try:
            client.close()
            print(f"{GREEN}🔌 Connection closed.{RESET}")
        except:
            pass

if __name__ == "__main__":
    main()