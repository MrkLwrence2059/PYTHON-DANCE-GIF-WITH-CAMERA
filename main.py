import cv2
import numpy as np
from PIL import Image
import time
import random
import os
import urllib.request
import math

try:
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision
except ImportError:
    print("Error: MediaPipe not found. Install it with: python -m pip install mediapipe")
    raise SystemExit(1)

# --- SETTINGS ---
GIF_DIR = os.path.join("assets", "gifs")
MODEL_DIR = os.path.join("assets", "models")
POSE_MODEL_PATH = os.path.join(MODEL_DIR, "pose_landmarker_lite.task")
POSE_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
HAND_MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")
HAND_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
SPECIAL_GIF_NAME = "tiktok_thezaysss_7628842312428260629-ezgif.com-optimize.gif"
FOX_GIF_KEYWORD = "fox"
CAT_GIF_KEYWORD = "cat"
PAIR_SIZE_OPTIONS = ["M"]
NOSE_TOUCH_THRESHOLD = 0.16
GRACE_PERIOD = 0.6
WATERMARK_TEXT = "OUTSHINER"
TEXT_PRIMARY_COLOR = (0, 255, 255)  # Yellow
TEXT_SECONDARY_COLOR = (255, 255, 255)  # White
TEXT_ACCENT_COLOR = (0, 255, 0)  # Green
TEXT_OUTLINE_COLOR = (0, 0, 0)  # Black

# GIF window positions (first two slots are under OUTSHINER CAMERA).
SLOTS = [
    (60, 560),   (390, 560),   (720, 560),
    (60, 880),   (390, 880),   (720, 880),
    (1050, 560), (1050, 880),  (1380, 560)
]

def ensure_pose_model(model_path):
    """Ensure the PoseLandmarker model exists locally."""
    if os.path.exists(model_path):
        return model_path
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    print("Downloading MediaPipe Pose model...")
    urllib.request.urlretrieve(POSE_MODEL_URL, model_path)
    print("Model downloaded successfully.")
    return model_path

def create_pose_tracker():
    model_path = ensure_pose_model(POSE_MODEL_PATH)
    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return vision.PoseLandmarker.create_from_options(options)

def ensure_hand_model(model_path):
    """Ensure the HandLandmarker model exists locally."""
    if os.path.exists(model_path):
        return model_path
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    print("Downloading MediaPipe Hand model...")
    urllib.request.urlretrieve(HAND_MODEL_URL, model_path)
    print("Model downloaded successfully.")
    return model_path

def create_hand_tracker():
    model_path = ensure_hand_model(HAND_MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.35,
        min_hand_presence_confidence=0.35,
        min_tracking_confidence=0.35,
    )
    return vision.HandLandmarker.create_from_options(options)

def draw_ui_text(frame, text, org, font, font_scale, color, thickness=2, outline_thickness=4):
    """Draw readable text with dark outline for better contrast."""
    cv2.putText(frame, text, org, font, font_scale, TEXT_OUTLINE_COLOR, outline_thickness, cv2.LINE_AA)
    cv2.putText(frame, text, org, font, font_scale, color, thickness, cv2.LINE_AA)

