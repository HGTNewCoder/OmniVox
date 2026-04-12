import argparse
import socket
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "GPIO button daemon (Raspberry Pi only). "
            "Watches a GPIO input pin and sends a UDP 'TOGGLE' message to the app."  # noqa: E501
        )
    )
    parser.add_argument("--pin", type=int, default=17, help="BCM GPIO pin number (default: 17)")
    parser.add_argument("--host", default="127.0.0.1", help="App host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5678, help="App UDP port (default: 5678)")
    parser.add_argument(
        "--bouncetime",
        type=int,
        default=300,
        help="Debounce time in ms for the button (default: 300)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        import RPi.GPIO as GPIO  # type: ignore[reportMissingImports]
    except Exception as exc:  # pragma: no cover
        print("RPi.GPIO is not available in this environment.")
        print("Run this script on a Raspberry Pi (Raspberry Pi OS).")
        print(f"Import error: {type(exc).__name__}: {exc}")
        return 1

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    target = (args.host, args.port)

    def on_press(_channel: int) -> None:
        try:
            sock.sendto(b"TOGGLE\n", target)
        except Exception as exc:
            print(f"Failed to send UDP message: {type(exc).__name__}: {exc}")

    print(f"GPIO daemon started. Pin BCM {args.pin} -> UDP {args.host}:{args.port}")
    print("Press Ctrl+C to stop.")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(args.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(args.pin, GPIO.FALLING, callback=on_press, bouncetime=args.bouncetime)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return 0
    finally:
        try:
            GPIO.cleanup()
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
