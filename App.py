import tkinter as tk
from tkinter import messagebox
import cv2
import pyaudio
import wave
import threading
import subprocess
import os
import time
import socket
import threading
import pyautogui
import pygetwindow as gw
from datetime import datetime
from PIL import Image, ImageTk, ImageGrab
import numpy as np

class Settings:
    def __init__(self):
        self.blur_active = False
        self.mirror_active = False
        self.bw_active = False

class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        tk.Label(master, text="Username:").pack()
        self.entry_username = tk.Entry(master)
        self.entry_username.pack()
        tk.Label(master, text="Password:").pack()
        self.entry_password = tk.Entry(master, show="*")
        self.entry_password.pack()
        tk.Button(master, text="Login", command=self.login).pack()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if username == "utilizator1" and password == "conectare1":
            messagebox.showinfo("Success", "You have successfully logged in!")
            self.open_mainmenu_app(username)
        elif username == "utilizator2" and password == "conectare2":
            messagebox.showinfo("Success", "You have successfully logged in!")
            self.open_mainmenu_app(username)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_mainmenu_app(self, username):
        self.master.destroy()
        menu_window = tk.Tk()
        app = MenuApp(menu_window, username)
        menu_window.mainloop()

class MenuApp:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.master.title("Main Menu")
        user_label = tk.Label(master, text=f"Connected as: {self.username}")
        user_label.pack()
        self.settings = Settings()
        tk.Button(master, text="Connect", command=self.open_webcam_app).pack()
        tk.Button(master, text="Settings", command=self.open_settings).pack()
        tk.Button(master, text="Exit", command=self.exit_app).pack()

    def open_settings(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        app = SettingsApp(settings_window, self.settings)

    def open_webcam_app(self):
        webcam_window = tk.Toplevel(self.master)
        webcam_window.title("Video Conference")
        app = WebcamApp(webcam_window, self.settings, self.username)

    def exit_app(self):
        self.master.destroy()

class SettingsApp:
    def __init__(self, master, settings):
        self.master = master
        self.settings = settings
        self.master.title("Settings")
        self.capture = cv2.VideoCapture(0)
        self.res = (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.canvas = tk.Canvas(master, width=self.res[0], height=self.res[1])
        self.canvas.pack()

        tk.Button(master, text="Toggle Blur", command=self.toggle_blur).pack()
        tk.Button(master, text="Toggle Mirror", command=self.toggle_mirror).pack()
        tk.Button(master, text="Toggle B/W", command=self.toggle_bw).pack()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update()

    def toggle_blur(self):
        self.settings.blur_active = not self.settings.blur_active

    def toggle_mirror(self):
        self.settings.mirror_active = not self.settings.mirror_active

    def toggle_bw(self):
        self.settings.bw_active = not self.settings.bw_active

    def update(self):
        ret, frame = self.capture.read()
        if ret:
            if self.settings.blur_active:
                frame = self.apply_blur(frame)
            if self.settings.mirror_active:
                frame = self.apply_mirror(frame)
            if self.settings.bw_active:
                frame = self.apply_bw(frame)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.master.after(10, self.update)

    def on_closing(self):
        if self.capture.isOpened():
            self.capture.release()
        self.master.destroy()

    def apply_blur(self, frame):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        blurred_frame = cv2.GaussianBlur(frame, (21, 21), cv2.BORDER_DEFAULT)
        for (x, y, w, h) in faces:
            blurred_frame[y:y+h, x:x+w] = frame[y:y+h, x:x+w]
        return blurred_frame

    def apply_mirror(self, frame):
        return cv2.flip(frame, 1)

    def apply_bw(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

class WebcamApp:
    def __init__(self, master, settings, username, server_address='YOUR IP', server_port=5000):
        self.master = master
        self.settings = settings
        self.username = username
        self.server_address = server_address
        self.server_port = server_port
        self.recording = False
        self.master.title("Video Conference")

        # Conectare la server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.server_address, self.server_port))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
            return
        
        # Configurarea capturii video
        self.capture = cv2.VideoCapture(0)
        self.camera_active = True
        if not self.capture.isOpened():
            messagebox.showerror("Camera Error", "Failed to open the camera.")
            self.camera_active = False
            return

        self.fps = 24
        self.res = (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        threading.Thread(target=self.send_video).start()
        threading.Thread(target=self.receive_video).start()

        self.own_canvas = tk.Canvas(master, width=self.res[0], height=self.res[1])
        self.own_canvas.pack(side=tk.LEFT if username == "utilizator1" else tk.RIGHT)

        self.other_user_canvas = tk.Canvas(master, width=self.res[0], height=self.res[1])
        self.other_user_canvas.pack(side=tk.RIGHT if username == "utilizator1" else tk.LEFT)

        self.thread_send = threading.Thread(target=self.send_video)
        self.thread_receive = threading.Thread(target=self.receive_video)
        self.thread_send.daemon = True
        self.thread_receive.daemon = True
        self.thread_send.start()
        self.thread_receive.start()


        # Buton pentru controlul microfonului
        self.mic_button = tk.Button(master, text="Mute", command=self.toggle_mic)
        self.mic_button.pack(side=tk.BOTTOM)
        self.mic_muted = False

        # Buton pentru controlul camerei
        self.cam_button = tk.Button(master, text="Turn Off Camera", command=self.toggle_camera)
        self.cam_button.pack(side=tk.BOTTOM)

        # Buton pentru începerea înregistrării
        self.record_button = tk.Button(master, text="Record", command=self.start_recording)
        self.record_button.pack(side=tk.BOTTOM)

        # Buton pentru oprirea înregistrării
        self.stop_button = tk.Button(master, text="Stop", command=self.stop_recording)
        self.stop_button.pack(side=tk.BOTTOM)

        # Setează GUI pentru chat
        self.chat_log = tk.Text(master, state='disabled', height=8)
        self.chat_log.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.message_entry = tk.Entry(master)
        self.message_entry.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.BOTTOM)

        # Thread pentru mesaje
        threading.Thread(target=self.send_message, daemon=True).start()
        threading.Thread(target=self.receive_message, daemon=True).start()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update()

        self.start_video_stream()
        self.start_message()

    def on_closing(self):
        if self.capture.isOpened():
            self.capture.release()
        if self.sock:
            self.sock.close()
        self.master.destroy()


    def start_video_stream(self):
        if not self.recording:
            self.recording = True
            threading.Thread(target=self.send_video).start()
            threading.Thread(target=self.receive_video).start()
            
    def start_message(self):
        if not self.recording:
            self.recording = True
            threading.Thread(target=self.send_message).start()
            threading.Thread(target=self.receive_message).start()

    def send_video(self):
        try:
            while self.recording:
                ret, frame = self.capture.read()
                if ret:
                    if self.settings.blur_active:
                        frame = self.apply_blur(frame)
                    if self.settings.mirror_active:
                        frame = self.apply_mirror(frame)
                    if self.settings.bw_active:
                        frame = self.apply_bw(frame)
                    _, buffer = cv2.imencode('.jpg', frame)
                    self.sock.sendall(buffer.tobytes())
        except Exception as e:
            print(f"Failed to send video: {e}")

    def receive_video(self):
        try:
            while self.recording:
                data = self.sock.recv(1024 * 1024)
                if not data:
                    break
                if not data.startswith(b'USERMSG '):
                    nparr = np.frombuffer(data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        self.update_frame(frame)
        except Exception as e:
            print(f"Failed to receive video: {e}")

    def send_message(self):
        message = self.message_entry.get()
        if message:
            formatted_message = f"USERMSG {self.username}: {message}\n".encode('utf-8')
            print(f"Sending: {formatted_message}")
            self.sock.sendall(formatted_message)
            self.message_entry.delete(0, tk.END)

    def receive_message(self):
        try:
            while self.recording:
                data = self.sock.recv(1024)
                if not data:
                    break
                print(f"Received: {data}")
                if data.startswith(b'USERMSG '):
                    message_content = data[8:].decode('utf-8').strip()
                    self.display_message(message_content)
        except Exception as e:
            print(f"Error receiving message: {e}")

    def display_message(self, message):
        self.chat_log.config(state='normal')
        tag = 'right' if message.startswith(self.username) else 'left'
        self.chat_log.tag_configure(tag, justify=tk.RIGHT if tag == 'right' else tk.LEFT)
        self.chat_log.insert(tk.END, message + "\n", tag)
        self.chat_log.yview(tk.END)
        self.chat_log.config(state='disabled')

    def update_chat(self, username, text):
        self.chat_log.config(state='normal')
        if username.strip() == self.username:
            self.chat_log.tag_configure('right', justify='right')
            self.chat_log.insert(tk.END, text + "\n", 'right')
        else:
            self.chat_log.tag_configure('left', justify='left')
            self.chat_log.insert(tk.END, username + ": " + text + "\n", 'left')
        self.chat_log.yview(tk.END)
        self.chat_log.config(state='disabled')


    def update_frame(self, frame):
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        self.other_user_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.other_user_canvas.image = photo


    def show_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame))
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)

    def toggle_mic(self):
        self.mic_muted = not self.mic_muted
        self.mic_button.config(text="Unmute" if self.mic_muted else "Mute")

    def toggle_camera(self):
        if self.camera_active:
            self.capture.release()
            self.camera_active = False
            self.cam_button.config(text="Turn On Camera")
        else:
            self.capture = cv2.VideoCapture(0)
            if self.capture.isOpened():
                self.camera_active = True
                self.cam_button.config(text="Turn Off Camera")
            else:
                messagebox.showerror("Camera Error", "Failed to reactivate camera.")

    def mute_mic(self):
        self.mic_muted = True
        print("Microphone muted.")

    def unmute_mic(self):
        self.mic_muted = False
        print("Microphone unmuted.")

    def deactivate_camera(self):
        if self.capture.isOpened():
            self.capture.release()
        print("Camera turned off.")

    def activate_camera(self):
        if not self.capture.isOpened():
            self.capture = cv2.VideoCapture(0)
        print("Camera turned on.")

    def update(self):
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                if self.settings.blur_active:
                    frame = self.apply_blur(frame)
                if self.settings.mirror_active:
                    frame = self.apply_mirror(frame)
                if self.settings.bw_active:
                    frame = self.apply_bw(frame)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                self.photo = ImageTk.PhotoImage(image=image)
                self.own_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.master.after(10, self.update)

    def apply_blur(self, frame):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        blurred_frame = cv2.GaussianBlur(frame, (21, 21), cv2.BORDER_DEFAULT)
        for (x, y, w, h) in faces:
            blurred_frame[y:y+h, x:x+w] = frame[y:y+h, x:x+w]
        return blurred_frame

    def apply_mirror(self, frame):
        return cv2.flip(frame, 1)

    def apply_bw(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

    def start_screen_capture(self):
        screen_capture = pyautogui.screenshot()
        
        frame = np.array(screen_capture)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('screen_capture.avi', fourcc, 20.0, (frame.shape[1], frame.shape[0]))
        out.write(frame)
        
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame = np.array(pyautogui.screenshot())
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)

        out.release()
        cv2.destroyAllWindows()

    def start_recording(self):
        if self.recording:
            return
        self.recording = True
        self.current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.video_thread = threading.Thread(target=self.record_window)
        self.video_thread.start()
        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

    def record_video(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(f'temp_video_{self.current_time}.avi', fourcc, self.fps, self.res)
        while self.recording:
            ret, frame = self.capture.read()
            if ret:
                if self.settings.blur_active:
                    frame = self.apply_blur(frame)
                if self.settings.mirror_active:
                    frame = self.apply_mirror(frame)
                if self.settings.bw_active:
                    frame = self.apply_bw(frame)
                self.out.write(frame)
            else:
                break
        self.out.release()

    def record_audio(self):
        p = pyaudio.PyAudio()
        mic_id = 0
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, input_device_index=mic_id)
        while self.recording:
            data = stream.read(1024)
            if not self.mic_muted:
                self.frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(f'temp_audio_{self.current_time}.wav', 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        self.video_thread.join()
        self.audio_thread.join()

        command = [
            'ffmpeg',
            '-y',
            '-i', f'temp_video_{self.current_time}.avi',
            '-i', f'temp_audio_{self.current_time}.wav',
            '-async', '1',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            f'output_{self.current_time}.mp4'
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(f'temp_video_{self.current_time}.avi')
        os.remove(f'temp_audio_{self.current_time}.wav')
        messagebox.showinfo("Success", "Recording stopped and file saved.")

root = tk.Tk()
app = LoginApp(root)
root.mainloop()
