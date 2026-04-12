import os
import time
from gpiozero import Button
from signal import pause
import subprocess

# --- CONFIGURATION ---
IDLE_TIMEOUT_SECONDS = 300  # 5 minutes (300 seconds)
BUTTON_GPIO = 17            # Physical Pin 11
# ---------------------

class PhoneStyleScreenManager:
    def __init__(self):
        # Initialize button with internal Pull-Up resistor enabled
        self.button = Button(BUTTON_GPIO, pull_up=True)
        self.is_on = True
        self.last_activity = time.time()
        
        # Link button press to the toggle function
        self.button.when_pressed = self.toggle_screen
        
        # Find the backlight device path (Waveshare usually shows as 10-0045 or similar)
        self.bl_path = self._get_backlight_path()

    def _get_backlight_path(self):
        base = "/sys/class/backlight/"
        dirs = os.listdir(base)
        if dirs:
            # Returns the first backlight found (usually the DSI screen)
            return os.path.join(base, dirs[0], "brightness")
        return None

    def set_backlight(self, state):
        """0 is off, 255 is full brightness"""
        if not self.bl_path: return
        
        val = "255" if state else "0"
        try:
            # Using sudo tee because sysfs requires root permissions
            subprocess.run(['bash', '-c', f'echo {val} | sudo tee {self.bl_path}'], check=True, capture_output=True)
            self.is_on = state
            print(f"Backlight {'ON' if state else 'OFF'}")
        except Exception as e:
            print(f"Error: {e}")

    def toggle_screen(self):
        print("Button pressed!")
        self.last_activity = time.time()
        self.set_backlight(not self.is_on)

    def monitor(self):
        while True:
            # Sleep if idle for too long
            if self.is_on and (time.time() - self.last_activity > IDLE_TIMEOUT_SECONDS):
                print("Idle timeout reached.")
                self.set_backlight(False)
            
            time.sleep(1)

if __name__ == "__main__":
    manager = PhoneStyleScreenManager()
    print(f"Manager active. GPIO {BUTTON_GPIO} monitoring...")
    try:
        manager.monitor()
    except KeyboardInterrupt:
        print("Exiting...")