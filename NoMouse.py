import math
import cv2
import mediapipe as mp
import pyautogui as pag
import time
import tkinter as tk
from PIL import Image, ImageTk
import configparser

config = configparser.ConfigParser()
config.read('settings.ini')

video_source = config.get('application','video_source')
quit_key = config.get('application','quit_key')

def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def scale_position(val):
    return (val - 0.2) / 0.6

def set_capture_device(num):
    config.set('application', 'video_source', str(num))
    save_config()

def set_quit_key(key):
    config.set('application', 'quit_key', key)
    save_config()

def save_config():
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

def find_webcams(max_cameras=4):
    valid_webcams = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            valid_webcams.append(str(i))
            cap.release()
    return valid_webcams

webcam_list = find_webcams()

class GestureProcessor:
    def __init__(self):
        self.running = False
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False,
                                         model_complexity=1,
                                         min_detection_confidence=0.5,
                                         min_tracking_confidence=0.5,
                                         max_num_hands=2)

    def process_image(self, frame):
        if not self.running:
            return frame

        frame_w, frame_h = pag.size()

        image = frame
        image.flags.writeable = False

        results = self.hands.process(image)

        image.flags.writeable = True

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                x, y = int(scale_position(hand_landmarks.landmark[5].x) * frame_w), int(
                    scale_position(hand_landmarks.landmark[5].y) * frame_h)

                # Move cursor to the position detected by the hand
                pag.moveTo(x, y)

                # Left click if thumb and index finger within certain distance
                # Right click if thumb and middle finger are close
                if abs(hand_landmarks.landmark[4].x * frame_w - hand_landmarks.landmark[8].x * frame_w) < 50 and \
                        abs(hand_landmarks.landmark[4].y * frame_h - hand_landmarks.landmark[8].y * frame_h) < 50:
                    pag.click(button='left')
                    print("left click")
                elif abs(hand_landmarks.landmark[4].x * frame_w - hand_landmarks.landmark[12].x * frame_w) < 50 and \
                        abs(hand_landmarks.landmark[4].y * frame_h - hand_landmarks.landmark[12].y * frame_h) < 50:
                    pag.click(button='right')
                    print("right click")

        return image

    def start_tracking(self):
        self.running = True

    def stop_tracking(self):
        self.running = False


# Main UI loop to handle video capture and display with Tkinter
class Application(tk.Tk):
    def __init__(self, processor):
        super().__init__()

        self.processor = processor

        # Settings Button
        self.settings_button = tk.Button(self, text="Settings", command=self.open_config_window)
        self.settings_button.pack(anchor=tk.W, expand=True)

        # canvas to display the video feed
        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack()

        # FPS label
        self.fps_label = tk.Label(self, text="FPS: 0", font=("Arial", 14))
        self.fps_label.pack()

        # Start the video capture
        self.cap = cv2.VideoCapture(int(video_source))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.last_time = time.time()
        self.frame_count = 0

        # Add buttons to start and stop tracking
        self.start_button = tk.Button(self, text="Start Tracking", command=self.start_tracking)
        self.start_button.pack(anchor=tk.CENTER, expand=True)

        self.stop_button = tk.Button(self, text="Stop Tracking", command=self.stop_tracking)
        self.stop_button.pack(anchor=tk.CENTER, expand=True)

        self.update_video_frame()

    def update_video_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Process the frame and get the result
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result_image = self.processor.process_image(frame)

            result_image = Image.fromarray(result_image)
            result_image = ImageTk.PhotoImage(result_image)

            # Update the canvas
            self.canvas.create_image(0, 0, image=result_image, anchor=tk.NW)
            self.canvas.image = result_image

            # FPS
            self.frame_count += 1
            if time.time() - self.last_time >= 1:
                fps = self.frame_count
                self.fps_label.config(text=f"FPS: {fps}")
                self.frame_count = 0
                self.last_time = time.time()
        # Updates again after 10 ms
        self.after(10, self.update_video_frame)

    def open_config_window(self):
        config_window = tk.Toplevel(self)
        config_window.title("Settings")

        label = tk.Label(config_window, text="Choose a webcam:")
        label.pack(pady=10)

        webcams = tk.StringVar(config_window)

        option_menu = tk.OptionMenu(config_window, webcams, *webcam_list)
        option_menu.pack()

        def save_options():
            webcam = webcams.get()
            self.cap.release()
            self.cap = cv2.VideoCapture(int(webcam))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            config_window.destroy()
            set_capture_device(webcam)

        save_button = tk.Button(config_window, text="Save", command=save_options)
        save_button.pack()

    def start_tracking(self):
        self.processor.start_tracking()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_tracking(self):
        self.processor.stop_tracking()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def on_close(self):
        self.processor.running = False
        self.cap.release()
        self.destroy()


# Run the Tkinter UI with GestureProcessor
def run_app():
    processor = GestureProcessor()
    app = Application(processor)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()

if __name__ == "__main__":
    run_app()
