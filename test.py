from gpiozero import Button, Device
from time import sleep

try:
	from gpiozero.pins.lgpio import LGPIOFactory
except Exception:
	LGPIOFactory = None

try:
	from gpiozero.pins.rpigpio import RPiGPIOFactory
except Exception:
	RPiGPIOFactory = None

try:
	from gpiozero.pins.mock import MockFactory
except Exception:
	MockFactory = None

BUTTON_GPIO = 17  # Physical pin 11


def configure_pin_factory():
	if LGPIOFactory is not None:
		Device.pin_factory = LGPIOFactory()
		return "LGPIOFactory"

	if RPiGPIOFactory is not None:
		Device.pin_factory = RPiGPIOFactory()
		return "RPiGPIOFactory"

	if MockFactory is not None:
		Device.pin_factory = MockFactory()
		return "MockFactory"

	raise RuntimeError("No gpiozero pin factory is available.")


def main():
	factory_name = configure_pin_factory()
	button = Button(BUTTON_GPIO, pull_up=True, bounce_time=0.05)

	button.when_pressed = lambda: print("Button pressed")
	button.when_released = lambda: print("Button released")

	print(f"Listening for button presses on GPIO {BUTTON_GPIO} using {factory_name}...")
	if factory_name == "MockFactory":
		print("MockFactory is active, so this will not read a real GPIO button.")

	while True:
		sleep(1)


if __name__ == "__main__":
	main()
