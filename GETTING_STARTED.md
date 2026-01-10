# 🚀 Getting Started with Stock Advisor Pro

Welcome! This guide is for **anyone new to coding, GitHub, or this project**. We'll walk you through downloading the code, setting everything up, and running the application.

---

## 📋 What You Need

Before you start, make sure you have:

1. **A Mac or Windows computer** (Linux also works)
2. **About 5-10 minutes** for setup
3. **Internet connection** (to download files and dependencies)

That's it! We'll install everything else together.

---

## 🎯 Three Ways to Get the Code

Pick **one** of these options:

### Option 1: Download as a ZIP File (Easiest for beginners)

This is the simplest way if you've never used GitHub before.

**Steps:**
1. Open your web browser and go to: https://github.com/ethanwack/StockAdvisor
2. Click the green **Code** button (top right)
3. Click **Download ZIP**
4. Your browser will download a file called `StockAdvisor-main.zip`
5. Double-click the file to unzip it (creates a folder called `StockAdvisor-main`)
6. Rename the folder to just `StockAdvisor` (optional, but easier)
7. **Done!** You now have the code on your computer.

### Option 2: Use Git (Recommended if you plan to update regularly)

Git is a tool for managing code. If you don't have it installed:

**On Mac:**
- Open Terminal (Spotlight → type "Terminal" → press Enter)
- Paste this command:
```bash
xcode-select --install
```
- Wait for it to finish, then:

**Copy and paste this into Terminal:**
```bash
cd ~
git clone https://github.com/ethanwack/StockAdvisor.git
cd StockAdvisor
```

**On Windows:**
- Download and install Git from: https://git-scm.com/download/win
- Open Git Bash (search for it in Start menu)
- Paste these commands:
```bash
cd ~
git clone https://github.com/ethanwack/StockAdvisor.git
cd StockAdvisor
```

### Option 3: Fork and Clone (For developers who want to contribute)

1. Go to https://github.com/ethanwack/StockAdvisor
2. Click **Fork** (top right) — this creates your own copy
3. On your forked repo, click **Code** → **Copy** the HTTPS URL
4. Open Terminal/Git Bash and run:
```bash
cd ~
git clone [PASTE-THE-URL-YOU-COPIED]
cd StockAdvisor
```

---

## 📂 What's Inside the Folder?

After downloading, your `StockAdvisor` folder should contain:

```
StockAdvisor/
├── main.py                    ← Run this for the desktop app
├── backend/                   ← Python backend code
├── frontend/                  ← Web interface code
├── gui/                       ← Desktop app screens
├── services/                  ← Analysis engines
├── mobile/                    ← iPhone app code
├── README.md                  ← Project overview
└── GETTING_STARTED.md         ← This file!
```

---

## ✅ Verify You Have the Right Files

Open a Terminal and check:

**On Mac or Linux:**
```bash
cd ~/StockAdvisor
ls -la
```

**On Windows (Git Bash):**
```bash
cd ~/StockAdvisor
ls -la
```

You should see files and folders like `main.py`, `gui/`, `services/`, `mobile/`, etc.

If you don't see these, make sure you're in the right folder. Type `pwd` and press Enter to see where you are.

---

## 🖥️ Running the Desktop Application

This is the main Stock Advisor app with all the analysis tools.

### Step 1: Install Python

**Check if you have Python 3:**
```bash
python3 --version
```

If you see a version like `Python 3.9` or higher, you're good! If not:

**On Mac:**
- Install Homebrew first (paste this in Terminal):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
- Then install Python:
```bash
brew install python
```

**On Windows:**
- Download from: https://www.python.org/downloads/
- **Important:** Check the box "Add Python to PATH" during install
- Restart your computer after installing

### Step 2: Set Up the Python Environment

This creates an isolated space for the app's dependencies.

```bash
cd ~/StockAdvisor
python3 -m venv venv
```

Now activate it:

**On Mac/Linux:**
```bash
source venv/bin/activate
```

**On Windows (Git Bash):**
```bash
source venv/Scripts/activate
```

You'll see `(venv)` appear at the start of your terminal line. Good!

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This downloads all the packages the app needs (yfinance, PySide6, scikit-learn, etc.). It may take 2-5 minutes.

### Step 4: Run the App!

```bash
python3 main.py
```

A window should pop up with the Stock Advisor interface. 🎉

**To stop the app:** Press Ctrl+C in Terminal, or close the window.

