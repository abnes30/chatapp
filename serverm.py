import socket
import threading
from cryptography.fernet import Fernet

# Connection Data
host = '127.0.0.1'
port = 55555

# Encryption setup
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

# Sending Messages To Specific Client
def send_private_message(message, sender, recipient):
    if recipient in nicknames:
        recipient_client = clients[nicknames.index(recipient)]
        recipient_client.send(cipher_suite.encrypt(f"[{sender}] (private): {message}".encode('ascii')))
    else:
        sender_client = clients[nicknames.index(sender)]
        sender_client.send(cipher_suite.encrypt(f"User {recipient} not found.".encode('ascii')))

# Sending Messages To All Connected Clients
def broadcast(message, sender=None):
    for client in clients:
        if sender:
            if clients.index(client) != nicknames.index(sender):
                client.send(cipher_suite.encrypt(message))
        else:
            client.send(cipher_suite.encrypt(message))

# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = cipher_suite.decrypt(client.recv(1024)).decode('ascii')
            if message.startswith("@"):
                recipient, private_message = message.split(" ", 2)[1:]
                send_private_message(private_message, nicknames[clients.index(client)], recipient)
            else:
                broadcast(message.encode('ascii'), nicknames[clients.index(client)])
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left!'.encode('ascii'))
            nicknames.remove(nickname)
            break

# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Send encryption key
        client.send(key)

        # Request And Store Nickname
        nickname = cipher_suite.decrypt(client.recv(1024)).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast(f"{nickname} joined!".encode('ascii'))
        client.send(cipher_suite.encrypt('Connected to server!'.encode('ascii')))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()
