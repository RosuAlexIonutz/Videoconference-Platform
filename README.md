Video Conference Application
Overview
This project implements a video conferencing application using Python. It includes a client-side GUI (App.py) and a server component (Server.py) to manage video and audio streaming, along with chat functionalities between users.

Features
User Authentication: Simple login interface with predefined credentials.
Video Conference:
Real-time video streaming between two users.
Video filters including blur, mirror, and grayscale.
Audio Controls:
Mute/unmute microphone during the conference.
Start/stop video recording for later playback.
Settings: Users can apply filters to their video stream.
Chat: Text chat functionality with synchronized message display.
Recording: Capture and save both video and audio as a synchronized file.
Project Structure
App.py: Implements the client-side application with a Tkinter GUI, video capture, streaming, and filter settings.
Server.py: Implements a server to relay video and chat messages between connected clients.
Requirements
Python 3.x
Packages: tkinter, opencv-python, numpy, pyaudio, PIL, socket, wave, pyautogui, pygetwindow
Install required packages with:

bash
Copiază codul
pip install opencv-python-headless numpy pyaudio pillow pyautogui pygetwindow
Usage
Server:
Run the server on the desired IP and port:
bash
Copiază codul
python Server.py
Client:
Run the client application:
bash
Copiază codul
python App.py
Log in with the username and password (utilizator1/conectare1 or utilizator2/conectare2).
Use the Main Menu to start a video conference, adjust settings, or exit.
Notes
The server and clients should be on the same network for optimal connectivity.
Recorded video files are saved in the same directory as the client script.
Acknowledgements
Built with Tkinter for GUI, OpenCV for video processing, and sockets for network communication.
 
