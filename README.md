# NoMouse

NoMouse is a hand gesture-based mouse control application that allows you to control your computer's cursor using hand movements captured by a webcam. Built with MediaPipe's hand tracking technology, this application enables mouse navigation, clicking, and scrolling without touching your physical mouse.

![NoMouse Application](screenshot.png)

## Features

- **Cursor Control**: Move your hand to control the mouse cursor position
- **Left & Right Click**: Perform specific hand gestures to trigger mouse clicks
- **Scrolling**: Use a thumb-to-index gesture with vertical movement to scroll
- **Multi-Monitor Support**: Works across multiple displays
- **Customizable Settings**:
  - Camera selection
  - Left/Right hand preference
  - Camera orientation (Front Facing or Top Down)
  - UI themes

## Installation

### Prerequisites

- Python 3.8 or higher
- Connected Camera
- Windows, macOS, or Linux

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nomouse.git
   cd nomouse
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python NoMouse.py
   ```

## Usage

### Basic Controls

1. **Launch the application**: Run `python NoMouse.py`
2. **Start tracking**: Click the "Start Tracking" button
3. **Control the cursor**: Move your hand in the webcam's field of view
4. **Click**: Use the gestures defined in settings
5. **Scroll**: Touch your thumb to the base of your index finger and move your hand up/down

### Gestures

- **Move Cursor**: Position your hand in the camera's field of view
- **Left Click**: Bring your index finger tip close to your index finger base
- **Right Click**: Bring your thumb tip close to your palm
- **Scroll**: Touch your thumb to the base of your index finger, then move hand up/down

### Settings

Access the settings panel by clicking the "Settings" button:

- **Camera Settings**:
  - Choose webcam: Select from available cameras
  - Hand preference: Choose Left or Right hand for tracking
  - Camera orientation: Set to "Front Facing" for regular webcams or "Top Down" for overhead setup

- **Theme Settings**:
  - Choose from multiple UI themes
  - Preview theme appearance before applying

## Configuration

The application settings are stored in `settings.ini`. This file is automatically created on first run with default values:

```ini
[application]
video_source = 0
hand_preference = Right
theme = arc
camera_orientation = Front Facing
```

### Gesture Configuration

Gestures are defined in `hand_gestures_data.csv`. Each row represents a different gesture:

- LEFT_CLICK (row 0)
- RIGHT_CLICK (row 1)
- SCROLL (row 2)

The CSV columns define which finger positions trigger each gesture.

## Troubleshooting

### Camera Not Working

- Ensure your webcam is properly connected
- Try a different USB port
- Check if another application is using the camera
- Select the correct camera in Settings

### Poor Tracking

- Improve lighting conditions
- Ensure a clean background
- Position your hand clearly in the camera's view
- Adjust your webcam position

### Gesture Not Detected

- Review the gesture definition in the CSV file
- Try making more deliberate gestures
- Adjust your hand position relative to the camera
- Make sure you're using the configured hand preference

## Project Structure

- `NoMouse.py` - Main entry point
- `app_ui.py` - UI implementation
- `gesture_processor.py` - Hand tracking and gesture processing
- `config_manager.py` - Settings management
- `utils.py` - Utility functions
- `hand_gestures_data.csv` - Gesture definitions
- `settings.ini` - Application configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking
- [OpenCV](https://opencv.org/) for computer vision capabilities
- [Tkinter](https://docs.python.org/3/library/tkinter.html) and [ttkthemes](https://ttkthemes.readthedocs.io/) for the UI