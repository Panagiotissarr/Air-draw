# 🖐️ Air Draw v4.1 (Classic Edition)

Air Draw is a real-time, computer vision-based drawing application that turns your hands into a digital canvas. Using MediaPipe and OpenCV, it tracks hand gestures to allow for free-hand drawing, geometric line baking, and intuitive tool toggling without touching a mouse or keyboard.
# ✨ Features

    Classic Hand Visuals: Restored the "Old Hand" aesthetic with Sea Green (Primary) and Vibrant Orange (Secondary) skeletons.

    Pinch-to-Erase: A high-precision toggle. Pinch your index and thumb together (with other fingers closed) to switch to Eraser Mode.

    Timed Line Tool: Use two hands to "bake" a perfectly straight line with a 5-second countdown.

    Layered UI: * Left Sidebar: Quick "Clear Canvas" button.

        Right Sidebar: Color palette with 8 selectable colors and paginated navigation.

    Performance Optimized: Thinned skeleton lines for better canvas visibility and a white "joint" overlay for classic feedback.

    Desktop Integrated: Support for custom taskbar icons and a Python-based VENV launcher.

# 🛠️ Installation
1. Clone the repository
Bash

git clone https://github.com/YourUsername/Air-Draw.git
cd Air-Draw

2. Set up the Environment

It is recommended to use a virtual environment:
Bash

python -m venv venv
# On Windows:
venv\Scripts\activate

3. Install Dependencies
Bash

pip install opencv-python mediapipe pyautogui pywin32 pillow

4. Required Assets

Ensure [hand_landmarker.task](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) is in the root directory. You can download it from the MediaPipe Solutions page.

# 🎮 Controls
Action	Gesture
Draw	Extend Index Finger only (Thumb tucked).
Erase Toggle	Pinch Index and Thumb tips together (all other fingers closed).
Select Color/Clear	Point Index Finger at the button and hover your Thumb over it.
Straight Line	Extend Index Fingers on both hands.
Bake Line	While in Line mode, Flick your Thumb up to start the 5s timer.
Switch Palette	Hover over the Up/Down Arrows on the right sidebar.

# 📂 Project Structure

    Air-draw_v4.1.py: The main application logic.

    launcher.py: Bootstrapper to auto-activate VENV and run the app.

    logo.ico: The custom taskbar icon.

    hand_landmarker.task: The AI model for hand tracking.

# 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
