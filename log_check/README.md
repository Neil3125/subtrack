# log_check/log_check/README.md

# Log Check Script

This project contains a Python script that logs check entries for service and backup operations. The script collects user input, formats the log entry, and writes it to a file on the user's desktop.

## Files

- `log_check.py`: The main script that implements the logging functionality.
- `requirements.txt`: Lists any dependencies required for the project.

## How to Use

1. Ensure you have Python installed on your system.
2. Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```
3. Run the script by executing:
   ```
   python log_check.py
   ```
4. Follow the prompts to enter the duration and type of check (service or backup).
5. The log entry will be saved to a file named `check_log.txt` on your desktop.

## Creating an Executable

To run this Python script as an executable, you can use a tool like PyInstaller. Here are the steps:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```
2. Navigate to the project directory where `log_check.py` is located.
3. Run the command:
   ```
   pyinstaller --onefile log_check.py
   ```
4. The executable will be created in the `dist` folder. You can find it there and run it directly.

## Notes

- The script uses the `ctypes` library to obtain the desktop path in a Windows-compatible manner.
- Ensure that you have the necessary permissions to write to the desktop.