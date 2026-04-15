# 🐍 Python Installation Guide for Windows

## 🎯 Quick Steps (5 Minutes)

### 1. Download Python
- Go to: https://www.python.org/downloads/
- Click "Download Python 3.9+" (latest stable version)
- Choose "Windows installer (64-bit)"

### 2. Run Installer
- Double-click the downloaded `.exe` file
- **IMPORTANT**: Check "Add Python to PATH" at the bottom
- Click "Install Now"

### 3. Verify Installation
- Open Command Prompt or PowerShell
- Type: `python --version`
- Should show: `Python 3.x.x`

### 4. Install Required Packages
```bash
pip install Flask Flask-CORS
```

### 5. Run the Application
```bash
cd "c:/Users/Divya Shree NP/New folder"
python app.py
```

---

## 📋 Detailed Instructions

### Step 1: Download Python
1. Visit https://www.python.org/downloads/
2. Download the latest Python 3.9+ version
3. Save the `.exe` file to your Downloads folder

### Step 2: Install Python
1. Double-click the downloaded installer
2. When the installer opens, look at the bottom
3. **CRITICAL**: Make sure "Add Python to PATH" is checked ✅
4. Click "Install Now"
5. Wait for installation to complete
6. Click "Close"

### Step 3: Verify Installation
1. Open Command Prompt:
   - Press `Win + R`, type `cmd`, press Enter
   - OR search "Command Prompt" in Start Menu

2. Test Python:
   ```bash
   python --version
   ```
   Should show: `Python 3.11.4` (or similar)

3. Test pip:
   ```bash
   pip --version
   ```
   Should show pip version

### Step 4: Install Dependencies
1. In the same command prompt:
   ```bash
   pip install Flask==2.3.3
   pip install Flask-CORS==4.0.0
   pip install gunicorn==21.2.0
   ```

### Step 5: Run Quick Commerce System
1. Navigate to project folder:
   ```bash
   cd "c:/Users/Divya Shree NP/New folder"
   ```

2. Start the application:
   ```bash
   python app.py
   ```

3. You should see:
   ```
   * Serving Flask app 'app'
   * Debug mode: on
   * Running on http://127.0.0.1:5000
   * Press CTRL+C to quit
   ```

4. Open browser and go to: **http://localhost:5000**

---

## 🔧 Troubleshooting

### "Python is not recognized"
- **Solution**: Python wasn't added to PATH during installation
- **Fix**: Reinstall Python and make sure "Add Python to PATH" is checked

### "pip command not found"
- **Solution**: Python PATH issue
- **Fix**: Use `python -m pip install flask` instead

### Port 5000 already in use
- **Solution**: Another app is using port 5000
- **Fix**: Close other apps or change port in `app.py`:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

### ModuleNotFoundError
- **Solution**: Missing dependencies
- **Fix**: Run `pip install -r requirements.txt`

---

## 🚀 Alternative: Use Python Launcher

If Python is installed but `python` command doesn't work:

1. Try: `py app.py`
2. Try: `python3 app.py`
3. Use the provided `run_app.bat` file

---

## ✅ Success Checklist

After installation, you should be able to:
- [ ] Run `python --version` successfully
- [ ] Run `pip list` and see Flask installed
- [ ] Navigate to project folder with `cd`
- [ ] Start app with `python app.py`
- [ ] Access http://localhost:5000 in browser
- [ ] See the Quick Commerce Logistics System interface

---

## 🎯 Next Steps

Once Python is installed and running:
1. Test all features through the web interface
2. Create orders and watch AI optimization
3. Run demand simulations
4. Deploy to Vercel when ready

The system is fully functional - just needs Python environment!
