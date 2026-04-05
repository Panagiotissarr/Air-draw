import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import win32gui, win32con, win32api
import time, math, ctypes, os
from PIL import Image, ImageDraw, ImageFont

# --- WINDOW & ICON SETUP ---
myappid = 'sarris.airdraw.v4.1' 
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
SCREEN_W, SCREEN_H = pyautogui.size()

window_name = "Air Draw"
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
hwnd = win32gui.FindWindow(None, window_name)
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 0, win32con.LWA_COLORKEY)

icon_path = os.path.join(os.getcwd(), "logo.ico")
if os.path.exists(icon_path):
    hicon = win32gui.LoadImage(None, icon_path, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
    win32api.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)

# --- COLORS ---
COLOR_DATA = {
    "WHITE": (255, 255, 255), "CYAN": (0, 255, 255), "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255), "YELLOW": (255, 255, 0), "RED": (255, 0, 0),
    "ORANGE": (255, 165, 0), "PURPLE": (128, 0, 128)
}
color_keys = list(COLOR_DATA.keys())
pages = [color_keys[0:4], color_keys[4:8]]

# --- STATE ---
color = "WHITE" 
current_page = 0
last_ui_action = 0 
prev_pos = {"Hand_0": (0,0), "Hand_1": (0,0)}
is_eraser = False

# --- INITIALIZE ---
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2, min_hand_detection_confidence=0.5)
detector = vision.HandLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0)
canvas = np.zeros((SCREEN_H, SCREEN_W, 3), dtype=np.uint8)

HAND_CONNECTIONS = [(0,1), (1,2), (2,3), (3,4), (0,5), (5,6), (6,7), (7,8), (5,9), (9,10), (10,11), (11,12), (9,13), (13,14), (14,15), (15,16), (13,17), (17,18), (18,19), (19,20), (0,17)]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    hud_frame = np.zeros((SCREEN_H, SCREEN_W, 3), dtype=np.uint8)
    cv2.rectangle(hud_frame, (0,0), (SCREEN_W, SCREEN_H), (20, 20, 20), -1)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    results = detector.detect(mp_image)

    active_indices = []

    if results.hand_landmarks:
        for h_id, landmarks in enumerate(results.hand_landmarks):
            h_tag = f"Hand_{h_id}"
            pts = [(int(lm.x * SCREEN_W), int(lm.y * SCREEN_H)) for lm in landmarks]
            t_tip, i_tip = pts[4], pts[8]
            now = time.time()
            
            # Skeleton
            hand_color = (0, 255, 127) if h_id == 0 else (255, 140, 0)
            for conn in HAND_CONNECTIONS: cv2.line(hud_frame, pts[conn[0]], pts[conn[1]], hand_color, 2)
            for pt in pts: cv2.circle(hud_frame, pt, 3, (255, 255, 255), -1)

            # Finger States
            m_closed = landmarks[12].y > landmarks[10].y
            r_closed = landmarks[16].y > landmarks[14].y
            p_closed = landmarks[20].y > landmarks[18].y
            
            # --- STRICT PINCH TOGGLE ---
            # Distance between Thumb Tip (4) and Index Tip (8)
            pinch_dist = math.hypot(t_tip[0] - i_tip[0], t_tip[1] - i_tip[1])
            
            # Only toggle if pinch is tight AND other fingers are closed
            if pinch_dist < 35 and m_closed and r_closed and p_closed:
                if now - last_ui_action > 1.2:
                    is_eraser = not is_eraser
                    last_ui_action = now

            # Eraser Visual Ring
            if is_eraser and h_id == 0:
                cv2.circle(hud_frame, i_tip, 35, (255, 0, 255), 3)

            # --- NAVIGATION & DRAWING ---
            i_up = landmarks[8].y < landmarks[6].y
            
            if i_up:
                # Button Hits (Using Index finger tip for precision)
                if i_tip[0] < 250 and i_tip[1] > SCREEN_H - 180:
                    canvas = np.zeros_like(canvas)

                if i_tip[0] > SCREEN_W - 200:
                    if i_tip[1] < 120 and (now - last_ui_action > 0.8):
                        current_page = (current_page + 1) % 2
                        last_ui_action = now
                    elif i_tip[1] > SCREEN_H - 120 and (now - last_ui_action > 0.8):
                        current_page = (current_page + 1) % 2
                        last_ui_action = now
                    for i, name in enumerate(pages[current_page]):
                        y_btn = 150 + (i * 170)
                        if y_btn < i_tip[1] < y_btn + 120: 
                            color = name
                            is_eraser = False

                # Free Draw (Only if not pinching)
                if pinch_dist > 60 and m_closed and r_closed and p_closed:
                    px, py = prev_pos[h_tag]
                    b_color = (0,0,0) if is_eraser else COLOR_DATA[color]
                    thick = 95 if is_eraser else 15
                    if px != 0: cv2.line(canvas, (px, py), i_tip, b_color, thick)
                    prev_pos[h_tag] = i_tip
                else: prev_pos[h_tag] = (0,0)
            else: prev_pos[h_tag] = (0,0)

    # --- UI RENDER ---
    pil_img = Image.fromarray(hud_frame)
    draw = ImageDraw.Draw(pil_img)
    try: font_b = ImageFont.truetype("JetBrainsMono NF", 25)
    except: font_b = ImageFont.load_default()

    if is_eraser:
        draw.rounded_rectangle([SCREEN_W//2-100, 15, SCREEN_W//2+100, 65], 10, fill=(255,0,255))
        draw.text((SCREEN_W//2-85, 25), "ERASER ACTIVE", font=font_b, fill=(255,255,255))

    draw.rounded_rectangle([20, SCREEN_H - 150, 230, SCREEN_H - 30], 15, fill=(40,40,40), outline=(255,255,255))
    draw.text((85, SCREEN_H - 100), "CLEAR", font=font_b, fill=(255,255,255))
    
    draw.polygon([(SCREEN_W-100, 40), (SCREEN_W-140, 90), (SCREEN_W-60, 90)], fill=(255,255,255))
    draw.polygon([(SCREEN_W-100, SCREEN_H-40), (SCREEN_W-140, SCREEN_H-90), (SCREEN_W-60, SCREEN_H-90)], fill=(255,255,255))

    for i, name in enumerate(pages[current_page]):
        y_p = 150 + (i * 170)
        if color == name and not is_eraser: 
            draw.rounded_rectangle([SCREEN_W-145, y_p-10, SCREEN_W-15, y_p+110], 15, outline=(255,255,255), width=4)
        draw.rounded_rectangle([SCREEN_W-130, y_p, SCREEN_W-30, y_p+100], 15, fill=COLOR_DATA[name])

    final_bgr = cv2.cvtColor(cv2.addWeighted(np.array(pil_img), 1, canvas, 1, 0), cv2.COLOR_RGB2BGR)
    cv2.imshow(window_name, final_bgr)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()