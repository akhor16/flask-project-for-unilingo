# Install Tesseract OCR for Windows

## Quick Installation Steps:

### Option 1: Download and Install (Recommended)
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
3. Run the installer
4. **Important**: During installation, make sure to check "Add to PATH" option
5. Restart your terminal/PyCharm

### Option 2: Manual PATH Setup (if Option 1 doesn't work)
1. Install Tesseract to default location: `C:\Program Files\Tesseract-OCR\`
2. Add to Windows PATH:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"
   - Under "System Variables", find and select "Path", click "Edit"
   - Click "New" and add: `C:\Program Files\Tesseract-OCR\`
   - Click OK on all dialogs
3. Restart your terminal/PyCharm

### Option 3: Test Installation
Open a new terminal and run:
```bash
tesseract --version
```

If it shows version information, Tesseract is properly installed!

## For the App:
The app will automatically detect Tesseract in common Windows locations. If you still get errors, the app will show helpful error messages with installation instructions.
