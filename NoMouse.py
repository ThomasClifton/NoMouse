import cv2
import mediapipe as mp
import pyautogui as pag
import math
import configparser

config = configparser.ConfigParser()
config.read('settings.ini')

video_source = config['application']['video_source']
quit_key = config['application']['quit_key']

def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def scale_position(val):
    return (val-.1)/.8

if __name__ == '__main__':
    cap = cv2.VideoCapture(int(video_source))

    ptime = 0
    ctime = 0

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)

    mp_drawing = mp.solutions.drawing_utils
    frame_w, frame_h = pag.size()

    mp_hands = mp.solutions.hands
    with  (mp_hands.Hands(static_image_mode=False,
                         min_detection_confidence=0.7,
                         min_tracking_confidence=0.7,
                         max_num_hands=2) as hands):
        while True:
            success, frame = cap.read()
            if not success:
                print("Error reading frame")
                break
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame.flags.writeable = False
            result = hands.process(frame)

            frame.flags.writeable = True
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Track mouse movement to wrist
                    x, y = int(scale_position(hand_landmarks.landmark[5].x) * frame_w), int(scale_position(hand_landmarks.landmark[5].y) * frame_h)
                    # print(f"x: {hand_landmarks.landmark[5].x}, y: {hand_landmarks.landmark[5].y}")
                    pag.moveTo(x, y)

                    # Left click if thumb and index finger within certain distance
                    # Right click if thumb and middle finger are close
                    if abs(hand_landmarks.landmark[4].x * frame_w - hand_landmarks.landmark[8].x* frame_w) < 50 and \
                        abs(hand_landmarks.landmark[4].y * frame_h - hand_landmarks.landmark[8].y * frame_h) < 50:
                        pag.click(button='left')
                        print("left click")
                    elif abs(hand_landmarks.landmark[4].x * frame_w - hand_landmarks.landmark[12].x* frame_w) < 50 and \
                        abs(hand_landmarks.landmark[4].y * frame_h - hand_landmarks.landmark[12].y * frame_h) < 50:
                        pag.click(button='right')
                        print("right click")

            cv2.imshow("capture", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            key = cv2.waitKey(1)
            if key == ord(quit_key):
                break

    cap.release()
    cv2.destroyAllWindows()