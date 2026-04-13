from gpiozero import Button
from signal import pause

# List of GPIO pins to monitor (BCM numbering)
GPIO_PINS = [11, 17, 27, 22, 23, 24, 25]
buttons = {}

print("Testing multiple GPIO pins - Press Ctrl+C to exit")
print("-" * 40)
print(f"Monitoring pins: {GPIO_PINS}")
print("-" * 40)

# Create button handlers for each pin
for pin in GPIO_PINS:
    try:
        button = Button(pin)
        buttons[pin] = button
        
        def on_press(p=pin):
            print(f"Pin {p}: PRESSED")
        
        def on_release(p=pin):
            print(f"Pin {p}: RELEASED")
        
        button.when_pressed = on_press
        button.when_released = on_release
    except Exception as e:
        print(f"Failed to initialize pin {pin}: {e}")

print(f"Successfully initialized {len(buttons)} pin(s)")
pause()  # Keep the script running