---

## 📱 Running the Mobile App (iPhone/Android)

This is the mobile version of Stock Advisor.

### Step 1: Install Node.js

The mobile app needs Node.js and npm (which comes with it).

**Check if you have it:**
```bash
node --version
npm --version
```

If you see version numbers, you're good! If not:

**On Mac:**
```bash
brew install node
```

**On Windows:**
- Download from: https://nodejs.org/ (pick the LTS version)
- Run the installer and follow the steps
- Restart your computer

### Step 2: Install Mobile Dependencies

```bash
cd ~/StockAdvisor/mobile
npm install
```

This may take 2-5 minutes.

### Step 3: Start the Development Server

```bash
npm start
```

You'll see a QR code in the terminal. Now you have two options:

**Option A: Run on your iPhone**
- Download "Expo Go" from the App Store
- Open Expo Go on your phone
- Scan the QR code shown in Terminal
- The app loads on your phone!

**Option B: Run on a Simulator (Mac only)**
- Install Xcode from the App Store (free, but large)
- Type this in Terminal:
```bash
npm run ios
```

**Option C: Run on Android (Windows/Mac/Linux)**
- Download Android Studio from https://developer.android.com/studio
- Set it up (follow their guide)
- In Terminal, type:
```bash
npm run android
```

---

## 🌐 Running the Web Frontend (Optional)

If you want to run the web version:

```bash
cd ~/StockAdvisor/frontend
npm install
npm start
```

Your browser will open to http://localhost:3000 with the web app.

---

## ❓ Troubleshooting

### "Command not found: python3"
**Solution:** Python isn't installed or not in your PATH.
- **Mac:** `brew install python`
- **Windows:** Reinstall Python and check "Add Python to PATH"

### "Permission denied" when cloning with Git
**Solution:** You're using SSH but don't have SSH keys set up. Use Option 1 (download ZIP) or Option 2 (use HTTPS clone).

### "ModuleNotFoundError" when running the app
**Solution:** You forgot to activate the virtual environment or didn't install dependencies.
```bash
source venv/bin/activate  # Mac/Linux
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### "npm: command not found"
**Solution:** Node.js isn't installed.
- **Mac:** `brew install node`
- **Windows:** Download from https://nodejs.org/

### App runs but looks weird or crashes
**Solution:** Make sure you have the latest Python (3.9+) and Node.js (16+).
```bash
python3 --version
node --version
```

### Need to update your copy of the code later
If you used Option 2 (Git clone):
```bash
cd ~/StockAdvisor
git pull origin main
```

If you used Option 1 (ZIP download):
- Download the latest ZIP again and extract it

---

## 📚 Next Steps

Once everything is running:

1. **Desktop App:** Explore the tabs (Dashboard, Search, Technical Analysis, etc.)
2. **Mobile App:** Try adding stocks to your watchlist
3. **Documentation:** Read `README.md` for detailed feature info
4. **Connect Data:** Check the Settings tab to connect your broker accounts (optional)

---

## 🆘 Still Stuck?

If something doesn't work:

1. **Read the error message** — it often tells you what's wrong
2. **Check you're in the right folder** — type `pwd` to confirm
3. **Make sure you activated the virtual environment** — you should see `(venv)` in your terminal
4. **Restart Terminal** — sometimes fixes weird issues
5. **Search online for the error** — most Python/Node errors have solutions on Stack Overflow

---

## 💡 Quick Reference Commands

**Navigate to the project:**
```bash
cd ~/StockAdvisor
```

**Activate Python environment (Mac/Linux):**
```bash
source venv/bin/activate
```

**Activate Python environment (Windows):**
```bash
source venv/Scripts/activate
```

**Run the desktop app:**
```bash
python3 main.py
```

**Run the mobile app:**
```bash
cd mobile
npm start
```

**Run the web frontend:**
```bash
cd frontend
npm start
```

**Stop any running app:**
Press `Ctrl+C` in Terminal

**Deactivate Python environment:**
```bash
deactivate
```

---

## 🎉 You're All Set!

Congratulations! You've set up Stock Advisor Pro. Enjoy exploring the app and analyzing stocks!

If you run into any issues or have questions, feel free to reach out. Happy investing! 📈

---

**Version:** 1.0  
**Last Updated:** January 2026  
**Questions?** Check the `README.md` or `INSTALLATION.md` files for more details.
