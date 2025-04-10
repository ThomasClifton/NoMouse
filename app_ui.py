import tkinter as tk
from tkinter import ttk
import time
import cv2
from PIL import Image, ImageTk
from ttkthemes import ThemedTk, ThemedStyle
from config_manager import save_config, get_config_value, set_config_value
from utils import find_webcams


class Application(ThemedTk):
    def __init__(self, processor):
        current_theme = get_config_value('application', 'theme', 'arc')

        super().__init__(theme=current_theme)
        self.title("NoMouse")

        self.configure(padx=10, pady=10)

        # Create a themed style
        self.themed_style = ThemedStyle(self)
        self.available_themes = self.get_themes()

        self.processor = processor
        self.processor.set_hand_preference(get_config_value('application', 'hand_preference', 'Right'))
        self.processor.set_camera_orientation(get_config_value('application', 'camera_orientation', 'Front Facing'))

        self.config_window = None

        # main container frame
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # frame for controls
        self.top_frame = ttk.Frame(self.main_container, padding=5)
        self.top_frame.pack(fill=tk.X, pady=(0, 5))

        # settings Button
        self.settings_button = ttk.Button(self.top_frame, text="Settings", command=self.open_settings_window)
        self.settings_button.pack(side=tk.LEFT)

        # frame for the video display
        self.video_frame = ttk.LabelFrame(self.main_container, text="Video Feed", padding=10)
        self.video_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        self.info_frame = ttk.Frame(self.main_container, padding=5)
        self.info_frame.pack(fill=tk.X, pady=5)

        self.fps_label = ttk.Label(self.info_frame, text="FPS: 0", font=("Arial", 14))
        self.fps_label.pack(side=tk.LEFT, padx=10)

        # Start the video capture
        video_source = get_config_value('application', 'video_source', '0')
        self.cap = cv2.VideoCapture(int(video_source))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.last_time = time.time()
        self.frame_count = 0

        self.button_frame = ttk.Frame(self.main_container, padding=5)
        self.button_frame.pack(fill=tk.X, pady=5)

        self.start_button = ttk.Button(self.button_frame, text="Start Tracking", command=self.start_tracking)
        self.start_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.stop_button = ttk.Button(self.button_frame, text="Stop Tracking", command=self.stop_tracking)
        self.stop_button.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)

        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Not tracking")
        self.statusbar = ttk.Label(self.main_container, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        self.update_background()

        self.update_video_frame()

    def update_background(self):
        try:
            bg_color = self.themed_style.lookup('TFrame', 'background')
            if not bg_color:
                bg_color = self.themed_style.lookup('TLabel', 'background')
            if bg_color:
                self.configure(background=bg_color)
        except Exception as e:
            print(f"Error updating background: {e}")

    def update_video_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Process the frame and get the result
            if self.processor.camera_orientation == "Front Facing":
                frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result_image = self.processor.process_image(frame)

            pil_image = Image.fromarray(result_image)
            photo_image = ImageTk.PhotoImage(pil_image)

            # Update the label with the new image
            self.video_label.configure(image=photo_image)
            self.video_label.image = photo_image

            # FPS calculation
            self.frame_count += 1
            if time.time() - self.last_time >= 1:
                fps = self.frame_count
                self.fps_label.config(text=f"FPS: {fps}")
                self.frame_count = 0
                self.last_time = time.time()

        # Update again after 10 ms
        self.after(10, self.update_video_frame)

    def open_settings_window(self):
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.lift()
            return

        # Create a regular Toplevel window
        self.config_window = tk.Toplevel(self)
        self.config_window.title("Settings")
        self.config_window.geometry("320x320")
        self.config_window.resizable(False, False)
        self.config_window.transient(self)
        self.config_window.grab_set()

        self.config_window.geometry(f"+{self.winfo_x()}+{self.winfo_y()}")
        current_theme = get_config_value('application', 'theme', 'arc')

        style = ThemedStyle(self.config_window)
        style.set_theme(current_theme)

        main_frame = ttk.Frame(self.config_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        video_source = get_config_value('application', 'video_source', '0')
        webcams = tk.StringVar(self.config_window)
        webcams.set(video_source)  # Set current value

        theme_var = tk.StringVar(self.config_window)
        theme_var.set(current_theme)  # Set current value

        hand_var = tk.StringVar(self.config_window)
        hand_var.set(get_config_value('application', 'hand_preference', 'Right'))  # Set current value

        orientation_var = tk.StringVar(self.config_window)
        orientation_var.set(get_config_value('application', 'camera_orientation', 'Front Facing'))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        camera_tab = ttk.Frame(notebook, padding=10)
        theme_tab = ttk.Frame(notebook, padding=10)

        notebook.add(camera_tab, text="Camera Settings")
        notebook.add(theme_tab, text="Theme Settings")

        webcam_list = find_webcams()

        webcam_label = ttk.Label(camera_tab, text="Choose a webcam:")
        webcam_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        webcam_menu = ttk.Combobox(camera_tab, textvariable=webcams, values=webcam_list, state="readonly")
        webcam_menu.grid(column=1, row=0, sticky=tk.W, padx=5, pady=5)

        hand_label = ttk.Label(camera_tab, text="Hand Preference:")
        hand_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        hand_menu = ttk.Combobox(camera_tab, textvariable=hand_var, values=["Left", "Right"], state="readonly")
        hand_menu.grid(column=1, row=1, sticky=tk.W, padx=5, pady=5)

        orientation_label = ttk.Label(camera_tab, text="Camera Orientation:")
        orientation_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

        orientation_menu = ttk.Combobox(camera_tab, textvariable=orientation_var,
                                        values=["Front Facing", "Top Down"], state="readonly")
        orientation_menu.grid(column=1, row=2, sticky=tk.W, padx=5, pady=5)

        theme_label = ttk.Label(theme_tab, text="Choose a theme:")
        theme_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        theme_menu = ttk.Combobox(theme_tab, textvariable=theme_var, values=self.available_themes, state="readonly")
        theme_menu.grid(column=1, row=0, sticky=tk.W, padx=5, pady=5)

        theme_preview_label = ttk.Label(theme_tab, text="Theme Preview:")
        theme_preview_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        preview_frame = ttk.LabelFrame(theme_tab, text="Preview", padding=10)
        preview_frame.grid(column=0, row=2, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)

        preview_button = ttk.Button(preview_frame, text="Button")
        preview_button.pack(side=tk.LEFT, padx=5)

        preview_entry = ttk.Entry(preview_frame)
        preview_entry.pack(side=tk.LEFT, padx=5)
        preview_entry.insert(0, "Sample text")

        def on_theme_change(event):
            selected_theme = theme_var.get()
            style.set_theme(selected_theme)
            try:
                bg_color = style.lookup('TFrame', 'background')
                if bg_color:
                    self.config_window.configure(background=bg_color)
            except Exception as e:
                print(f"Error updating preview: {e}")

        theme_menu.bind("<<ComboboxSelected>>", on_theme_change)
        button_frame = ttk.Frame(self.config_window, padding=(10, 5))
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        def save_settings():
            webcam = webcams.get()
            theme = theme_var.get()
            hand = hand_var.get()
            orientation = orientation_var.get()
            need_update = False

            if webcam and webcam != video_source:
                self.cap.release()
                self.cap = cv2.VideoCapture(int(webcam))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                set_config_value('application', 'video_source', webcam)
                need_update = True

            if hand and hand != self.processor.hand_preference:
                set_config_value('application', 'hand_preference', hand)
                self.processor.set_hand_preference(hand)
                need_update = True

            if orientation and orientation != self.processor.camera_orientation:
                set_config_value('application', 'camera_orientation', orientation)
                self.processor.set_camera_orientation(orientation)
                need_update = True

            current_theme = get_config_value('application', 'theme', 'arc')
            if theme and theme != current_theme:
                self.set_theme(theme)
                set_config_value('application', 'theme', theme)
                self.themed_style.theme_use(theme)
                self.update_background()
                need_update = True

            save_config()

            self.config_window.destroy()

            if need_update:
                self.status_var.set("Settings updated")
            else:
                self.status_var.set("Ready - Not tracking")

        def close_settings():
            self.config_window.destroy()
            current_theme = get_config_value('application', 'theme', 'arc')
            self.themed_style.theme_use(current_theme)
            self.update_background()

        save_button = ttk.Button(button_frame, text="Save", command=save_settings)
        close_button = ttk.Button(button_frame, text="Cancel", command=close_settings)
        close_button.pack(side=tk.RIGHT, padx=5)
        save_button.pack(side=tk.RIGHT, padx=5)

    def start_tracking(self):
        self.processor.start_tracking()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Active - Tracking enabled")

    def stop_tracking(self):
        self.processor.stop_tracking()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Ready - Not tracking")

    def on_close(self):
        self.processor.running = False
        self.processor.release_all_buttons()
        self.cap.release()
        self.destroy()