# Steam to TierMaker GUI Application

A standalone GUI application that combines Steam image scraping and TierMaker uploading into a single executable with a simple interface.

## Features

- 🖥️ **Simple GUI Interface**: Easy-to-use graphical interface with one-click operation
- 🎮 **Steam Integration**: Automatically scrapes game images from your Steam library
- 📤 **TierMaker Upload**: Uploads all images to TierMaker.com for tier list creation
- 📊 **Real-time Progress**: Live progress updates and detailed logging
- 🔧 **Configurable**: Customizable Steam URL and output folder
- 🚀 **Standalone Executable**: No Python installation required on target machines

## Quick Start

### Option 1: Use Pre-built Executable
1. Download the `SteamToTierMaker.exe` from the releases
2. Make sure Chrome browser is installed
3. Run the executable
4. Enter your Steam library URL
5. Click "Start Process"

### Option 2: Build from Source
1. Install Python 3.8+ and Chrome browser
2. Install dependencies:
   ```bash
   pip install -r requirements_gui.txt
   ```
3. Build executable:
   ```bash
   python build_exe.py
   ```
   Or on Windows:
   ```bash
   build.bat
   ```

## How to Use

1. **Get Your Steam Library URL**:
   - Go to your Steam profile
   - Click on "Games" tab
   - Make sure your profile is set to PUBLIC
   - Copy the URL (should look like: `https://steamcommunity.com/profiles/YOUR_ID/games/?tab=all`)

2. **Run the Application**:
   - Launch `SteamToTierMaker.exe`
   - Paste your Steam library URL
   - Choose output folder (default: `steam_images`)
   - Click "🚀 Start Process"

3. **Process Flow**:
   - The app will open Chrome and navigate to your Steam library
   - If login is required, log in to Steam in the browser window
   - The app will automatically scroll and download all game images
   - Then it will upload all images to TierMaker.com
   - Your browser will stay open on TierMaker with all images ready

4. **Create Your Tier List**:
   - Use the TierMaker interface to create your tier list
   - Drag and drop games between tiers
   - Save and share your tier list

## Configuration

The application uses `config.json` for settings:

```json
{
    "steam_library_url": "https://steamcommunity.com/profiles/YOUR_ID/games/?tab=all",
    "output_folder": "steam_images",
    "delay_between_downloads": 0.1,
    "scroll_pause": 0.1,
    "max_scroll_attempts": 1000
}
```

## Troubleshooting

### Common Issues

1. **"Chrome not found"**:
   - Install Google Chrome browser
   - Make sure Chrome is in your system PATH

2. **"Login required"**:
   - Make sure your Steam profile is set to PUBLIC
   - Log in to Steam when prompted in the browser window

3. **"No images found"**:
   - Check that your Steam library URL is correct
   - Ensure your profile is public and has games

4. **"Upload failed"**:
   - Check your internet connection
   - Make sure TierMaker.com is accessible
   - Try running the process again

### Performance Tips

- Use a fast internet connection for better download speeds
- Close other browser tabs to free up memory
- The process may take several minutes for large game libraries

## Technical Details

### Dependencies
- Python 3.8+
- Selenium WebDriver
- Chrome browser
- tkinter (included with Python)
- requests
- Pillow (PIL)

### File Structure
```
steam-to-tiermaker/
├── steam_tiermaker_gui.py      # Main GUI application
├── steam_image_scraper.py      # Steam scraping functionality
├── tiermaker_uploader.py       # TierMaker upload functionality
├── config.json                 # Configuration file
├── requirements_gui.txt        # Python dependencies
├── build_exe.py               # Build script
├── build.bat                  # Windows build script
└── steam_images/              # Downloaded images folder
```

## Building the Executable

### Prerequisites
- Python 3.8+
- All dependencies installed
- Chrome browser

### Build Steps
1. Install build dependencies:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

3. The executable will be created in the `dist/` folder

### Build Options
- **Console**: Set `console=True` in the spec file for debugging
- **Icon**: Add an icon file and update the spec file
- **One-file**: Modify the spec file to create a single executable file

## License

MIT License - see LICENSE file for details.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Make sure all requirements are met
3. Check the log output in the GUI for error details
4. Ensure your Steam profile is public and accessible
