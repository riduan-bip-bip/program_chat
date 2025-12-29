import socket
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import datetime

class ChatClientGUI:
    def __init__(self, root, client_id):
        self.root = root
        self.root.title(f"Chat Client - {client_id}")
        self.client_id = client_id

        self.text_area = scrolledtext.ScrolledText(root, height=20, width=70)
        self.text_area.pack(pady=10)

        tk.Label(root, text="Kepada (ID):").pack(side=tk.LEFT, padx=5)
        self.target_entry = tk.Entry(root, width=20)
        self.target_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(root, text="Pesan:").pack(side=tk.LEFT, padx=5)
        self.message_entry = tk.Entry(root, width=40)
        self.message_entry.pack(side=tk.LEFT, padx=5)

        self.send_button = tk.Button(root, text="Kirim", command=self.send_message)
        self.send_button.pack(pady=5)

        self.connect_button = tk.Button(root, text="Connect to Server", command=self.connect_to_server)
        self.connect_button.pack(pady=5)

        self.client_socket = None
        self.running = False
        self.client_log = f"{client_id}_log.txt"

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_entry = f"{timestamp} {message}\n"

        with open(self.client_log, "a") as file:
            file.write(log_entry)

        self.text_area.insert(tk.END, log_entry)
        self.text_area.see(tk.END)

    def receive_messages(self):
        """Menerima pesan dari server."""
        while self.running:
            try:
                target_id = self.target_entry.get().strip()
                data = self.client_socket.recv(1024).decode('ascii')
                if not data:
                    self.running = False
                    break
                self.log_message(f"{data} ")
            except:
                self.running = False
                break

    def send_message(self, event=None):
        """Mengirim pesan privat ke server."""
        target_id = self.target_entry.get().strip()
        message = self.message_entry.get().strip()

        if target_id and message and self.client_socket:
            full_message = f"TO:{target_id}:{message}"

            start_time = time.time()
            self.client_socket.send(full_message.encode('ascii'))
            end_time = time.time()

            ascii_codes = [ord(c) for c in message]
            rtt = (end_time - start_time) * 1000

            self.log_message(
                f"Terikirim ke {target_id}: {message} (ASCII: {ascii_codes}, RTT: {rtt:.2f} ms)"
            )

            self.message_entry.delete(0, tk.END)

        

    def connect_to_server(self, host="127.0.0.1", port=12345):
        """Menghubungkan ke server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.client_socket.send(self.client_id.encode('ascii'))

            self.log_message(f"Terhubung ke {host}:{port}")

            self.connect_button.config(state="disabled")

            self.running = True
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.log_message(f"Error koneksi: {e}")

if __name__ == "__main__":
    print("=== Chat Client Lokal (Private Messaging) ===")
    client_id = input("Masukkan ID client (misalnya, Client1): ")
    root = tk.Tk()
    app = ChatClientGUI(root, client_id)
    root.mainloop()
