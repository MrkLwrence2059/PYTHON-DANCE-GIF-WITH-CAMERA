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

## Git + GitHub Guide (For Any Project)

Use this for future projects so they are saved to your GitHub account.

### 1) One-time setup (new PC only)
```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### 2) Publish a brand-new project folder
1. Create an empty repository on GitHub first (no README, no license).
2. In PowerShell, open your project folder:
   ```powershell
   cd "C:\path\to\your\project"
   ```
3. Initialize git and commit:
   ```powershell
   git init -b main
   git add .
   git commit -m "Initial commit"
   ```
4. Connect to GitHub and push:
   ```powershell
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```

### 3) Update an existing project and push new changes
```powershell
cd "C:\path\to\your\project"
git add .
git commit -m "Describe your changes"
git push
```

### 4) Check if everything is linked correctly
```powershell
git status
git branch --show-current
git remote -v
```

### 5) Helpful fixes
- If `origin` is wrong:
  ```powershell
  git remote set-url origin https://github.com/<your-username>/<repo-name>.git
  ```
- If repo has no `main` branch yet:
  ```powershell
  git branch -M main
  git push -u origin main
  ```
