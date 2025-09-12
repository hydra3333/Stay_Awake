# Stay_Awake

A lightweight system tray application that prevents your computer from going to sleep or hibernating while allowing the display to sleep for power savings.

## Features

- **System Tray Integration**: Runs quietly in the system tray with minimal resource usage
- **Prevents Sleep & Hibernation**: Keeps your system awake for long-running tasks
- **Allows Display Sleep**: Monitor can still turn off to save power
- **Clean Interface**: Simple main window with minimize and quit options
- **Multiple Exit Methods**: Window buttons, system tray right-click menu
- **Automatic Cleanup**: Restores normal power management on exit
- **Cross-platform**: Built with Python, works on Windows (with potential for other platforms)

## Microsoft Defender / Windows Security Issues

**If Windows Defender flags the executable as "Trojan:Win32/Wacatac.C!ml":**

This is a machine learning false positive. The application is safe - all code is publicly available.

**Quick fix:**
1. Open Windows Security (Windows key + I → Update & Security → Windows Security)
2. Go to "Virus & threat protection"
3. Under "Current threats" click "Protection history"
4. Find the Stay_Awake detection and click "Allow on device"

**Or add permanent exclusion:**
1. Windows Security → Virus & threat protection
2. "Manage settings" under Virus & threat protection settings
3. "Add or remove exclusions" 
4. Add the Stay_Awake.exe file or folder

**Submit false positive report:**
Visit: https://www.microsoft.com/en-us/wdsi/filesubmission

## Installation

### Option 1: Download Executable (Recommended)
1. Go to the [Releases](https://github.com/yourusername/Stay_Awake/releases) page
2. Download the latest `Stay_Awake.exe`
3. Run the executable - no installation required!

### Option 2: Run from Source
Requirements:
- Python 3.8 or higher
- pip package manager

```bash
# Clone the repository
git clone https://github.com/yourusername/Stay_Awake.git
cd Stay_Awake

# Install dependencies
pip install wakepy pystray Pillow

# Run the application
python Stay_Awake.py
```

### Option 3: Build Your Own Executable
```bash
# Install build dependencies
pip install pyinstaller wakepy pystray Pillow

# Build the executable
pyinstaller --onefile --windowed --noconsole --name "Stay_Awake" Stay_Awake.py

# The executable will be in the dist/ folder
```

## Usage

1. **Start the Application**: Run `Stay_Awake.exe` or `python Stay_Awake.py`
2. **Control Window**: The main window shows the current status
   - Click "Minimize to System Tray" to hide the window
   - Click "Quit" to exit the application
3. **System Tray**: Look for the eye icon in your system tray
   - **Left-click** the icon to show the main window
   - **Right-click** the icon for menu options (About, Quit)
4. **Window Behavior**: 
   - Both the close button (X) and minimize button (-) send the window to the system tray
   - Only the red "Quit" button or tray menu actually exits the application

## How It Works

Stay_Awake uses the `wakepy` library which calls the Windows `SetThreadExecutionState` API to inform the operating system that the application requires the system to stay awake. This is a lightweight, efficient method that:

- Uses virtually no CPU resources
- Doesn't interfere with other applications
- Automatically cleans up when the application exits
- Is the same method used by professional applications

## Technical Details

- **Language**: Python 3
- **GUI Framework**: tkinter (built into Python)
- **System Tray**: pystray library
- **Wake Management**: wakepy library
- **Icon Generation**: PIL/Pillow
- **Executable Generation**: PyInstaller

## Troubleshooting

**Icon not visible in system tray?**
- Check if your system tray is set to show all icons
- The icon appears as a black eye with radiating lines

**Application doesn't prevent sleep?**
- Make sure no other sleep-prevention software is conflicting
- Check Windows power settings aren't overriding the request
- Verify the application is running (check system tray)

**About dialog won't close?**
- This is fixed in version 1.1+, please update to the latest release

## System Requirements

- **Windows**: Windows 10 or later (primary target)
- **Memory**: Minimal (~10-20 MB RAM usage)
- **CPU**: Negligible impact when idle
- **Dependencies**: None for the executable version

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas for potential improvement:

- macOS and Linux support enhancements
- Additional power management options
- UI themes or customization
- Localization/translations

## License

This project is open source. Please check the LICENSE file for details.

## Changelog

### v1.1 (Latest)
- Fixed About dialog not closing properly
- Improved system tray icon visibility
- Enhanced window minimize behavior
- Both window minimize (-) and close (X) buttons now go to system tray

### v1.0
- Initial release
- Basic system tray functionality
- Prevent sleep and hibernation
- Simple GUI interface

## Support

If you encounter issues:
1. Check the [Issues](https://github.com/yourusername/Stay_Awake/issues) page
2. Create a new issue with details about your system and the problem
3. Include the Python/Windows version you're using

---

**Note**: This application prevents automatic sleep/hibernation but does not prevent manual sleep (e.g., clicking Start → Sleep). This is intentional behavior for user control.
