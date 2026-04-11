import pyttsx3


DEFAULT_TEXT = {
	"en": "Hello, this is an offline English voice test.",
	"th": "สวัสดีครับ นี่คือการทดสอบเสียงภาษาไทยแบบออฟไลน์",
}


def pick_voice(engine, language_code):
	"""Select an English or Thai voice if one exists on this machine."""
	language_code = language_code.lower().strip()
	for voice in engine.getProperty("voices"):
		blob = f"{voice.id} {voice.name}".lower()
		if language_code == "th" and ("thai" in blob or "th-" in blob or " th" in blob):
			engine.setProperty("voice", voice.id)
			return voice
		if language_code == "en" and ("english" in blob or "en-" in blob or " en" in blob):
			engine.setProperty("voice", voice.id)
			return voice
	return None


def speak_text(text, language_code):
	engine = pyttsx3.init()
	selected_voice = pick_voice(engine, language_code)

	# Use a slightly slower pace for clearer pronunciation.
	engine.setProperty("rate", 150 if language_code == "th" else 170)

	if selected_voice:
		print(f"Using {language_code} voice: {selected_voice.name}")
	else:
		print(f"No {language_code} voice found. Using default system voice.")

	engine.say(text)
	engine.runAndWait()


def choose_language():
	choice = input("Choose language ('en' for English, 'th' for Thai): ").strip().lower()
	if choice in ("en", "th"):
		return choice
	print("Invalid choice. Defaulting to English ('en').")
	return "en"


if __name__ == "__main__":
	lang = choose_language()
	user_text = input("Enter text to speak (leave blank to use a default sample): ").strip()
	text_to_speak = user_text if user_text else DEFAULT_TEXT[lang]
	speak_text(text_to_speak, lang)
