import cv2
import mediapipe as mp
import pyautogui as pag
import math
import pandas as pd

FINGERTIPS = [4, 8, 12, 16, 20]
LEFT_CLICK = 0
RIGHT_CLICK = 1
SCROLL = 2
prev_Y = 0
ScrollUpBool = False
ScrollDownBool = False

def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def scale_position(val):
    return (val-.1)/.8

def dist_to_send(dist):
    if dist == -1.0:
        return dist
    else:
        return dist + 10

if __name__ == '__main__':
    gestureCSV = pd.read_csv('hand_gestures_data.csv')

    cap = cv2.VideoCapture(0)

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

                    LeftClickBool = True
                    RightClickBool = True
                    ScrollBool = True

                    # Iterate through each of the 5 fingers
                    # Only check distance if the finger is part of the gesture
                    # If distance isn't small enough, then the gesture is not being performed; mark as false
                    for index, finger in enumerate(FINGERTIPS):
                        if gestureCSV.iloc[LEFT_CLICK, (index + 11)] == True:
                            if distance(hand_landmarks.landmark[finger].x * frame_w,
                                        hand_landmarks.landmark[finger].y * frame_h,
                                        hand_landmarks.landmark[gestureCSV.iloc[LEFT_CLICK, (index + 1)]].x * frame_w,
                                        hand_landmarks.landmark[gestureCSV.iloc[LEFT_CLICK, (index + 1)]].y * frame_h) > gestureCSV.iloc[LEFT_CLICK, (index + 6)]:
                                LeftClickBool = False

                        if gestureCSV.iloc[RIGHT_CLICK, (index + 11)] == True:
                            if distance(hand_landmarks.landmark[finger].x * frame_w,
                                        hand_landmarks.landmark[finger].y * frame_h,
                                        hand_landmarks.landmark[gestureCSV.iloc[RIGHT_CLICK, (index + 1)]].x * frame_w,
                                        hand_landmarks.landmark[gestureCSV.iloc[RIGHT_CLICK, (index + 1)]].y * frame_h) > gestureCSV.iloc[RIGHT_CLICK, (index + 6)]:
                                RightClickBool = False

                        if gestureCSV.iloc[SCROLL, (index + 11)] == True:
                            if distance(hand_landmarks.landmark[finger].x * frame_w,
                                        hand_landmarks.landmark[finger].y * frame_h,
                                        hand_landmarks.landmark[gestureCSV.iloc[SCROLL, (index + 1)]].x * frame_w,
                                        hand_landmarks.landmark[gestureCSV.iloc[SCROLL, (index + 1)]].y * frame_h) > gestureCSV.iloc[SCROLL, (index + 6)]:
                                ScrollBool = False

                    if ScrollBool is True:
                        if ScrollUpBool == True:
                            pag.scroll(3)
                            print("scrollUp")
                        elif ScrollDownBool == True:
                            pag.scroll(-3)
                            print("scrollDown")
                        if y < prev_Y:
                            ScrollUpBool = True
                            ScrollDownBool = False
                        elif y > prev_Y:
                            ScrollDownBool = True
                            ScrollUpBool = False
                    elif LeftClickBool is True:
                        pag.click(button='left')
                        ScrollUpBool = False
                        ScrollDownBool = False
                        print("left click")
                    elif RightClickBool is True:
                        pag.click(button='right')
                        ScrollUpBool = False
                        ScrollDownBool = False
                        print("right click")
                    else:
                        ScrollUpBool = False
                        ScrollDownBool = False

                    prev_Y = y

            cv2.imshow("capture", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == ord('s'):
                row = int(input("Input Gesture: "))  # 0 = LeftClick, 1 = RightClick
                fingersInGesture = []
                for i in range(5):
                    bool = input("t/f: ")
                    if bool == "t":
                        fingersInGesture.append(True)
                    elif bool == "f":
                        fingersInGesture.append(False)
                closestList = []
                distList = []

                for index, fingertipLandmark in enumerate(FINGERTIPS):
                    closest = None
                    dist = None
                    if fingersInGesture[index] == True:
                        for i in range(21):
                            dist2 = distance(hand_landmarks.landmark[fingertipLandmark].x * frame_w,
                                             hand_landmarks.landmark[fingertipLandmark].y * frame_h,
                                             hand_landmarks.landmark[i].x * frame_w,
                                             hand_landmarks.landmark[i].y * frame_h)
                            if dist == None:
                                dist = dist2
                                closest = i
                            elif i == fingertipLandmark or i == fingertipLandmark - 1:
                                dist = dist
                                closest = closest
                            elif dist2 < dist:
                                dist = dist2
                                closest = i
                        closestList.append(closest)
                        distList.append(dist)
                    else:
                        closestList.append(-1)
                        distList.append(-1.0)

                gesture = {"name": gestureCSV.iloc[row, 0],
                           "landmark_thumb": closestList[0], "distance_thumb": dist_to_send(distList[0]),
                           "landmark_index": closestList[1], "distance_index": dist_to_send(distList[1]),
                           "landmark_middle": closestList[2], "distance_middle": dist_to_send(distList[2]),
                           "landmark_ring": closestList[3], "distance_ring": dist_to_send(distList[3]),
                           "landmark_pinky": closestList[4], "distance_pinky": dist_to_send(distList[4]),
                           "tf0": fingersInGesture[0], "tf1": fingersInGesture[1], "tf2": fingersInGesture[2],
                           "tf3": fingersInGesture[3], "tf4": fingersInGesture[4]}

                gestureCSV.iloc[row] = gesture
                gestureCSV.to_csv('hand_gestures_data.csv', index=False)

                gestureCSV = pd.read_csv('hand_gestures_data.csv')

    cap.release()
    cv2.destroyAllWindows()
