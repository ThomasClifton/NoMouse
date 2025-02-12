import cv2
import mediapipe as mp
import pyautogui as pag
import math


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    ptime = 0
    ctime = 0

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)

    mp_drawing = mp.solutions.drawing_utils
    frame_w, frame_h = pag.size()

    mp_hands = mp.solutions.hands
    with  mp_hands.Hands(static_image_mode=False,
                         min_detection_confidence=0.7,
                         min_tracking_confidence=0.7,
                         max_num_hands=2) as hands:
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
                    x, y = int(hand_landmarks.landmark[0].x * frame_w), int(hand_landmarks.landmark[0].y * frame_h)
                    pag.moveTo(x, y, .1)

                    # Left click if thumb and index finger within certain distance
                    x1, y1 = int(hand_landmarks.landmark[4].x * frame_w), int(hand_landmarks.landmark[4].y * frame_h)
                    x2, y2 = int(hand_landmarks.landmark[8].x * frame_w), int(hand_landmarks.landmark[8].y * frame_h)
                    print(distance(x1, y1, x2, y2))
                    if distance(x1, y1, x2, y2) < 50:
                        print("Click")

            cv2.imshow("capture", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()