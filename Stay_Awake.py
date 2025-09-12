__version__ = "1.1.2"
__author__ = "Open Source"
__description__ = "System tray application to prevent sleep"
"""
Stay_Awake System Tray Application
Keeps system awake, runs in system tray with minimal GUI

NOTE: for testing ...
.pyw files run with pythonw.exe instead of python.exe
pythonw.exe doesn't create a console window
Drawback: You lose all the print() messages, but the app works silently.
"""

import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
from wakepy import keep
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import atexit
import signal

class Stay_AwakeTrayApp:
    def __init__(self):
        self.running = False
        self.icon = None
        self.main_window = None
        self.keep_awake_context = None
        self.window_visible = True
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def create_image(self):
        """Create an eye icon that fills the entire tray icon space"""
        # Create a high-resolution image for crisp scaling
        image = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Fill almost the entire space with the eye shape (leave tiny border)
        # Eye outline - uses almost full width and good height
        eye_left = 10
        eye_top = 80
        eye_right = 246
        eye_bottom = 176
        
        # Draw the outer eye shape (almond/oval)
        draw.ellipse([eye_left, eye_top, eye_right, eye_bottom], 
                    fill='black', outline='black')
        
        # Inner eye (white part) - slightly smaller
        inner_margin = 20
        draw.ellipse([eye_left + inner_margin, eye_top + inner_margin, 
                     eye_right - inner_margin, eye_bottom - inner_margin], 
                    fill='white', outline='white')
        
        # Pupil (black center) - large and centered
        pupil_size = 50
        center_x = 128
        center_y = 128
        draw.ellipse([center_x - pupil_size//2, center_y - pupil_size//2,
                     center_x + pupil_size//2, center_y + pupil_size//2],
                    fill='black', outline='black')
        
        # Small white highlight in pupil for life-like appearance
        highlight_size = 15
        highlight_offset_x = -12
        highlight_offset_y = -12
        draw.ellipse([center_x + highlight_offset_x, center_y + highlight_offset_y,
                     center_x + highlight_offset_x + highlight_size, 
                     center_y + highlight_offset_y + highlight_size],
                    fill='white', outline='white')
        
        # Add "awake" radiating lines around the eye - using full space
        import math
        for angle in [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]:
            rad = math.radians(angle)
            # Start from edge of eye
            start_distance = 130
            end_distance = 240
            
            x1 = center_x + start_distance * math.cos(rad)
            y1 = center_y + start_distance * math.sin(rad)
            x2 = center_x + end_distance * math.cos(rad) 
            y2 = center_y + end_distance * math.sin(rad)
            
            # Make sure lines stay within bounds
            x2 = max(5, min(x2, 251))
            y2 = max(5, min(y2, 251))
            
            draw.line([x1, y1, x2, y2], fill='black', width=8)
        
        return image
    
    def create_main_window(self):
        """Create the main control window"""
        self.main_window = tk.Tk()
        self.main_window.title("Stay_Awake Control")
        self.main_window.geometry("350x200")
        self.main_window.resizable(False, False)
        
        # Center the window
        self.main_window.geometry("+{}+{}".format(
            (self.main_window.winfo_screenwidth() // 2) - 175,
            (self.main_window.winfo_screenheight() // 2) - 100
        ))
        
        # Handle window close button (X) and minimize button
        self.main_window.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        # Override the minimize button behavior
        self.main_window.bind("<Unmap>", self.on_window_minimize)
        
        # Create main frame
        main_frame = tk.Frame(self.main_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        status_label = tk.Label(
            main_frame, 
            text="Stay_Awake is Active", 
            font=("Arial", 14, "bold"),
            fg="green"
        )
        status_label.pack(pady=(0, 10))
        
        # Info label
        info_label = tk.Label(
            main_frame,
            text="System sleep and hibernation are prevented.\nDisplay Monitor sleep is allowed.",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        info_label.pack(pady=(0, 20))
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Minimize to tray button
        minimize_btn = tk.Button(
            button_frame,
            text="Minimize to System Tray",
            command=self.minimize_to_tray,
            font=("Arial", 11),
            padx=20,
            pady=8,
            bg="#4CAF50",
            fg="white",
            relief="raised"
        )
        minimize_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Quit button
        quit_btn = tk.Button(
            button_frame,
            text="Quit",
            command=self.quit_from_window,
            font=("Arial", 11),
            padx=20,
            pady=8,
            bg="#f44336",
            fg="white",
            relief="raised"
        )
        quit_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status info at bottom
        bottom_label = tk.Label(
            main_frame,
            text="When minimized, right-click the tray icon for options.",
            font=("Arial", 9),
            fg="gray"
        )
        bottom_label.pack(side=tk.BOTTOM, pady=(20, 0))
    
    def minimize_to_tray(self):
        """Hide the main window and show in tray"""
        if self.main_window:
            self.main_window.withdraw()
            self.window_visible = False
    
    def on_window_minimize(self, event):
        """Handle window minimize button (underscore icon) - redirect to system tray"""
        # Only handle if this is the main window being minimized
        if event.widget == self.main_window:
            # Use after_idle to ensure the minimize event completes first
            self.main_window.after_idle(self.check_and_redirect_minimize)
    
    def check_and_redirect_minimize(self):
        """Check if window was minimized and redirect to system tray"""
        # If window is iconified (minimized to taskbar), redirect to system tray
        if self.main_window.state() == 'iconic':
            self.minimize_to_tray()
    
    def show_main_window(self, icon=None, item=None):
        """Show the main window from tray"""
        if self.main_window:
            self.main_window.deiconify()
            self.main_window.lift()
            self.main_window.focus_force()
            self.window_visible = True
    
    def quit_from_window(self):
        """Quit the application from main window"""
        self.quit_application(None, None)
    
    def start_Stay_Awake(self):
        """Start the Stay_Awake functionality"""
        try:
            # Use the modern wakepy API
            self.keep_awake_context = keep.running()
            self.keep_awake_context.__enter__()
            self.running = True
            print("Stay_Awake activated")
        except Exception as e:
            if self.main_window:
                messagebox.showerror("Error", f"Failed to activate Stay_Awake: {e}")
            sys.exit(1)
    
    def cleanup(self):
        """Cleanup function - ensures wakepy context is properly closed"""
        if self.running and self.keep_awake_context:
            print("Cleaning up - restoring normal power management...")
            try:
                self.keep_awake_context.__exit__(None, None, None)
                self.running = False
                self.keep_awake_context = None
                print("Normal power management restored")
            except Exception as e:
                print(f"Error during cleanup: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle system signals (Ctrl+C, terminate, etc.)"""
        print(f"Received signal {signum}, cleaning up...")
        self.cleanup()
        
        # Ensure tray icon is removed
        if self.icon:
            try:
                self.icon.visible = False
                self.icon.stop()
            except:
                pass  # Icon might already be stopped
        
        sys.exit(0)
    
    def quit_application(self, icon, item):
        """Quit the application cleanly"""
        print("User requested quit via tray menu")
        self.cleanup()
        
        # Close main window if it exists
        if self.main_window:
            try:
                self.main_window.quit()
                self.main_window.destroy()
            except:
                pass
        
        # Ensure icon is removed from system tray
        if self.icon:
            self.icon.visible = False  # Hide icon immediately
            self.icon.stop()           # Stop the icon thread
        
        # Small delay to ensure tray cleanup completes
        time.sleep(0.1)
        sys.exit(0)
    
    def show_about(self, icon, item):
        """Show about dialog"""
        # Create a temporary Tk window for the messagebox
        temp_root = tk.Tk()
        temp_root.withdraw()
        temp_root.attributes('-topmost', True)  # Keep on top
        
        messagebox.showinfo(
            "About Stay_Awake", 
            "Stay_Awake System Tray Application v1.1\n\n"
            "Prevents system sleep and hibernation while allowing\n"
            "Display Monitor sleep for power savings.\n\n"
            "Click the tray icon to show the main window.\n"
            "Right-click for this menu.",
            parent=temp_root
        )
        
        # Ensure proper cleanup
        temp_root.quit()
        temp_root.destroy()
    
    def create_tray_icon(self):
        """Create and run the system tray icon"""
        image = self.create_image()
        
        menu = pystray.Menu(
            item('Show Window', self.show_main_window, default=True),
            item('About', self.show_about),
            pystray.Menu.SEPARATOR,
            item('Quit', self.quit_application)
        )
        
        self.icon = pystray.Icon("Stay_Awake", image, "Stay_Awake - System Awake", menu)
        
        # Set up left-click to show window
        self.icon.default_action = self.show_main_window
        
        # Run the icon (this blocks)
        self.icon.run()
    
    def run(self):
        """Main run method"""
        # Start Stay_Awake functionality
        self.start_Stay_Awake()
        
        # Create main window
        self.create_main_window()
        
        # Start tray icon in separate thread
        tray_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        tray_thread.start()
        
        # Show main window initially
        self.main_window.mainloop()


def main():
    """Main entry point"""
    try:
        app = Stay_AwakeTrayApp()
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Ensure cleanup happens and tray icon is removed
        print("Final cleanup...")
        sys.exit(1)

if __name__ == "__main__":
    main()