def add_watermark(frame):
    """Draw OUTSHINER watermark on a frame and return it."""
    marked = frame.copy()
    h, w = marked.shape[:2]
    draw_ui_text(marked, WATERMARK_TEXT, (w - 190, h - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.8, TEXT_SECONDARY_COLOR, thickness=2, outline_thickness=4)
    return marked

def _extract_hand_points(hand_result):
    """Return hand landmarks and wrist points for left/right hands."""
    left_hand = None
    right_hand = None
    left_wrist = None
    right_wrist = None
    for idx, hand_landmarks in enumerate(hand_result.hand_landmarks):
        if idx >= len(hand_result.handedness) or not hand_result.handedness[idx]:
            continue
        label = hand_result.handedness[idx][0].category_name
        wrist = hand_landmarks[0]
        if label == "Left":
            left_hand = hand_landmarks
            left_wrist = wrist
        elif label == "Right":
            right_hand = hand_landmarks
            right_wrist = wrist
    return left_hand, right_hand, left_wrist, right_wrist

def _hand_distance_to_point(hand_landmarks, point):
    """Return the minimum distance from selected hand points to a target point."""
    if hand_landmarks is None or point is None:
        return float("inf")
    # Use palm anchors + fingertips for robust "covering nose" detection.
    check_indices = (0, 5, 9, 13, 17, 4, 8, 12, 16, 20)
    min_dist = float("inf")
    for i in check_indices:
        dx = hand_landmarks[i].x - point.x
        dy = hand_landmarks[i].y - point.y
        d = math.sqrt(dx * dx + dy * dy)
        if d < min_dist:
            min_dist = d
    return min_dist

def draw_hand_xray(frame, hand_result):
    """Draw an x-ray style hand skeleton overlay."""
    if not hand_result.hand_landmarks:
        return

    h, w, _ = frame.shape
    connections = vision.HandLandmarksConnections.HAND_CONNECTIONS

    for hand_idx, hand_landmarks in enumerate(hand_result.hand_landmarks):
        # Draw skeleton connections
        for connection in connections:
            start = hand_landmarks[connection.start]
            end = hand_landmarks[connection.end]
            p1 = (int(start.x * w), int(start.y * h))
            p2 = (int(end.x * w), int(end.y * h))
            cv2.line(frame, p1, p2, (255, 255, 0), 2)

        # Draw joints
        for lm in hand_landmarks:
            p = (int(lm.x * w), int(lm.y * h))
            cv2.circle(frame, p, 4, (0, 255, 255), -1)

        # Draw handedness label
        if hand_idx < len(hand_result.handedness) and hand_result.handedness[hand_idx]:
            label = hand_result.handedness[hand_idx][0].category_name
            score = hand_result.handedness[hand_idx][0].score
            wrist = hand_landmarks[0]
            text_p = (int(wrist.x * w), max(20, int(wrist.y * h) - 15))
            draw_ui_text(frame, f"{label} {score:.2f}", text_p, cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_PRIMARY_COLOR, thickness=2, outline_thickness=4)

def _is_finger_up(hand_landmarks, tip_idx, pip_idx):
    return hand_landmarks[tip_idx].y < hand_landmarks[pip_idx].y

def _is_thumb_up(hand_landmarks, hand_label):
    thumb_tip_x = hand_landmarks[4].x
    thumb_ip_x = hand_landmarks[3].x
    if hand_label == "Right":
        return thumb_tip_x < thumb_ip_x
    if hand_label == "Left":
        return thumb_tip_x > thumb_ip_x
    return abs(thumb_tip_x - thumb_ip_x) > 0.03

def detect_hand_phrase(hand_result):
    """Return phrase based on right-hand gesture only."""
    if not hand_result.hand_landmarks:
        return None

    for idx, hand_landmarks in enumerate(hand_result.hand_landmarks):
        hand_label = ""
        if idx < len(hand_result.handedness) and hand_result.handedness[idx]:
            hand_label = hand_result.handedness[idx][0].category_name
        if hand_label != "Right":
            continue

        index_up = _is_finger_up(hand_landmarks, 8, 6)
        middle_up = _is_finger_up(hand_landmarks, 12, 10)
        ring_up = _is_finger_up(hand_landmarks, 16, 14)
        pinky_up = _is_finger_up(hand_landmarks, 20, 18)
        thumb_up = _is_thumb_up(hand_landmarks, hand_label)

        # Five fingers up.
        if thumb_up and index_up and middle_up and ring_up and pinky_up:
            return "YOU LIKE MY PROJECT"

        # Four fingers up (index to pinky, thumb down).
        if (not thumb_up) and index_up and middle_up and ring_up and pinky_up:
            return "CASEY"

        # Two fingers up (peace sign style).
        if (not thumb_up) and index_up and middle_up and (not ring_up) and (not pinky_up):
            return "I HOPE"

        # One finger up (index finger only).
        if (not thumb_up) and index_up and (not middle_up) and (not ring_up) and (not pinky_up):
            return "HI"

        # Middle finger gesture priority.
        if middle_up and not index_up and not ring_up and not pinky_up and not thumb_up:
            return "POTANGINA MO"

        # Three-finger gesture: index + middle + ring up.
        if index_up and middle_up and ring_up and not pinky_up:
            return "143"

    return None

pose_tracker = create_pose_tracker()
hand_tracker = create_hand_tracker()

# Window name mapping to handle special characters in filenames
window_name_map = {}
window_counter = 0

def get_safe_window_name(gif_filename):
    """Create a safe window name for the GIF filename."""
    global window_counter
    if gif_filename not in window_name_map:
        window_counter += 1
        safe_name = f"GIF_{window_counter}"
        window_name_map[gif_filename] = safe_name
    return window_name_map[gif_filename]

def find_fox_and_cat_names(gif_list):
    """Find fox and cat GIF names from loaded GIF list."""
    fox_name = next((n for n in gif_list if FOX_GIF_KEYWORD in n.lower()), None)
    cat_name = next((n for n in gif_list if CAT_GIF_KEYWORD in n.lower() and n != fox_name), None)
    # Fallback: treat special GIF as cat if no explicit cat filename exists.
    if cat_name is None and SPECIAL_GIF_NAME in gif_list and SPECIAL_GIF_NAME != fox_name:
        cat_name = SPECIAL_GIF_NAME
    return fox_name, cat_name

def load_gifs_with_cache(directory):
    """Preload GIFs in 3 sizes to avoid spawn lag."""
    print("Loading OUTSHINER army and preparing cache...")
    gifs_cache = {} # Structure: { name: { 'P': frames, 'M': frames, 'G': frames } }
    
    if not os.path.exists(directory): return {}
    files = [f for f in os.listdir(directory) if f.lower().endswith(".gif")]
    
    sizes = {"P": 220, "M": 300, "G": 380} # Balanced size definitions

    for name in files:
        path = os.path.join(directory, name)
        try:
            img = Image.open(path)
            raw_frames = []
            while True:
                raw_frames.append(img.convert("RGB"))
                img.seek(img.tell() + 1)
        except EOFError:
            if raw_frames:
                gifs_cache[name] = {}
                # Create all 3 resized versions once at startup
                for label, s in sizes.items():
                    try:
                        processed = [cv2.cvtColor(np.array(f.resize((s, s))), cv2.COLOR_RGB2BGR) for f in raw_frames]
                        gifs_cache[name][label] = processed
                        print(f"Cache ready: {name} - {label} size: {len(processed)} frames, shape: {processed[0].shape}")
                    except Exception as e:
                        print(f"ERROR processing {name} at size {label}: {e}")
    return gifs_cache

# --- INITIALIZATION ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

all_gifs_cache = load_gifs_with_cache(GIF_DIR)
gif_names = list(all_gifs_cache.keys())
print(f"DEBUG: Loaded {len(gif_names)} GIFs: {gif_names}")

active_windows, used_slots = {}, set()
last_spawn, last_movement_time = 0, 0
special_active = False
main_win = "OUTSHINER CAMERA"

cv2.namedWindow(main_win)
cv2.moveWindow(main_win, 0, 0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    timestamp_ms = int(time.monotonic() * 1000)
    pose_res = pose_tracker.detect_for_video(mp_image, timestamp_ms)
    hand_res = hand_tracker.detect_for_video(mp_image, timestamp_ms)
    gesture_phrase = detect_hand_phrase(hand_res)
    draw_hand_xray(frame, hand_res)
    now = time.time()

    left_hand, right_hand, _, _ = _extract_hand_points(hand_res)
    # Right hand is reserved for sign language only.
    moving_now = left_hand is not None
    nose_point = None
    if pose_res.pose_landmarks:
        nose_point = pose_res.pose_landmarks[0][0]

    left_near_nose = _hand_distance_to_point(left_hand, nose_point) <= NOSE_TOUCH_THRESHOLD
    right_near_nose = _hand_distance_to_point(right_hand, nose_point) <= NOSE_TOUCH_THRESHOLD
    hand_near_nose = left_near_nose
    fox_name, cat_name = find_fox_and_cat_names(gif_names)
    special_trigger = hand_near_nose and bool(fox_name and cat_name)

    # Keep fox + cat visible while hand is on nose.
    if special_trigger:
        if not special_active:
            for gif_filename, data in list(active_windows.items()):
                window_name = data.get("window_name", get_safe_window_name(gif_filename))
                try:
                    cv2.destroyWindow(window_name)
                except cv2.error:
                    pass
            active_windows, used_slots = {}, set()
            free_slots = [i for i in range(len(SLOTS)) if i not in used_slots]
            if len(free_slots) >= 2:
                pair_size_label = random.choice(PAIR_SIZE_OPTIONS)
                spawn_pairs = [(fox_name, free_slots[0]), (cat_name, free_slots[1])]
                for gif_name, slot_idx in spawn_pairs:
                    safe_window_name = get_safe_window_name(gif_name)
                    cv2.namedWindow(safe_window_name)
                    cv2.moveWindow(safe_window_name, SLOTS[slot_idx][0], SLOTS[slot_idx][1])
                    active_windows[gif_name] = {
                        "frames": all_gifs_cache[gif_name][pair_size_label],
                        "idx": 0,
                        "slot": slot_idx,
                        "window_name": safe_window_name
                    }
                    used_slots.add(slot_idx)
                special_active = True
                print(f"DEBUG: Nose trigger spawned '{fox_name}' + '{cat_name}' at size '{pair_size_label}'")
    elif special_active:
        for gif_filename, data in list(active_windows.items()):
            window_name = data.get("window_name", get_safe_window_name(gif_filename))
            cv2.destroyWindow(window_name)
        active_windows, used_slots = {}, set()
        special_active = False

    if gesture_phrase:
        draw_ui_text(frame, gesture_phrase, (80, 155), cv2.FONT_HERSHEY_TRIPLEX, 1.1, TEXT_PRIMARY_COLOR, thickness=2, outline_thickness=4)
    elif not hand_res.hand_landmarks:
        draw_ui_text(frame, "Show your hand to the camera", (120, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_SECONDARY_COLOR, thickness=2, outline_thickness=4)

    if hand_near_nose:
        draw_ui_text(frame, "HAND: NOSE OK", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_ACCENT_COLOR, thickness=2, outline_thickness=4)
    if special_active:
        draw_ui_text(frame, "FOX + CAT TRIGGERED", (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_PRIMARY_COLOR, thickness=2, outline_thickness=4)

    frame = add_watermark(frame)

    # --- WINDOW LOGIC (NO HEAVY COMPUTATION) ---
    
    if special_active:
        pass
    elif moving_now:
        last_movement_time = now
        if (now - last_spawn) > 0.4:
            available = [n for n in gif_names if n not in active_windows and n != SPECIAL_GIF_NAME]
            free_slots = [i for i in range(len(SLOTS)) if i not in used_slots]
            print(f"DEBUG: Spawn check - Available GIFs: {available}, Active GIFs: {list(active_windows.keys())}, Free slots: {free_slots}")
            
            if available and free_slots:
                new_gif_name = random.choice(available)
                slot_idx = free_slots[0]
                safe_window_name = get_safe_window_name(new_gif_name)
                print(f"DEBUG: Spawning '{new_gif_name}' at slot {slot_idx} with window name '{safe_window_name}'")
                
                # Keep random spawns moderate to avoid oversized windows.
                size_label = random.choice(["P", "M"])
                
                try:
                    cv2.namedWindow(safe_window_name)
                    cv2.moveWindow(safe_window_name, SLOTS[slot_idx][0], SLOTS[slot_idx][1])
                    
                    # Pull preprocessed frames from cache
                    active_windows[new_gif_name] = {
                        "frames": all_gifs_cache[new_gif_name][size_label], 
                        "idx": 0, 
                        "slot": slot_idx,
                        "window_name": safe_window_name
                    }
                    used_slots.add(slot_idx)
                    last_spawn = now
                    print(f"DEBUG: Successfully created window for '{new_gif_name}'")
                except Exception as e:
                    print(f"ERROR creating window for '{new_gif_name}': {e}")


    elif (now - last_movement_time) > GRACE_PERIOD:
        if active_windows:
            print(f"DEBUG: Grace period expired, destroying {len(active_windows)} windows")
            for gif_filename, data in list(active_windows.items()):
                window_name = data.get("window_name", get_safe_window_name(gif_filename))
                cv2.destroyWindow(window_name)
            active_windows, used_slots = {}, set()

    # Smooth rendering
    for gif_filename, data in list(active_windows.items()):
        try:
            frame_to_show = add_watermark(data["frames"][data["idx"]])
            window_name = data.get("window_name", get_safe_window_name(gif_filename))
            
            if frame_to_show is None or frame_to_show.size == 0:
                print(f"ERROR: Invalid frame for '{gif_filename}', frame is None or empty")
                cv2.destroyWindow(window_name)
                del active_windows[gif_filename]
                if data.get("slot") is not None:
                    used_slots.discard(data["slot"])
            else:
                cv2.imshow(window_name, frame_to_show)
                data["idx"] = (data["idx"] + 1) % len(data["frames"])
                if data["idx"] == 0:  # Print every time we loop through the GIF
                    print(f"DEBUG: Displaying '{gif_filename}' (frame 0 of {len(data['frames'])})")
        except Exception as e:
            print(f"ERROR displaying '{gif_filename}': {type(e).__name__}: {e}")
            try:
                window_name = data.get("window_name", get_safe_window_name(gif_filename))
                cv2.destroyWindow(window_name)
            except:
                pass
            if gif_filename in active_windows:
                del active_windows[gif_filename]
                if data.get("slot") is not None:
                    used_slots.discard(data["slot"])

    cv2.imshow(main_win, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
pose_tracker.close()
hand_tracker.close()
cv2.destroyAllWindows()
