import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
from pypresence import Presence
import json
import logging
import threading

class VRChatPresenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VRChat Presence")
        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(self.main_frame, width=60, height=15)
        self.log_text.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.user_id_label = tk.Label(self.main_frame, text="User ID:")
        self.user_id_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        self.user_id_entry = tk.Entry(self.main_frame, width=40)
        self.user_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.cookie_label = tk.Label(self.main_frame, text="Cookie:")
        self.cookie_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        self.cookie_entry = tk.Entry(self.main_frame, width=40)
        self.cookie_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.save_button = tk.Button(self.main_frame, text="Save", command=self.save_credentials)
        self.save_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.presence_thread = None
        self.rpc = None
        self.prev_world_id = None

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # Load saved credentials
        credentials = self.load_credentials()
        if credentials:
            user_id, cookie = credentials
            self.user_id_entry.insert(0, user_id)
            self.cookie_entry.insert(0, cookie)
            threading.Thread(target=self.update_presence, args=(user_id, cookie), daemon=True).start()

    def save_credentials(self):
        user_id = self.user_id_entry.get().strip()
        cookie = self.cookie_entry.get().strip()

        if not user_id or not cookie:
            messagebox.showerror("Error", "Please enter both User ID and Cookie.")
            return

        # Save credentials to JSON file
        credentials = {"user_id": user_id, "cookie": cookie}
        try:
            with open("credentials.json", "w") as f:
                json.dump(credentials, f)
        except Exception as e:
            logging.error(f"Error saving credentials: {e}")
            messagebox.showerror("Error", "Failed to save credentials.")
            return

        self.log_text.insert(tk.END, "Credentials saved.\n")
        self.log_text.see(tk.END)

        threading.Thread(target=self.update_presence, args=(user_id, cookie), daemon=True).start()

    def load_credentials(self):
        try:
            with open("credentials.json", "r") as f:
                credentials = json.load(f)
                user_id = credentials.get("user_id", "")
                cookie = credentials.get("cookie", "")
                return user_id, cookie
        except FileNotFoundError:
            return None
        except Exception as e:
            logging.error(f"Error loading credentials: {e}")
            messagebox.showerror("Error", "Failed to load credentials.")
            return None

    def update_presence(self, user_id, cookie):
        self.rpc = Presence("1128943146638778388")
        try:
            self.rpc.connect()
        except Exception as e:
            logging.error(f"Error connecting to Discord: {e}")
            self.log_text.insert(tk.END, "Failed to connect to Discord.\n")
            self.log_text.see(tk.END)
            return

        start_time = int(time.time())
        self.log_text.insert(tk.END, "Presence updater thread started.\n")
        self.log_text.see(tk.END)

        while True:
            try:
                current_location, world_id = self.get_current_world_info(user_id, cookie)
                if current_location is None or world_id is None:
                    raise Exception("Failed to get user or world information.")
                    
                if world_id != self.prev_world_id:
                    self.prev_world_id = world_id

                    if world_id != 'offline':
                        world_name, world_image_url = self.get_world_info(world_id, cookie)
                        if world_name is not None:
                            large_image = "vrchat_logo"
                            if world_image_url:
                                large_image = world_image_url

                            try:
                                presence_details = "Made by tinyboone"
                                self.rpc.update(
                                    details=presence_details,
                                    state=f"In {world_name}",
                                    start=start_time,
                                    large_image=large_image,
                                    large_text="VRChat World",
                                    small_image="vrchat_logo",
                                    small_text="VRChat"
                                )
                                self.log_text.insert(tk.END, "Discord Rich Presence updated successfully.\n")
                                self.log_text.see(tk.END)
                            except Exception as e:
                                logging.error(f"Error updating Discord Rich Presence: {e}")
                                self.log_text.insert(tk.END, "Failed to update Discord Rich Presence.\n")
                                self.log_text.see(tk.END)
                        else:
                            self.rpc.update(
                                details="Made by tinyboone",
                                state="Loading World",
                                start=start_time,
                                large_image="vrchat_logo",
                                large_text="VRChat World",
                                small_image="vrchat_logo",
                                small_text="VRChat"
                            )
                            self.log_text.insert(tk.END, "World not found, displaying 'Loading World'.\n")
                            self.log_text.see(tk.END)
            except Exception as e:
                logging.error(f"Error: {e}")
                self.log_text.insert(tk.END, f"Error: {e}\n")
                self.log_text.see(tk.END)
            
            time.sleep(4)

    def get_current_world_info(self, user_id, cookie):
        url = f"https://vrchat.com/api/1/users/{user_id}"
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0 make work'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

            if 'location' in user_data and 'worldId' in user_data:
                current_location = user_data['location']
                world_id = user_data['worldId']
                return current_location, world_id
        except Exception as e:
            logging.error(f"Error getting current world information: {e}")
            self.log_text.insert(tk.END, f"Error getting current world information: {e}\n")
            self.log_text.see(tk.END)

        return None, None

    def get_world_info(self, world_id, cookie):
        url = f'https://api.vrchat.cloud/api/1/worlds/{world_id}'
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0 make work'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                raise Exception(f"World not found: {world_id}")
            response.raise_for_status()
            world_data = response.json()

            if 'name' in world_data and 'imageUrl' in world_data:
                world_name = world_data['name']
                world_image_url = world_data['imageUrl']
                return world_name, world_image_url
            else:
                return None, None
        except Exception as e:
            logging.error(f"Error getting world information: {e}")
            self.log_text.insert(tk.END, f"Error getting world information: {e}\n")
            self.log_text.see(tk.END)
            return None, None

if __name__ == "__main__":
    root = tk.Tk()
    app = VRChatPresenceApp(root)
    root.mainloop()
