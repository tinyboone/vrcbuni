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
        self.root.title("VRCbuni remade by tinyboone")
        self.root.configure(bg="#1e1e2e")

        # Main Frame
        self.main_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.main_frame.pack(padx=10, pady=10)

        # Log Text
        self.log_text = scrolledtext.ScrolledText(self.main_frame, width=60, height=15, bg="#2e2e3e", fg="#f0f0f0")
        self.log_text.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # User ID Input
        self.user_id_label = tk.Label(self.main_frame, text="User ID:", bg="#1e1e2e", fg="#ff79c6")
        self.user_id_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        self.user_id_entry = tk.Entry(self.main_frame, width=40, bg="#2e2e3e", fg="#f0f0f0")
        self.user_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Cookie Input
        self.cookie_label = tk.Label(self.main_frame, text="Cookie:", bg="#1e1e2e", fg="#ff79c6")
        self.cookie_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        self.cookie_entry = tk.Entry(self.main_frame, width=40, bg="#2e2e3e", fg="#f0f0f0")
        self.cookie_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Save Button
        self.save_button = tk.Button(self.main_frame, text="Save", command=self.save_credentials, bg="#ff79c6", fg="#1e1e2e")
        self.save_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        # Toggles
        self.small_image_var = tk.BooleanVar(value=True)
        self.small_image_toggle = tk.Checkbutton(self.main_frame, text="Show Avatar as Small Image", variable=self.small_image_var, bg="#1e1e2e", fg="#f0f0f0", selectcolor="#2e2e3e")
        self.small_image_toggle.grid(row=4, column=0, columnspan=2, pady=5)

        self.logs_var = tk.BooleanVar(value=True)
        self.logs_toggle = tk.Checkbutton(self.main_frame, text="Enable Logs", variable=self.logs_var, bg="#1e1e2e", fg="#f0f0f0", selectcolor="#2e2e3e")
        self.logs_toggle.grid(row=5, column=0, columnspan=2, pady=5)

        self.details_var = tk.StringVar(value="Made by tinyboone")
        self.details_toggle = tk.OptionMenu(self.main_frame, self.details_var, "Made by tinyboone", "Set to Username")
        self.details_toggle.config(bg="#ff79c6", fg="#1e1e2e")
        self.details_toggle.grid(row=6, column=0, columnspan=2, pady=5)

        # Presence Variables
        self.presence_thread = None
        self.rpc = None
        self.prev_world_id = None

        # Logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # Load Credentials
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

        self.log("Credentials saved.")

        threading.Thread(target=self.update_presence, args=(user_id, cookie), daemon=True).start()

    def log(self, message):
        if self.logs_var.get():
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)

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
            self.log("Failed to connect to Discord.")
            return

        start_time = int(time.time())
        self.log("Presence updater thread started.")

        while True:
            try:
                current_location, world_id, display_name, avatar_image = self.get_current_world_info(user_id, cookie)
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

                            small_image = "vrchat_logo"
                            small_text = "VRChat"
                            if self.small_image_var.get():
                                small_image = avatar_image
                                small_text = display_name

                            presence_details = self.details_var.get()
                            if presence_details == "Set to Username":
                                presence_details = display_name

                            try:
                                self.rpc.update(
                                    details=presence_details,
                                    state=f"In {world_name}",
                                    start=start_time,
                                    large_image=large_image,
                                    large_text="VRChat World",
                                    small_image=small_image,
                                    small_text=small_text
                                )
                                self.log("Discord Rich Presence updated successfully.")
                            except Exception as e:
                                logging.error(f"Error updating Discord Rich Presence: {e}")
                                self.log("Failed to update Discord Rich Presence.")
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
                            self.log("displaying'Loading World'.")
            except Exception as e:
                logging.error(f"Error: {e}")
                self.log(f"Error: {e}")

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
                display_name = user_data.get('displayName', "Unknown User")
                avatar_image = user_data.get('currentAvatarThumbnailImageUrl', "vrchat_logo")
                return current_location, world_id, display_name, avatar_image
        except Exception as e:
            logging.error(f"Error getting current world information: {e}")
            self.log(f"Error getting current world information: {e}")

        return None, None, None, None

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
            self.log(f"Error getting world information: {e}")
            return None, None
if __name__ == "__main__":
    root = tk.Tk()
    app = VRChatPresenceApp(root)
    root.mainloop()
