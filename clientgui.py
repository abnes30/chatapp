import socket
import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import simpledialog
from cryptography.fernet import Fernet

# Setup client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# Receive encryption key
key = client.recv(1024)
cipher_suite = Fernet(key)

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")

        # Nickname Entry
        self.nickname_window = Toplevel(root)
        self.nickname_window.title("Nickname")
        self.nickname_label = Label(self.nickname_window, text="Choose your nickname:")
        self.nickname_label.pack(padx=20, pady=5)
        self.nickname_entry = Entry(self.nickname_window)
        self.nickname_entry.pack(padx=20, pady=5)
        self.nickname_button = Button(self.nickname_window, text="Join", command=self.send_nickname)
        self.nickname_button.pack(padx=20, pady=5)

        # Main chat window
        self.chat_label = Label(self.root, text="Chat:")
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = ScrolledText(self.root)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = Label(self.root, text="Message:")
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = Text(self.root, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = Button(self.root, text="Send", command=self.write)
        self.send_button.pack(padx=20, pady=5)

        self.nickname = None

    def send_nickname(self):
        self.nickname = self.nickname_entry.get()
        if self.nickname:
            client.send(cipher_suite.encrypt(self.nickname.encode('ascii')))
            self.nickname_window.destroy()
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

    def receive(self):
        while True:
            try:
                message = cipher_suite.decrypt(client.recv(1024)).decode('ascii')
                self.text_area.config(state='normal')
                self.text_area.insert('end', message + '\n')
                self.text_area.config(state='disabled')
                self.text_area.yview('end')
            except:
                print("An error occurred!")
                client.close()
                break

    def write(self):
        message = self.input_area.get("1.0", 'end-1c')
        self.input_area.delete('1.0', 'end')
        if message.startswith("@"):
            try:
                recipient, private_message = message.split(" ", 2)[1:]
                client.send(cipher_suite.encrypt(f"@ {recipient} {private_message}".encode('ascii')))
                self.text_area.config(state='normal')
                self.text_area.insert('end', f"{self.nickname} (private to {recipient}): {private_message}\n")
                self.text_area.config(state='disabled')
                self.text_area.yview('end')
            except ValueError:
                print("Invalid format. Use @ <recipient> <message>")
        else:
            client.send(cipher_suite.encrypt(f"{self.nickname}: {message}".encode('ascii')))
            self.text_area.config(state='normal')
            self.text_area.insert('end', f"{self.nickname}: {message}\n")
            self.text_area.config(state='disabled')
            self.text_area.yview('end')

    def on_closing(self):
        client.close()
        self.root.quit()

if __name__ == "__main__":
    root = Tk()
    gui = ClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()
