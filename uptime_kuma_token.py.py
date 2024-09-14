import socketio
import tkinter as tk
from tkinter import messagebox
import pyperclip

# Uptime Kuma client to get the token
class UptimeKumaClient:
    def __init__(self, url):
        self.url = url
        self.token = None
        self.sio = socketio.Client()

    def connect(self):
        try:
            self.sio.connect(self.url)
            print("Connected to Uptime Kuma WebSocket")
        except Exception as e:
            print(f"Connection Error: {e}")
            return False
        return True

    def login(self, username, password, token2fa=None):
        def handle_login_response(response):
            if response['ok']:
                self.token = response['token']
                print(f"Login successful, token: {self.token}")
                return self.token
            else:
                if response.get('tokenRequired', False):
                    print("Two-factor authentication required")
                else:
                    print(f"Login failed: {response.get('msg', 'Unknown error')}")
            return None
        
        self.sio.emit(
            "login",
            {
                "username": username,
                "password": password,
                "token": token2fa,
            },
            callback=handle_login_response
        )

    def get_token(self):
        return self.token


# GUI to enter credentials and display the token
def login_and_get_token():
    username = username_entry.get()
    password = password_entry.get()
    url = url_entry.get()

    if not username or not password or not url:
        messagebox.showwarning("Input Error", "Please provide URL, username, and password.")
        return

    client = UptimeKumaClient(url)
    if not client.connect():
        messagebox.showerror("Connection Error", "Failed to connect to the server.")
        return

    client.login(username, password)

    root.after(1000, lambda: display_token(client))

def display_token(client):
    token = client.get_token()
    if token:
        token_label.config(text=f"Token: {token}")
        copy_button.config(state="normal")
    else:
        token_label.config(text="Failed to get token. Check credentials.")

def copy_to_clipboard():
    token = token_label.cget("text").replace("Token: ", "")
    if token:
        pyperclip.copy(token)
        messagebox.showinfo("Copied", "Token copied to clipboard!")

# GUI Setup using Tkinter
root = tk.Tk()
root.title("Uptime Kuma Login")
root.geometry("400x300")

tk.Label(root, text="Uptime Kuma URL:").pack(pady=10)
url_entry = tk.Entry(root)
url_entry.pack(pady=5)

tk.Label(root, text="Username:").pack(pady=10)
username_entry = tk.Entry(root)
username_entry.pack(pady=5)

tk.Label(root, text="Password:").pack(pady=10)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

login_button = tk.Button(root, text="Login", command=login_and_get_token)
login_button.pack(pady=20)

token_label = tk.Label(root, text="Token: ", wraplength=300)
token_label.pack(pady=10)

copy_button = tk.Button(root, text="Copy Token to Clipboard", command=copy_to_clipboard, state="disabled")
copy_button.pack(pady=5)

# Start the GUI event loop
root.mainloop()
