import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import time
import datetime

class ChatServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Server - Teroptimasi (Dictionary)")

        self.server_socket = None
        # Dictionary
        self.clients = {}  
        self.client_lock = threading.Lock()

        self.text_area = scrolledtext.ScrolledText(root, height=20, width=70)
        self.text_area.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=5)

        self.server_running = False
        self.client_log = "server_log.txt"

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_entry = f"{timestamp} {message}\n"
        with open(self.client_log, "a") as file:
            file.write(log_entry)
        self.text_area.insert(tk.END, log_entry)
        self.text_area.see(tk.END)

    def handle_client(self, client_socket, client_address, client_id):
        """Menangani pesan dari client dengan optimasi Dictionary."""
        self.log_message(f"Client terhubung: {client_address} (ID: {client_id})")

        with self.client_lock:
            self.clients[client_id] = client_socket

        while True:
            try:
                data = client_socket.recv(1024).decode('ascii')
                if not data or data.lower() == "exit": break

                parts = data.split(":", 2)
                if len(parts) >= 3:
                    target_id = parts[1].strip()
                    raw_message = parts[2].strip()

                    # FITUR BROADCAST
                    if target_id.upper() == "ALL":
                        broadcast_text = f"[BROADCAST dari {client_id}]: {raw_message}"
                        self.log_message(f"Broadcast dari {client_id}: {raw_message}")
                        
                        with self.client_lock:
                            for tid, target_sock in self.clients.items():
                                if tid != client_id:
                                    try:
                                        target_sock.send(broadcast_text.encode('ascii'))
                                    except: continue
                        continue

                    # FITUR PRIVAT (OPTIMASI O(1))
                    formatted_msg = f"[Pesan dari {client_id}]: {raw_message}"
                    
                    with self.client_lock:
                        if target_id in self.clients:
                            try:
                                self.clients[target_id].send(formatted_msg.encode('ascii'))
                                self.log_message(f"Pesan: {client_id} -> {target_id} : {raw_message}")
                            except:
                                del self.clients[target_id]
                        else:
                            client_socket.send(f"Error: Client {target_id} tidak ditemukan".encode('ascii'))
            except:
                break

        # Cleanup saat disconnect
        with self.client_lock:
            if client_id in self.clients:
                del self.clients[client_id]
        client_socket.close()
        self.log_message(f"Client {client_id} terputus.")

    def accept_connections(self):
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_id = client_socket.recv(1024).decode('ascii')
                threading.Thread(target=self.handle_client, args=(client_socket, client_address, client_id), daemon=True).start()
            except: break

    def start_server(self, host="127.0.0.1", port=12345):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            self.log_message(f"Server berjalan di {host}:{port}")
            self.start_button.config(state="disabled")
            threading.Thread(target=self.accept_connections, daemon=True).start()
        except Exception as e:
            self.log_message(f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatServerGUI(root)
    root.mainloop()