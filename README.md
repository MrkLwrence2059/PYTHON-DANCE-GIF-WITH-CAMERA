# OUTSHINER dance GIF

This project runs a webcam hand-tracking app that spawns GIF windows and shows gesture messages.

Watermark/ownership:
- The watermark `OUTSHINER` is shown on the camera and GIF windows.
- This project belongs to OUTSHINER.

## Project Structure
- `main.py` - main app
- `requirements.txt` - Python dependencies
- `assets/gifs/` - GIF files used by the app
- `assets/models/` - auto-downloaded MediaPipe models

## Included GIFs
- `tiktok_thezaysss_7628842312428260629-ezgif.com-optimize.gif` (special nose trigger)
- `Fox dance.gif` (random spawn pool)

## How To Run
1. Open PowerShell.
2. Go to the project folder:
   ```powershell
   cd "C:\Users\Mark\Desktop\OUTSHINER dance GIF"
   ```
3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. Run the app:
   ```powershell
   python .\main.py
   ```
5. Press `q` to quit.

## Controls / Behavior
- Hand x-ray overlay appears when hands are detected.
- Gesture text appears for configured hand signs.
- Special GIF behavior:
  - Put either hand near your nose -> special GIF appears.
  - Remove hand from nose -> special GIF closes.
  - Put hand near nose again -> special GIF appears again.

## Notes
- First run may download MediaPipe model files into `assets/models/`.
- If camera does not open, close other apps using webcam and run again.
