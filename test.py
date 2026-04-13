from gpiozero import Button
from time import sleep

BUTTON_GPIO = 17  # Physical pin 11


def main():
	button = Button(BUTTON_GPIO, pull_up=True, bounce_time=0.05)

	button.when_pressed = lambda: print("Button pressed")
	button.when_released = lambda: print("Button released")

	print(f"Listening for button presses on GPIO {BUTTON_GPIO}...")

	while True:
		sleep(1)


if __name__ == "__main__":
	main()
