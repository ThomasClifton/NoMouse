import math
import cv2
import screeninfo


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def scale_position(val):
    return (val - 0.2) / 0.6


def find_webcams(max_cameras=4):
    valid_webcams = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            valid_webcams.append(str(i))
            cap.release()
    return valid_webcams


def get_total_screen_dimensions():
    monitors = screeninfo.get_monitors()
    min_x = min(m.x for m in monitors)
    max_x = max(m.x + m.width for m in monitors)
    min_y = min(m.y for m in monitors)
    max_y = max(m.y + m.height for m in monitors)

    # Calculate total width and height
    total_width = max_x - min_x
    total_height = max_y - min_y

    return total_width, total_height, min_x, min_y