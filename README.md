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
