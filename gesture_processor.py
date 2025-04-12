import mediapipe as mp
import pandas as pd
from pynput.mouse import Controller, Button
from utils import distance, scale_position, get_total_screen_dimensions

FINGERTIPS = [4, 8, 12, 16, 20]
LEFT_CLICK = 0
RIGHT_CLICK = 1
SCROLL = 2


class GestureProcessor:
    """
    Processor for hand tracking and gesture recognition.
    Detects hand landmarks, interprets gestures, and controls mouse actions.

    Supports:
    - Mouse cursor movement based on hand position
    - Left and right mouse clicks based on finger positions
    - Scrolling based on hand gestures and movement
    """

    def __init__(self):
        """
        Initialize the GestureProcessor with MediaPipe hands tracking
        and mouse control capabilities.
        """
        self.running = False
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False,
                                         model_complexity=1,
                                         min_detection_confidence=0.7,
                                         min_tracking_confidence=0.7,
                                         max_num_hands=2)
        self.hands.use_gpu = True
        self.mouse = Controller()

        self.gesture_data = pd.read_csv('hand_gestures_data.csv')

        # get dimensions with multiple monitors
        self.total_width, self.total_height, self.min_x, self.min_y = get_total_screen_dimensions()

        self.left_mouse_down = False
        self.right_mouse_down = False
        self.scroll_active = False
        self.prev_y = 0
        self.scroll_threshold = 5
        self.scroll_amount = 2
        self.scroll_cooldown = 0

        self.smoothing_factor = 0.3
        self.previous_x = 0
        self.previous_y = 0

        self.position_history = []
        self.history_size = 5

        self.hand_preference = "Right"
        self.camera_orientation = "Front Facing"

    def set_hand_preference(self, preference):
        """
        Set which hand (Left or Right) should be used for tracking.

        Args:
            preference (str): 'Left' or 'Right' to indicate preferred hand
        """
        self.hand_preference = preference

    def set_camera_orientation(self, orientation):
        """
        Set the camera orientation for proper hand tracking.

        Args:
            orientation (str): 'Front Facing' or 'Top Down'
        """
        self.camera_orientation = orientation

    def process_image(self, frame):
        """
        Process a video frame to detect hand landmarks and perform gesture tracking.

        Args:
            frame (numpy.ndarray): Video frame from webcam

        Returns:
            numpy.ndarray: Processed frame with hand landmarks drawn
        """
        if not self.running:
            return frame

        self.total_width, self.total_height, self.min_x, self.min_y = get_total_screen_dimensions()

        image = frame
        image.flags.writeable = False

        results = self.hands.process(image)

        image.flags.writeable = True

        if results.multi_hand_landmarks:
            hands_landmarks = results.multi_hand_landmarks
            hands_handedness = results.multi_handedness

            # If two hands in frame, only track hand preference
            if len(hands_landmarks) == 2:
                for hand_landmarks, handedness in zip(hands_landmarks, hands_handedness):
                    hand_label = handedness.classification[0].label
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    if hand_label == self.hand_preference:
                        self.track_hand(frame, hand_landmarks)
            else:
                hand_landmarks = hands_landmarks[0]
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                self.track_hand(frame, hand_landmarks)
        else:
            # If no hands are detected, release mouse buttons
            self.release_all_buttons()

        return image

    def track_hand(self, frame, hand_landmarks):
        """
        Track hand position and gestures to control mouse behavior.

        Handles:
        - Mouse cursor positioning based on hand movement
        - Left/right click detection based on finger positions
        - Scroll gesture detection and vertical scrolling

        Args:
            frame (numpy.ndarray): The current video frame
            hand_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList):
                Detected hand landmarks
        """
        frame_h, frame_w = frame.shape[:2]

        raw_x = int(scale_position(hand_landmarks.landmark[5].x) * self.total_width) + self.min_x
        raw_y = int(scale_position(hand_landmarks.landmark[5].y) * self.total_height) + self.min_y

        smoothed_position = self.smooth_position(raw_x, raw_y)
        x, y = smoothed_position

        # Only update mouse position if not in scroll mode
        if not self.scroll_active:
            self.mouse.position = (x, y)

        scroll_detected = True
        for index, finger in enumerate(FINGERTIPS):
            # Skip if the column doesn't exist in the data
            if index + 11 >= len(self.gesture_data.columns) or not self.gesture_data.iloc[SCROLL, (index + 11)]:
                continue

            ref_landmark_idx = int(self.gesture_data.iloc[SCROLL, (index + 1)])
            threshold = self.gesture_data.iloc[SCROLL, (index + 6)]

            if ref_landmark_idx < 0 or ref_landmark_idx >= len(hand_landmarks.landmark):
                continue

            finger_dist = distance(
                hand_landmarks.landmark[finger].x * frame_w,
                hand_landmarks.landmark[finger].y * frame_h,
                hand_landmarks.landmark[ref_landmark_idx].x * frame_w,
                hand_landmarks.landmark[ref_landmark_idx].y * frame_h
            )

            # If any finger position doesn't match the scroll gesture, don't scroll
            if finger_dist > threshold:
                scroll_detected = False
                break

        # Handle scrolling if the scroll gesture is detected
        if scroll_detected:
            if not self.scroll_active:
                self.scroll_active = True
                self.prev_y = y
            else:
                # Already in scroll mode, check for vertical movement
                if self.scroll_cooldown <= 0:
                    if y < self.prev_y - self.scroll_threshold:
                        # Scroll up
                        self.mouse.scroll(0, self.scroll_amount)
                        self.prev_y = y
                        self.scroll_cooldown = 3  # Add cooldown to prevent too rapid scrolling
                        print("Scrolling up")
                    elif y > self.prev_y + self.scroll_threshold:
                        # Scroll down
                        self.mouse.scroll(0, -self.scroll_amount)
                        self.prev_y = y
                        self.scroll_cooldown = 3  # Add cooldown to prevent too rapid scrolling
                        print("Scrolling down")
                else:
                    self.scroll_cooldown -= 1
        else:
            # Scroll gesture not detected
            if self.scroll_active:
                print("Scroll mode deactivated")
            self.scroll_active = False

            # Process mouse clicks only if not scrolling
            for index, finger in enumerate(FINGERTIPS):
                # Left click gesture processing
                if self.gesture_data.iloc[LEFT_CLICK, (index + 11)]:
                    ref_landmark_idx = int(self.gesture_data.iloc[LEFT_CLICK, (index + 1)])
                    threshold = self.gesture_data.iloc[LEFT_CLICK, (index + 6)]

                    if ref_landmark_idx < 0 or ref_landmark_idx >= len(hand_landmarks.landmark):
                        continue

                    finger_dist = distance(
                        hand_landmarks.landmark[finger].x * frame_w,
                        hand_landmarks.landmark[finger].y * frame_h,
                        hand_landmarks.landmark[ref_landmark_idx].x * frame_w,
                        hand_landmarks.landmark[ref_landmark_idx].y * frame_h
                    )

                    if finger_dist < threshold:
                        if not self.left_mouse_down:
                            self.mouse.press(Button.left)
                            self.left_mouse_down = True
                            print("Left mouse down")
                    else:
                        if self.left_mouse_down:
                            self.mouse.release(Button.left)
                            self.left_mouse_down = False
                            print("Left mouse up")

                # Right click gesture processing
                if self.gesture_data.iloc[RIGHT_CLICK, (index + 11)]:
                    ref_landmark_idx = int(self.gesture_data.iloc[RIGHT_CLICK, (index + 1)])
                    threshold = self.gesture_data.iloc[RIGHT_CLICK, (index + 6)]

                    if ref_landmark_idx < 0 or ref_landmark_idx >= len(hand_landmarks.landmark):
                        continue

                    finger_dist = distance(
                        hand_landmarks.landmark[finger].x * frame_w,
                        hand_landmarks.landmark[finger].y * frame_h,
                        hand_landmarks.landmark[ref_landmark_idx].x * frame_w,
                        hand_landmarks.landmark[ref_landmark_idx].y * frame_h
                    )

                    if finger_dist < threshold:
                        if not self.right_mouse_down:
                            self.mouse.press(Button.right)
                            self.right_mouse_down = True
                            print("Right mouse down")
                    else:
                        if self.right_mouse_down:
                            self.mouse.release(Button.right)
                            self.right_mouse_down = False
                            print("Right mouse up")

    def smooth_position(self, x, y):
        """
        Apply smoothing to cursor movement to reduce jitter.

        Uses a combination of averaging and momentum for smoother tracking.

        Args:
            x (int): Raw x-coordinate
            y (int): Raw y-coordinate

        Returns:
            tuple: Smoothed (x, y) coordinates
        """
        self.position_history.append((x, y))

        if len(self.position_history) > self.history_size:
            self.position_history.pop(0)

        avg_x = sum(pos[0] for pos in self.position_history) / len(self.position_history)
        avg_y = sum(pos[1] for pos in self.position_history) / len(self.position_history)

        smoothed_x = int(self.previous_x * self.smoothing_factor + avg_x * (1 - self.smoothing_factor))
        smoothed_y = int(self.previous_y * self.smoothing_factor + avg_y * (1 - self.smoothing_factor))

        self.previous_x = smoothed_x
        self.previous_y = smoothed_y

        return smoothed_x, smoothed_y

    def release_all_buttons(self):
        """
        Release any currently pressed mouse buttons.
        Called when hand tracking is lost or stopped.
        """
        if self.left_mouse_down:
            self.mouse.release(Button.left)
            self.left_mouse_down = False
            print("left mouse released (no hand)")

        if self.right_mouse_down:
            self.mouse.release(Button.right)
            self.right_mouse_down = False
            print("right mouse released (no hand)")

    def start_tracking(self):
        """
        Begin hand tracking and mouse control.
        Initializes tracking state variables.
        """
        self.running = True
        self.previous_x, self.previous_y = self.total_width // 2 + self.min_x, self.total_height // 2 + self.min_y
        self.position_history = [(self.previous_x, self.previous_y)] * self.history_size

    def stop_tracking(self):
        """
        Stop hand tracking and mouse control.
        Ensures all mouse buttons are released.
        """
        self.running = False
        self.release_all_buttons()