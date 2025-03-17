import socket
import threading
from cryptography.fernet import Fernet

# Choosing Nickname
nickname = input("Choose your nickname: ")  # Ask immediately

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# Receive encryption key
key = client.recv(1024)
cipher_suite = Fernet(key)

# Send the nickname immediately after connecting
client.send(cipher_suite.encrypt(nickname.encode('ascii')))

# Listening to Server and Sending Messages
def receive():
    while True:
        try:
            message = cipher_suite.decrypt(client.recv(1024)).decode('ascii')
            print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    while True:
        message = input("")
        if message.startswith("@"):
            try:
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    print("Invalid format. Use: @ <recipient> <message>")
                    continue
                recipient, private_message = parts[1], parts[2]
                client.send(cipher_suite.encrypt(f"@ {recipient} {private_message}".encode('ascii')))
            except Exception as e:
                print("Error sending private message:", e)
        else:
            client.send(cipher_suite.encrypt(f"{nickname}: {message}".encode('ascii')))

# Start Threads
receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()
