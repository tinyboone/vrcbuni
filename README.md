# VRChat Discord Rich Presence

## Overview

This is a simple Python application that integrates with VRChat and Discord to display your current VRChat activity as a rich presence on Discord. It periodically updates your presence with details such as the world you are in.

## Features

- Displays your current VRChat activity on Discord as a rich presence.
- Automatically updates presence when you switch worlds in VRChat.

## How to Use

1. **Obtain User ID and Cookie:**
   - To use this application, you need your VRChat user ID and your session cookie.
   - Your user ID can be found in your VRChat profile URL. It's the long string of characters after `/users/`.
   - Your session cookie can be obtained by logging into VRChat in your web browser, then extracting it from the browser's developer tools (in the network tab).

2. **Install Dependencies:**
   - Make sure you have Python installed on your system.
   - Install the required Python packages using pip:
     ```
     pip install -r requirements.txt
     ```

3. **Run the Application:**
   - Run the application using Python:
     ```
     python vrcbuni.py
     ```

4. **Enter User ID and Cookie:**
   - Upon running the application, a window will appear prompting you to enter your user ID and cookie.
   - Enter your user ID and cookie in the respective fields and click "Save".

5. **Enjoy Discord Rich Presence:**
   - Once your credentials are saved, the application will start displaying your VRChat activity as a rich presence on Discord.

## Fixes and Updates

- **Fixed Crash Issue:**
  - Resolved an issue where the application would crash if the world information was not found (404 error).
  - Now, when the world information is not found, it displays "Loading World" in the Discord rich presence.

## Disclaimer

This application is for educational purposes only. Use it responsibly and respect the terms of service of both VRChat and Discord.
