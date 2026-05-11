import cv2
import numpy as np
from PIL import Image
import os

# Load the fox GIF
gif_path = os.path.join('assets', 'gifs', 'Fox dance.gif')
img = Image.open(gif_path)

# Get first frame
first_frame = np.array(img.convert("RGB"))
first_frame = cv2.cvtColor(first_frame, cv2.COLOR_RGB2BGR)

# Resize to 320x320
first_frame = cv2.resize(first_frame, (320, 320))

print(f"Frame shape: {first_frame.shape}")
print(f"Frame dtype: {first_frame.dtype}")

# Try to display it at position (650, 0)
window_name = "Test Fox"
cv2.namedWindow(window_name)
cv2.moveWindow(window_name, 650, 0)
cv2.imshow(window_name, first_frame)

print("Window displayed. Press 'q' to quit.")
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
