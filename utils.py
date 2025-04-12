import math
import cv2
import screeninfo


def distance(x1, y1, x2, y2):
    """
    Calculate Euclidean distance between two points.

    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point

    Returns:
        float: Euclidean distance
    """
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def scale_position(val):
    """
    Scale hand landmark coordinate to cursor position.
    Maps the 0-1 range from MediaPipe to usable screen coordinates.

    Args:
        val (float): Normalized coordinate (0-1)

    Returns:
        float: Scaled coordinate
    """
    return (val - 0.2) / 0.6


def find_webcams(max_cameras=4):
    """
    Find available webcams connected to the system.

    Args:
        max_cameras (int): Maximum number of cameras to check

    Returns:
        list: List of available camera indices as strings
    """
    valid_webcams = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            valid_webcams.append(str(i))
            cap.release()
    return valid_webcams


def get_total_screen_dimensions():
    """
    Get dimensions of all monitors combined.
    Useful for multi-monitor setups.

    Returns:
        tuple: (total_width, total_height, min_x, min_y)
    """
    monitors = screeninfo.get_monitors()
    min_x = min(m.x for m in monitors)
    max_x = max(m.x + m.width for m in monitors)
    min_y = min(m.y for m in monitors)
    max_y = max(m.y + m.height for m in monitors)

    # Calculate total width and height
    total_width = max_x - min_x
    total_height = max_y - min_y

    return total_width, total_height, min_x, min_y