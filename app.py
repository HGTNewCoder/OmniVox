import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout,
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QPushButton, QMessageBox, QStackedWidget, QTimeEdit,
                             QGraphicsDropShadowEffect, QScrollArea, QScroller, QSizePolicy,
                             QGraphicsOpacityEffect)
from PyQt6.QtGui import QFont, QPixmap, QColor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QDate, QTimer, QTime, QUrl, QRectF, QPropertyAnimation, QEasingCurve
from PyQt6.QtMultimedia import QSoundEffect

# ==========================================
# HARDCODED TRANSLATION DICTIONARY
# ==========================================
THAI_TRANSLATIONS = {
    # --- Main menu & headers ---
    "MY DAILY WELL-BEING": "ความเป็นอยู่ที่ดีของฉัน",
    "FOOD": "อาหาร",
    "Request food or specify meal type.": "ขออาหารหรือระบุเมนู",
    "FEELING": "ความรู้สึก",
    "Describe current mood and emotion.": "บอกความรู้สึกของคุณ",
    "POSITION & COMFORT": "ตำแหน่งและความสะดวก",
    "Adjust my bed or change my position.": "ปรับเตียงหรือเปลี่ยนท่าทางให้หน่อย",
    "BATHROOM": "ห้องน้ำ",
    "Request bathroom assistance.": "ขอความช่วยเหลือห้องน้ำ",
    "YES / NO": "ใช่ / ไม่ใช่",
    "Confirmatory responses for staff.": "ตอบตกลงหรือปฏิเสธ",
    "ENTERTAINMENT": "ความบันเทิง",
    "Request leisure activity or TV.": "ขอความบันเทิง",
    "RECOMMEND ANSWER": "แนะนำคำตอบ",
    "Suggestion from staff or system.": "แนะนำโดยระบบ",
    "CLOCK": "นาฬิกา",
    "Check the time or daily schedule.": "เช็คเวลาหรือตาราง",
    "CALL FOR HELP": "ขอความช่วยเหลือ",
    "Press to alert a staff member immediately.": "กดเพื่อแจ้งเจ้าหน้าที่ทันที",
    "CALL NOW": "เรียกเลย",
    "TALK WITH US": "พูดคุยกับเรา",

    # --- Sub-page headers ---
    "FOOD MENU": "เมนูอาหาร",
    "FEELING & MOOD": "ความรู้สึกและอารมณ์",
    "BATHROOM ASSISTANCE": "ความช่วยเหลือห้องน้ำ",
    "RECOMMENDATIONS": "คำแนะนำ",

    # --- Common buttons ---
    "Go Back": "ย้อนกลับ",
    "SELECT": "เลือก",
    "CONFIRM": "ยืนยัน",
    "CANCEL": "ยกเลิก",
    "TURN OFF": "ปิด",

    # --- Bathroom options ---
    "TOILET": "เข้าห้องน้ำ",
    "I need to use the toilet.": "ฉันต้องการเข้าห้องน้ำ",
    "SHOWER": "อาบน้ำ",
    "I would like to take a shower.": "ฉันต้องการอาบน้ำ",
    "WASH": "ล้างหน้า/ล้างมือ",
    "I need to wash my hands/face.": "ฉันต้องการล้างหน้าและมือ",
    "CLOTHES": "เปลี่ยนเสื้อผ้า",
    "I need help changing clothes.": "ฉันต้องการเปลี่ยนเสื้อผ้า",
    "TEETH": "เปลี่ยนผ้าอ้อม",
    "I need to change the diaper.": "ฉันต้องการเปลี่ยนผ้าอ้อม",
    "GROOMING": "จัดแต่งทรงผม",
    "I need help with hair or shaving.": "ฉันต้องการความช่วยเหลือเรื่องทรงผมหรือโกนหนวด",

    # --- Yes / No page ---
    "CHOOSE ANSWER": "เลือกคำตอบ",
    "YES": "ใช่",
    "NO": "ไม่ใช่",

    # --- Clock page ---
    "CLOCK SETTINGS": "ตั้งค่าเวลา",
    "ALARM": "นาฬิกาปลุก",
    "TIMER": "จับเวลา",
    "Tap arrows to set alarm": "แตะลูกศรเพื่อตั้งปลุก",
    "Tap arrows to set duration": "แตะลูกศรเพื่อตั้งเวลา",
    "SET ALARM": "ตั้งปลุก",
    "START TIMER": "เริ่มจับเวลา",
    "Alarm scheduled": "ตั้งนาฬิกาปลุกแล้ว",
    "Rings once — tap bell to dismiss": "ดังครั้งเดียว — แตะกระดิ่งเพื่อปิด",
    "Edit time": "แก้ไขเวลา",
    "Cancel alarm": "ยกเลิกการปลุก",

    # --- Alert / timer ---
    "ALARM!": "เสียงปลุก!",
    "TIMER FINISHED!": "หมดเวลาแล้ว!",
    "Cancel Timer": "ยกเลิกตัวจับเวลา",

    # --- Welcome page ---
    "Good morning, Mr. K.D 👋": "อรุณสวัสดิ์ คุณ K.D 👋",
    "Welcome to your daily well-being check-in": "ยินดีต้อนรับสู่การเช็คอินสุขภาพประจำวัน",
    "How are you feeling today?": "วันนี้คุณรู้สึกอย่างไรบ้าง?",
    "Continue to Menu ➜": "ไปที่เมนูหลัก ➜",

    # --- Mood labels ---
    "Great": "ดีมาก",
    "Good": "ดี",
    "Okay": "พอใช้",
    "Not great": "ไม่ค่อยดี",
    "In pain": "เจ็บปวด",

    # --- Mood reply messages ---
    "You look wonderful today! 😊": "วันนี้คุณดูดีมากเลย! 😊",
    "Glad to hear it! 😊": "ดีใจที่ได้ยินเช่นนั้น! 😊",
    "We are here for you. 💚": "เราอยู่เคียงข้างคุณเสมอ 💚",
    "Let us help you feel better. 🤝": "ขอช่วยให้คุณรู้สึกดีขึ้นนะ 🤝",
    "Staff will be notified right away. 🔔": "เจ้าหน้าที่จะได้รับแจ้งทันที 🔔",

    # --- Position & Comfort items ---
    "Adjust Bed": "ปรับเตียง",
    "Pull Me Up": "พยุงตัวขึ้น",
    "Support Right Arm": "พยุงแขนขวา",
    "Turn Me to My Side": "พลิกตัวตะแคง",
    "Fix Pillows/Cushions": "จัดหมอน/เบาะ",
    "Too Hot / Too Cold": "ร้อนเกินไป / เย็นเกินไป",
    "Transfer to Wheelchair": "ย้ายไปรถเข็น",
    "Transfer to Bed": "ย้ายขึ้นเตียง",
    "Transfer to Commode/Toilet": "ย้ายไปโถสุขภัณฑ์",
    "Move to Recliner": "ย้ายไปเก้าอี้เอนหลัง",

    # --- Feeling items ---
    "Happiness": "ความสุข",
    "Joy": "ปิติยินดี",
    "Painful": "เจ็บปวด",
    "Gratitude": "ความกตัญญู",
    "Relief": "โล่งอก",
    "Pride": "ความภาคภูมิใจ",
    "Confidence": "ความมั่นใจ",
    "Hope": "ความหวัง",
    "Optimism": "มองโลกในแง่ดี",
    "Excitement": "ตื่นเต้น",
    "Enthusiasm": "กระตือรือร้น",
    "Elation": "ปลาบปลื้ม",
    "Bliss": "สุขใจ",
    "Euphoria": "ปีติสุข",
    "Amusement": "สนุกสนาน",
    "Love": "ความรัก",
    "Fondness": "ความชอบพอ",
    "Caring": "ห่วงใย",
    "Compassion": "ความเห็นอกเห็นใจ",
    "Empathy": "การเข้าใจความรู้สึกผู้อื่น",
    "Sympathy": "ความเห็นใจ",
    "Tenderness": "อ่อนโยน",
    "Attachment": "ความผูกพัน",
    "Trust": "ความไว้วางใจ",
    "Admiration": "ชื่นชม",
    "Respect": "เคารพ",
    "Sadness": "เศร้า",
    "Unhappiness": "ไม่มีความสุข",
    "Sorrow": "โศกเศร้า",
    "Grief": "เสียใจ",
    "Depression": "ซึมเศร้า",
    "Despair": "สิ้นหวัง",
    "Hopelessness": "หมดหวัง",
    "Loneliness": "โดดเดี่ยว",
    "Heartbreak": "หัวใจสลาย",
    "Disappointment": "ผิดหวัง",
    "Regret": "เสียใจ/เสียดาย",
    "Guilt": "รู้สึกผิด",
    "Shame": "อับอาย",
    "Embarrassment": "ขายหน้า",
    "Insecurity": "ไม่มั่นใจ",
    "Worthlessness": "ไร้คุณค่า",
    "Neglect": "ถูกทอดทิ้ง",
    "Hurt": "เจ็บใจ",
    "Anger": "โกรธ",
    "Annoyance": "รำคาญ",
    "Irritation": "หงุดหงิด",
    "Frustration": "หัวร้อน",
    "Aggravation": "ขุ่นเคือง",
    "Resentment": "โกรธแค้น",
    "Bitterness": "ขมขื่น",
    "Hatred": "เกลียดชัง",
    "Rage": "พิโรธ",
    "Fury": "เดือดดาล",
    "Hostility": "เป็นปฏิปักษ์",
    "Jealousy": "หึงหวง",
    "Envy": "อิจฉา",
    "Fear": "กลัว",
    "Anxiety": "วิตกกังวล",
    "Worry": "เป็นห่วง",
    "Nervousness": "ประหม่า",
    "Stress": "เครียด",
    "Panic": "ตื่นตระหนก",
    "Terror": "สยดสยอง",
    "Dread": "หวาดกลัว",
    "Apprehension": "กังวลใจ",
    "Unease": "ไม่สบายใจ",
    "Disgust": "รังเกียจ",
    "Revulsion": "สะอิดสะเอียน",
    "Contempt": "경멸 / 경시",
    "Loathing": "ขยะแขยง",
    "Surprise": "ประหลาดใจ",
    "Amazement": "ตะลึงพรึงเพริด",
    "Astonishment": "ตกใจ",
    "Shock": "ช็อค",
    "Curiosity": "อยากรู้อยากเห็น",
    "Interest": "สนใจ",
    "Intrigue": "ถูกดึงดูด",
    "Fascination": "หลงใหล",
    "Boredom": "เบื่อ",
    "Apathy": "เฉยเมย",
    "Indifference": "ไม่แยแส",
    "Confusion": "สับสน",
    "Perplexity": "งุนงง",
    "Doubt": "สงสัย",
    "Uncertainty": "ไม่แน่ใจ",
    "Calmness": "สงบ",
    "Peacefulness": "สันติ",
    "Relaxation": "ผ่อนคลาย",
    "Serenity": "สงบเงียบ",
    "Awe": "ตื้นตัน",
    "Wonder": "อัศจรรย์",
    "Inspiration": "แรงบันดาลใจ",
    "Anticipation": "คาดหวัง",
    "Eagerness": "กระตือรือร้น",
    "Overwhelm": "ท่วมท้น",
    "Restlessness": "กระสับกระส่าย",
    "Nostalgia": "คิดถึงอดีต",
    "Melancholy": "เหงาหงอย",
    "Skepticism": "ไม่เชื่อง่าย",
    "Suspicion": "ระแวง",
    "Acceptance": "ยอมรับ",
    "Forgiveness": "การให้อภัย",
    "Determination": "มุ่งมั่น",
    "Motivation": "แรงจูงใจ",
    "Fulfillment": "พึงพอใจ",
    "Disconnection": "รู้สึกห่างเหิน",
    "Alienation": "แปลกแยก",

    # --- Recommend items ---
    "I need my glasses": "ฉันต้องการแว่นตา",
    "I need my hearing aid": "ฉันต้องการเครื่องช่วยฟัง",
    "My phone needs charging": "โทรศัพท์ของฉันต้องชาร์จ",
    "I dropped something": "ฉันทำของหล่น",
    "I need more light": "ฉันต้องการแสงสว่างเพิ่ม",
    "I need less light": "ฉันต้องการแสงน้อยลง",
    "Please turn off the TV": "กรุณาปิดทีวี",
    "Please turn on the fan": "กรุณาเปิดพัดลม",
    "Please turn off the fan": "กรุณาปิดพัดลม",
    "I need hand sanitizer": "ฉันต้องการเจลล้างมือ",
    "I need tissues": "ฉันต้องการกระดาษทิชชู",
    "I need lip balm": "ฉันต้องการลิปบาล์ม",
    "My mouth is dry": "ปากของฉันแห้ง",
    "I need to spit": "ฉันต้องการบ้วนน้ำลาย",
    "Please clean my hands": "กรุณาทำความสะอาดมือให้ฉัน",
    "I need my dentures": "ฉันต้องการฟันปลอม",
    "Please remove my dentures": "กรุณาถอดฟันปลอมให้ฉัน",
    "I want to see my family": "ฉันอยากพบครอบครัว",
    "I want to see my friend": "ฉันอยากพบเพื่อน",
    "Please ask visitor to leave": "กรุณาขอให้ผู้เยี่ยมออกไป",
    "I want more visitors": "ฉันต้องการให้มีผู้เยี่ยมเพิ่ม",
    "Please take my photo": "กรุณาถ่ายรูปให้ฉัน",
    "Please contact my doctor": "กรุณาติดต่อแพทย์ของฉัน",
    "I want to speak to a nurse": "ฉันต้องการพูดคุยกับพยาบาล",
    "I cannot sleep": "ฉันนอนไม่หลับ",
    "I need a sleep aid": "ฉันต้องการยานอนหลับ",
    "Please be quiet": "กรุณาเงียบ",
    "The light is bothering me": "แสงทำให้ฉันรำคาญ",
    "I want to nap": "ฉันอยากงีบหลับ",
    "I feel well rested": "ฉันรู้สึกพักผ่อนเต็มที่แล้ว",
    "I had a bad dream": "ฉันฝันร้าย",
    "I need my night medication": "ฉันต้องการยากลางคืน",
    "Please speak slowly": "กรุณาพูดช้าๆ",
    "Please repeat that": "กรุณาพูดซ้ำอีกครั้ง",
    "I do not understand": "ฉันไม่เข้าใจ",
    "Please call my family": "กรุณาโทรหาครอบครัวของฉัน",
    "I need a pen and paper": "ฉันต้องการปากกาและกระดาษ",
    "Please write it down": "กรุณาเขียนให้ฉันด้วย",
    "Please show me a picture": "กรุณาให้ฉันดูรูปภาพ",
    "I want to make a phone call": "ฉันต้องการโทรศัพท์",
    "I want to send a message": "ฉันต้องการส่งข้อความ",
    "Please read this to me": "กรุณาอ่านให้ฉันฟัง",
    "I need an interpreter": "ฉันต้องการล่าม",
    "Please be patient with me": "กรุณาอดทนกับฉันด้วย",
    "My bed is uncomfortable": "เตียงของฉันไม่สบาย",
    "I need my blanket": "ฉันต้องการผ้าห่ม",
    "Please raise my bed": "กรุณายกเตียงขึ้น",
    "Please lower my bed": "กรุณาลดเตียงลง",
    "I need more pillows": "ฉันต้องการหมอนเพิ่ม",
}


def translate(text, lang_code):
    if not text:
        return ""
    if lang_code == "en":
        return text
    return THAI_TRANSLATIONS.get(text, text)


# ==========================================
# COMMBOX
# ==========================================
class CommBox(QFrame):
    def __init__(self, title, description, bg_color, media_file, is_bell=False,
                 show_btn=True, large_text=False, add_shadow=False,
                 use_picture=False, hide_title=False, callback=None):
        super().__init__()
        self.is_bell = is_bell
        self.title = title
        self.description = description
        self.original_color = bg_color
        self.media_file = media_file
        self.callback = callback
        self.show_btn = show_btn
        self.large_text = large_text
        self.add_shadow = add_shadow
        self.use_picture = use_picture
        self.hide_title = hide_title
        self.setFrameShape(QFrame.Shape.NoFrame)

        if is_bell or not show_btn or callback:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("QFrame { border: none; border-radius: 20px; background-color: white; }")

        if self.add_shadow:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 40))
            shadow.setOffset(0, 6)
            self.setGraphicsEffect(shadow)

        self.main_v_layout = QVBoxLayout(self)
        self.main_v_layout.setContentsMargins(0, 0, 0, 0)
        self.main_v_layout.setSpacing(0)

        if is_bell:
            self.setup_bell_ui(media_file)
        else:
            self.setup_standard_ui(title, description, bg_color, media_file)

    def setup_bell_ui(self, media_file):
        self.bell_inner_frame = QFrame()
        self.bell_inner_frame.setStyleSheet(
            f"background-color: {self.original_color}; border-radius: 20px; border: none;")
        inner_layout = QHBoxLayout(self.bell_inner_frame)
        inner_layout.setContentsMargins(30, 15, 30, 15)
        inner_layout.setSpacing(25)

        self.bell_display = QLabel()
        if media_file and os.path.exists(media_file):
            pixmap = QPixmap(media_file)
            self.bell_display.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation))
        else:
            self.bell_display.setText("🔔")
            self.bell_display.setFont(QFont("Arial", 50))

        text_v_layout = QVBoxLayout()
        self.bell_title_label = QLabel("CALL FOR HELP")
        self.bell_title_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.bell_title_label.setStyleSheet("color: #8B4513; background: transparent;")

        self.bell_desc_label = QLabel("Press to alert a staff member immediately.")
        self.bell_desc_label.setFont(QFont("Arial", 16))
        self.bell_desc_label.setStyleSheet("color: #555; background: transparent;")

        text_v_layout.addWidget(self.bell_title_label)
        text_v_layout.addWidget(self.bell_desc_label)

        self.call_now_btn_label = QLabel("CALL NOW")
        self.call_now_btn_label.setFixedSize(180, 60)
        self.call_now_btn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.call_now_btn_label.setStyleSheet(
            "background-color: #C0392B; color: white; border-radius: 12px; font-weight: bold; font-size: 20px;")

        inner_layout.addWidget(self.bell_display)
        inner_layout.addLayout(text_v_layout)
        inner_layout.addStretch()
        inner_layout.addWidget(self.call_now_btn_label)
        self.main_v_layout.addWidget(self.bell_inner_frame)

    def setup_standard_ui(self, title, description, bg_color, media_file):
        self.top_half = QFrame()
        self.top_half.setStyleSheet(
            f"background-color: {bg_color}; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none;")
        top_layout = QVBoxLayout(self.top_half)

        if self.use_picture:
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(0)

        if not self.hide_title:
            self.title_label = QLabel(title)
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if self.large_text:
                self.title_label.setFont(QFont("Arial", 26, QFont.Weight.Bold))
                self.title_label.setStyleSheet(
                    "color: #2C4C49; padding: 15px;" if self.use_picture else "color: #2C4C49; padding-top: 10px;")
            else:
                self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                if self.use_picture:
                    self.title_label.setStyleSheet("padding: 10px;")
            top_layout.addWidget(self.title_label)

        if self.use_picture and media_file and os.path.exists(media_file):
            self.pic_frame = QFrame()
            safe_path = media_file.replace('\\', '/')
            self.pic_frame.setStyleSheet(
                f"QFrame {{ border-image: url({safe_path}) 0 0 0 0 stretch stretch; "
                f"border-top-left-radius: 20px; border-top-right-radius: 20px; border: none; }}")
            top_layout.addWidget(self.pic_frame, 1)
        else:
            self.media_display = QLabel()
            self.media_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if media_file and os.path.exists(media_file):
                pixmap = QPixmap(media_file)
                self.media_display.setPixmap(pixmap.scaled(140, 90, Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation))
            else:
                emoji_map = {
                    "TOILET": "🚽", "SHOWER": "🚿", "WASH": "🧼", "CLOTHES": "👕",
                    "FOOD": "🥪", "FEELING": "😊", "POSITION & COMFORT": "💪",
                    "ENTERTAINMENT": "📺", "YES / NO": "✅", "RECOMMEND ANSWER": "💡", "CLOCK": "⏰"
                }
                self.media_display.setText(emoji_map.get(title, "✨"))
                self.media_display.setFont(QFont("Arial", 70 if self.large_text else 40))
            top_layout.addWidget(self.media_display)

        self.bottom_half = QFrame()
        self.bottom_half.setStyleSheet(
            "background-color: white; border-radius: 0px; border: none;")
        bottom_layout = QVBoxLayout(self.bottom_half)
        bottom_layout.addStretch(1)

        self.desc_label = QLabel(description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setFont(
            QFont("Arial", 18 if (self.large_text or self.hide_title) else 15, QFont.Weight.Bold))
        self.desc_label.setStyleSheet("color: #444444;" if (self.large_text or self.hide_title) else "")
        bottom_layout.addWidget(self.desc_label)
        bottom_layout.addStretch(1)

        if self.show_btn:
            self.btn = QPushButton("TALK WITH US")
            self.btn.setFixedHeight(45)
            self.btn.setStyleSheet(
                "QPushButton { background-color: #4D908E; color: white; border-radius: 12px; font-weight: bold; border: none; }")
            self.btn.clicked.connect(self.handle_click)
            bottom_layout.addWidget(self.btn)

        if self.hide_title:
            weights = (75, 25)
        elif self.large_text:
            weights = (60, 40)
        else:
            weights = (40, 60)
        self.main_v_layout.addWidget(self.top_half, weights[0])
        self.main_v_layout.addWidget(self.bottom_half, weights[1])

    def handle_click(self):
        if self.callback:
            self.callback(self.title)

    def mousePressEvent(self, event):
        if self.is_bell:
            self.bell_inner_frame.setStyleSheet(
                "background-color: #900C3F; border-radius: 20px; border: none;")
            QTimer.singleShot(200, lambda: self.bell_inner_frame.setStyleSheet(
                f"background-color: {self.original_color}; border-radius: 20px; border: none;"))
            if self.callback:
                self.callback("BELL")

        elif not self.show_btn:
            if self.hide_title and self.use_picture and hasattr(self, 'pic_frame'):
                safe_path = self.media_file.replace('\\', '/')
                self.pic_frame.setStyleSheet(
                    f"QFrame {{ border-image: url({safe_path}) 0 0 0 0 stretch stretch; "
                    f"border-top-left-radius: 20px; border-top-right-radius: 20px; border: 6px solid #8FC8C2; }}")
            else:
                self.top_half.setStyleSheet(
                    "background-color: #BDBDBD; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none;")
            self.bottom_half.setStyleSheet(
                "background-color: #E0E0E0; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; border: none;")
            QTimer.singleShot(150, self.restore_colors)
            if self.callback:
                self.callback(self.title)

        elif self.show_btn and self.callback:
            self.top_half.setStyleSheet(
                "background-color: #BDBDBD; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none;")
            self.bottom_half.setStyleSheet(
                "background-color: #E0E0E0; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; border: none;")
            QTimer.singleShot(150, self.restore_colors)
            self.callback(self.title)

    def restore_colors(self):
        if self.hide_title and self.use_picture and hasattr(self, 'pic_frame'):
            safe_path = self.media_file.replace('\\', '/')
            self.pic_frame.setStyleSheet(
                f"QFrame {{ border-image: url({safe_path}) 0 0 0 0 stretch stretch; "
                f"border-top-left-radius: 20px; border-top-right-radius: 20px; border: none; }}")
        else:
            self.top_half.setStyleSheet(
                f"background-color: {self.original_color}; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none;")
        self.bottom_half.setStyleSheet(
            "background-color: white; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; border: none;")

    def update_language(self, lang_code):
        if not self.hide_title and hasattr(self, 'title_label'):
            self.title_label.setText(translate(self.title, lang_code))
        if hasattr(self, 'desc_label'):
            self.desc_label.setText(translate(self.description, lang_code))
        if hasattr(self, 'btn'):
            self.btn.setText(translate("TALK WITH US", lang_code))
        if self.is_bell:
            if hasattr(self, 'bell_title_label'):
                self.bell_title_label.setText(translate("CALL FOR HELP", lang_code))
            if hasattr(self, 'bell_desc_label'):
                self.bell_desc_label.setText(translate("Press to alert a staff member immediately.", lang_code))
            if hasattr(self, 'call_now_btn_label'):
                self.call_now_btn_label.setText(translate("CALL NOW", lang_code))


# ==========================================
# PAGE 11: FULL SCREEN ITEM PAGE
# ==========================================
class FullScreenItemPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._back_index = 1
        self._image_prefix = ""
        self._item_index = 0
        self._item_name = ""
        self._bg_fallback = "#E8F8F5"
        self._emoji_fallback = "✨"
        self.setStyleSheet("background-color: #E8F8F5;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.image_label, stretch=7)

        self.bottom_bar = QFrame()
        self.bottom_bar.setFixedHeight(140)
        self.bottom_bar.setStyleSheet(
            "background-color: white; border-radius: 0px; border: none;")
        bar_layout = QHBoxLayout(self.bottom_bar)
        bar_layout.setContentsMargins(30, 10, 30, 10)
        bar_layout.setSpacing(20)

        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedSize(150, 70)
        self.back_btn.setStyleSheet("""
            QPushButton { background-color: #BDBDBD; color: white; border-radius: 35px;
                          font-weight: bold; font-size: 20px; border: none; }
            QPushButton:pressed { background-color: #9E9E9E; }
        """)
        self.back_btn.clicked.connect(self._go_back)

        self.name_label = QLabel("")
        self.name_label.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("color: #2C4C49; background: transparent; border: none;")

        self.select_btn = QPushButton("SELECT ✓")
        self.select_btn.setFixedSize(180, 70)
        self.select_btn.setStyleSheet("""
            QPushButton { background-color: #4D908E; color: white; border-radius: 35px;
                          font-weight: bold; font-size: 20px; border: none; }
            QPushButton:pressed { background-color: #3a7a77; }
        """)
        self.select_btn.clicked.connect(self._confirm_selection)

        bar_layout.addWidget(self.back_btn)
        bar_layout.addWidget(self.name_label, stretch=1)
        bar_layout.addWidget(self.select_btn)

        layout.addWidget(self.bottom_bar, stretch=0)

    def show_item(self, item_name, item_index, image_prefix, bg_fallback, emoji_fallback, back_index):
        self._back_index = back_index
        self._image_prefix = image_prefix
        self._item_index = item_index
        self._item_name = item_name
        self._bg_fallback = bg_fallback
        self._emoji_fallback = emoji_fallback

        self.name_label.setText(item_name)

        image_path = f"assets/{image_prefix}_{item_index}.png"
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            screen_w = self.app.width()
            screen_h = self.app.height() - self.bottom_bar.height()
            scaled = pixmap.scaled(screen_w, screen_h,
                                   Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                   Qt.TransformationMode.SmoothTransformation)
            x_off = (scaled.width() - screen_w) // 2
            y_off = (scaled.height() - screen_h) // 4
            cropped = scaled.copy(x_off, y_off, screen_w, screen_h)

            rounded = QPixmap(cropped.size())
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            if painter.isActive():
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                path.addRoundedRect(QRectF(cropped.rect()), 0, 0)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, cropped)
                painter.end()

            self.image_label.setPixmap(rounded)
            self.image_label.setText("")
            self.setStyleSheet("background-color: #1a1a1a;")
            self.image_label.setStyleSheet("background: transparent; border: none;")
        else:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(emoji_fallback)
            self.image_label.setFont(QFont("Arial", 120))
            self.setStyleSheet(f"background-color: {bg_fallback};")
            self.image_label.setStyleSheet(
                f"background-color: {bg_fallback}; color: #2C4C49; border: none;")

    def _go_back(self):
        self.app.stack.setCurrentIndex(self._back_index)

    def _confirm_selection(self):
        self.bottom_bar.setStyleSheet(
            "background-color: #D5F5E3; border-radius: 0px; border: none;")
        QTimer.singleShot(400, lambda: self.app.stack.setCurrentIndex(self._back_index))

    def update_language(self, lang_code):
        self.back_btn.setText(translate("Go Back", lang_code))
        self.select_btn.setText(translate("SELECT", lang_code) + " ✓")


# ==========================================
# PAGE 0: WELCOME PAGE
# ==========================================
class WelcomePage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_lang = "en"
        self.setStyleSheet("background-color: #F0F8F7;")

        main = QVBoxLayout(self)
        main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.setSpacing(0)
        main.setContentsMargins(60, 40, 60, 40)

        self.greeting_frame = QFrame()
        self.greeting_frame.setStyleSheet("background: transparent; border: none;")
        g_layout = QVBoxLayout(self.greeting_frame)
        g_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel("Good morning, Mr. K.D 👋")
        self.name_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #2C4C49; border: none;")

        self.sub_label = QLabel("Welcome to your daily well-being check-in")
        self.sub_label.setFont(QFont("Arial", 20))
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_label.setStyleSheet("color: #4D908E; border: none;")

        g_layout.addWidget(self.name_label)
        g_layout.addWidget(self.sub_label)
        main.addWidget(self.greeting_frame)
        main.addSpacing(10)

        self.status_container = QFrame()
        self.status_container.setStyleSheet("background: transparent; border: none;")
        status_v_layout = QVBoxLayout(self.status_container)
        status_v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_v_layout.setContentsMargins(0, 10, 0, 10)
        status_v_layout.setSpacing(10)

        self.timer_status = QLabel("")
        self.timer_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_status.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        self.cancel_timer_btn = QPushButton("✕ Cancel Timer")
        self.cancel_timer_btn.setFixedSize(200, 40)
        self.cancel_timer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_timer_btn.setStyleSheet("""
            QPushButton { background-color: #C0392B; color: white; border-radius: 10px;
                          font-weight: bold; font-size: 16px; border: none; }
            QPushButton:pressed { background-color: #922B21; }
        """)
        self.cancel_timer_btn.clicked.connect(self.cancel_timer)
        self.cancel_timer_btn.hide()

        status_v_layout.addWidget(self.timer_status, alignment=Qt.AlignmentFlag.AlignCenter)
        status_v_layout.addWidget(self.cancel_timer_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setup_alarm_banner()
        status_v_layout.addWidget(self.alarm_container, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_container.hide()
        main.addWidget(self.status_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main.addSpacing(10)

        self.question_label = QLabel("How are you feeling today?")
        self.question_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setStyleSheet("color: #2C4C49; border: none;")
        main.addWidget(self.question_label)
        main.addSpacing(20)

        moods_frame = QFrame()
        moods_frame.setStyleSheet("background: transparent; border: none;")
        moods_h = QHBoxLayout(moods_frame)
        moods_h.setSpacing(20)
        moods_h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mood_data = [
            ("😄", "Great",     "#D5F5E3", "#4D908E"),
            ("🙂", "Good",      "#AED6F1", "#2471A3"),
            ("😐", "Okay",      "#F9E79F", "#B7950B"),
            ("😔", "Not great", "#FADBD8", "#A93226"),
            ("😣", "In pain",   "#EBDEF0", "#76448A"),
        ]
        self.mood_buttons = []
        self.mood_text_labels = []   # store the text QLabel for each mood button

        for emoji, label, bg, fg in self.mood_data:
            btn_frame = QFrame()
            btn_frame.setStyleSheet(
                "background-color: white; border: 2px solid #8FC8C2; border-radius: 20px;")
            btn_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_frame.setFixedSize(140, 140)

            bv = QVBoxLayout(btn_frame)
            bv.setAlignment(Qt.AlignmentFlag.AlignCenter)

            e_lbl = QLabel(emoji)
            e_lbl.setFont(QFont("Arial", 42))
            e_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e_lbl.setStyleSheet("border: none; background: transparent;")

            t_lbl = QLabel(label)
            t_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t_lbl.setStyleSheet(f"color: {fg}; border: none; background: transparent;")

            bv.addWidget(e_lbl)
            bv.addWidget(t_lbl)
            btn_frame._bg = bg
            btn_frame._fg = fg
            btn_frame._label = label         # keep the EN key for logic
            btn_frame._text_lbl = t_lbl      # reference to update language
            btn_frame.mousePressEvent = lambda e, f=btn_frame: self.select_mood(f)
            moods_h.addWidget(btn_frame)
            self.mood_buttons.append(btn_frame)
            self.mood_text_labels.append(t_lbl)

        main.addWidget(moods_frame)
        main.addSpacing(20)

        self.reply_label = QLabel("")
        self.reply_label.setFont(QFont("Arial", 18))
        self.reply_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reply_label.setStyleSheet("color: #4D908E; border: none;")
        main.addWidget(self.reply_label)
        main.addSpacing(20)

        self.continue_btn = QPushButton("Continue to Menu ➜")
        self.continue_btn.setFixedSize(320, 70)
        self.continue_btn.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.continue_btn.setStyleSheet("""
            QPushButton { background-color: #4D908E; color: white; border-radius: 35px; border: none; }
            QPushButton:pressed { background-color: #3a7a77; }
        """)
        self.continue_btn.clicked.connect(lambda: self.app.stack.setCurrentIndex(1))
        main.addWidget(self.continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._set_opacity(self.greeting_frame, 0)
        self._set_opacity(self.question_label, 0)
        for mb in self.mood_buttons:
            self._set_opacity(mb, 0)
        self._set_opacity(self.continue_btn, 0)
        QTimer.singleShot(200, self.animate_in)

    def setup_alarm_banner(self):
        self.alarm_container = QFrame()
        self.alarm_container.setFixedSize(600, 160)
        self.alarm_container.setStyleSheet("""
            QFrame { background-color: #FEF3E2; border-radius: 16px; border-left: 6px solid #E8A838; }
        """)

        alarm_outer = QHBoxLayout(self.alarm_container)
        alarm_outer.setContentsMargins(16, 12, 16, 12)
        alarm_outer.setSpacing(16)

        icon_label = QLabel("🔔")
        icon_label.setFont(QFont("Arial", 32))
        icon_label.setStyleSheet("border: none; background: transparent;")
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alarm_outer.addWidget(icon_label)

        text_block = QVBoxLayout()
        text_block.setSpacing(2)

        self.alarm_scheduled_label = QLabel("Alarm scheduled")
        self.alarm_scheduled_label.setFont(QFont("Arial", 13))
        self.alarm_scheduled_label.setStyleSheet("color: #8B6914; border: none; background: transparent;")

        self.alarm_status = QLabel("")
        self.alarm_status.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.alarm_status.setStyleSheet("color: #5C3D0E; border: none; background: transparent;")

        self.alarm_sub_label = QLabel("Rings once — tap bell to dismiss")
        self.alarm_sub_label.setFont(QFont("Arial", 12))
        self.alarm_sub_label.setStyleSheet("color: #A07830; border: none; background: transparent;")

        text_block.addWidget(self.alarm_scheduled_label)
        text_block.addWidget(self.alarm_status)
        text_block.addWidget(self.alarm_sub_label)
        alarm_outer.addLayout(text_block, stretch=1)

        btn_block = QVBoxLayout()
        btn_block.setSpacing(8)

        self.change_time_btn = QPushButton("Edit time")
        self.change_time_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_time_btn.setFixedSize(140, 44)
        self.change_time_btn.setStyleSheet("""
            QPushButton { background-color: white; color: #5C3D0E; border-radius: 10px;
                          border: 1.5px solid #D4A84B; font-size: 15px; font-weight: bold; }
            QPushButton:pressed { background-color: #F5E6C8; }
        """)
        self.change_time_btn.clicked.connect(lambda: self.app.stack.setCurrentIndex(9))

        self.cancel_alarm_btn = QPushButton("Cancel alarm")
        self.cancel_alarm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_alarm_btn.setFixedSize(140, 44)
        self.cancel_alarm_btn.setStyleSheet("""
            QPushButton { background-color: white; color: #5C3D0E; border-radius: 10px;
                          border: 1.5px solid #D4A84B; font-size: 15px; font-weight: bold; }
            QPushButton:pressed { background-color: #F5E6C8; }
        """)
        self.cancel_alarm_btn.clicked.connect(self.cancel_alarm)

        btn_block.addWidget(self.change_time_btn)
        btn_block.addWidget(self.cancel_alarm_btn)
        alarm_outer.addLayout(btn_block)

        self.alarm_container.hide()

    def update_status_visibility(self):
        if self.alarm_container.isHidden() and self.cancel_timer_btn.isHidden():
            self.status_container.hide()
        else:
            self.status_container.show()

    def cancel_timer(self):
        self.app.timer_seconds_remaining = 0
        self.timer_status.setText("")
        self.timer_status.setStyleSheet("")
        self.cancel_timer_btn.hide()
        self.update_status_visibility()

    def cancel_alarm(self):
        self.app.active_alarm_time = None
        self.alarm_status.setText("")
        self.alarm_container.hide()
        self.update_status_visibility()

    def _set_opacity(self, widget, val):
        eff = QGraphicsOpacityEffect()
        eff.setOpacity(val)
        widget.setGraphicsEffect(eff)

    def _fade_in(self, widget, duration):
        eff = QGraphicsOpacityEffect()
        eff.setOpacity(0)
        widget.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def animate_in(self):
        steps = [
            (self.greeting_frame, 600),
            (self.question_label, 500),
        ] + [(mb, 400) for mb in self.mood_buttons] + [
            (self.continue_btn, 400),
        ]
        delays = [0, 700, 1300, 1500, 1700, 1900, 2100, 2600]
        for i, (widget, duration) in enumerate(steps):
            d = delays[i] if i < len(delays) else 2600
            QTimer.singleShot(d, lambda w=widget, dur=duration: self._fade_in(w, dur))

    def select_mood(self, frame):
        replies = {
            "Great":    "You look wonderful today! 😊",
            "Good":     "Glad to hear it! 😊",
            "Okay":     "We are here for you. 💚",
            "Not great":"Let us help you feel better. 🤝",
            "In pain":  "Staff will be notified right away. 🔔",
        }
        for mb in self.mood_buttons:
            mb.setStyleSheet(
                "background-color: white; border: 2px solid #8FC8C2; border-radius: 20px;")
        frame.setStyleSheet(
            f"background-color: {frame._bg}; border: 2px solid {frame._fg}; border-radius: 20px;")

        reply_key = replies.get(frame._label, "")
        self.reply_label.setText(translate(reply_key, self.current_lang))

        if frame._label == "In pain":
            QTimer.singleShot(1000, lambda: QMessageBox.warning(
                self, "Alert", "Staff Alerted — patient reports pain!"))
            QTimer.singleShot(2500, lambda: self.app.stack.setCurrentIndex(1))
        else:
            QTimer.singleShot(1000, lambda: self.app.stack.setCurrentIndex(1))

    def update_language(self, lang_code):
        self.current_lang = lang_code
        # greeting
        self.name_label.setText(translate("Good morning, Mr. K.D 👋", lang_code))
        self.sub_label.setText(translate("Welcome to your daily well-being check-in", lang_code))
        # question
        self.question_label.setText(translate("How are you feeling today?", lang_code))
        # continue button
        self.continue_btn.setText(translate("Continue to Menu ➜", lang_code))
        # cancel timer button
        self.cancel_timer_btn.setText("✕ " + translate("Cancel Timer", lang_code))
        # mood labels
        for btn_frame in self.mood_buttons:
            btn_frame._text_lbl.setText(translate(btn_frame._label, lang_code))
        # alarm banner
        self.alarm_scheduled_label.setText(translate("Alarm scheduled", lang_code))
        self.alarm_sub_label.setText(translate("Rings once — tap bell to dismiss", lang_code))
        self.change_time_btn.setText(translate("Edit time", lang_code))
        self.cancel_alarm_btn.setText(translate("Cancel alarm", lang_code))


# ==========================================
# PAGE 1: MAIN MENU
# ==========================================
class MainMenuPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #F0F8F7;")
        self.main_layout = QVBoxLayout(self)

        self.header_container = QFrame()
        self.header_container.setFixedHeight(120)
        self.header_container.setStyleSheet("background-color: #8FC8C2; border: none;")
        header_h_layout = QHBoxLayout(self.header_container)
        header_h_layout.setContentsMargins(20, 15, 20, 15)

        text_v_layout = QVBoxLayout()

        self.header_label = QLabel("MY DAILY WELL-BEING")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        self.header_label.setStyleSheet("color: #2C4C49;")

        self.date_label = QLabel(QDate.currentDate().toString('dddd, MMMM d, yyyy'))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setFont(QFont("Arial", 18))
        self.date_label.setStyleSheet("color: #2C4C49;")

        text_v_layout.addWidget(self.header_label)
        text_v_layout.addWidget(self.date_label)

        header_h_layout.addStretch(1)
        header_h_layout.addLayout(text_v_layout)
        header_h_layout.addStretch(1)

        self.lang_btn = QPushButton("ENGLISH")
        self.lang_btn.setFixedSize(160, 60)
        self.lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang_btn.setStyleSheet("""
            QPushButton { background-color: white; color: #2C4C49; border-radius: 15px;
                          font-weight: bold; font-size: 18px; border: none; }
            QPushButton:pressed { background-color: #E0E0E0; }
        """)
        self.lang_btn.clicked.connect(self.toggle_language)
        header_h_layout.addWidget(self.lang_btn)

        self.main_layout.addWidget(self.header_container)

        self.grid = QGridLayout()
        self.grid.setContentsMargins(25, 10, 25, 10)
        self.grid.setSpacing(20)

        self.card_data = [
            ("FOOD",             "Request food or specify meal type.",     "#AED6F1", "assets/food.png",          0, 0),
            ("FEELING",          "Describe current mood and emotion.",     "#F9E79F", "assets/feeling.png",       0, 1),
            ("POSITION & COMFORT",         "Adjust my bed or change my position.",           "#D6EAF8", "assets/position.png",      0, 2),
            ("BATHROOM",         "Request bathroom assistance.",           "#D1F2EB", "assets/bathroom.png",      0, 3),
            ("YES / NO",         "Confirmatory responses for staff.",      "#FADBD8", "assets/yes_no.png",        1, 0),
            ("ENTERTAINMENT",    "Request leisure activity or TV.",        "#D5F5E3", "assets/entertainment.png", 1, 1),
            ("RECOMMEND ANSWER", "Suggestion from staff or system.",       "#FCF3CF", "assets/recommend.png",     1, 2),
            ("CLOCK",            "Check the time or daily schedule.",      "#E8DAEF", "assets/clock.png",         1, 3),
        ]

        self.cards = []
        for title, desc, col, img, r, c in self.card_data:
            card = CommBox(title=title, description=desc, bg_color=col,
                           media_file=img, callback=self.navigate)
            self.cards.append(card)
            self.grid.addWidget(card, r, c)

        self.bell_card = CommBox(title="", description="", bg_color="#FFEADB",
                                 media_file="assets/bell.png", is_bell=True, callback=self.navigate)
        self.grid.addWidget(self.bell_card, 2, 0, 1, 4)

        self.main_layout.addLayout(self.grid)

    def toggle_language(self):
        if self.lang_btn.text() == "ENGLISH":
            self.lang_btn.setText("THAI / ไทย")
            self.app.update_language("th")
        else:
            self.lang_btn.setText("ENGLISH")
            self.app.update_language("en")

    def navigate(self, title):
        pages = {
            "FOOD": 2, "FEELING": 3, "POSITION & COMFORT": 4, "BATHROOM": 5,
            "YES / NO": 6, "ENTERTAINMENT": 7, "RECOMMEND ANSWER": 8
        }
        if title in pages:
            self.app.stack.setCurrentIndex(pages[title])
        elif title == "CLOCK":
            self.app.stack.setCurrentIndex(9)
        elif title == "BELL":
            self.app.trigger_alert("Emergency! Staff has been alerted!")

    def update_language(self, lang_code):
        self.header_label.setText(translate("MY DAILY WELL-BEING", lang_code))
        if lang_code == "th":
            self.date_label.setText(QDate.currentDate().toString('วันddddที่ d MMMM yyyy'))
        else:
            self.date_label.setText(QDate.currentDate().toString('dddd, MMMM d, yyyy'))
        for card in self.cards:
            card.update_language(lang_code)
        self.bell_card.update_language(lang_code)


# ==========================================
# BASE PAGE
# ==========================================
class BasePage(QFrame):
    def __init__(self, app, title):
        super().__init__()
        self.app = app
        self.original_title = title
        self.setStyleSheet("background-color: #F0F8F7;")
        layout = QVBoxLayout(self)
        self.header = QLabel(title)
        self.header.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("color: #2C4C49;")
        layout.addWidget(self.header)
        layout.addStretch()
        self.back_btn = QPushButton("Go Back")
        self.back_btn.setFixedSize(200, 60)
        self.back_btn.setStyleSheet(
            "background-color: #BDBDBD; color: white; border-radius: 15px; "
            "font-weight: bold; font-size: 20px; border: none;")
        self.back_btn.clicked.connect(lambda: self.app.stack.setCurrentIndex(1))
        layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.page_layout = layout

    def update_language(self, lang_code):
        self.header.setText(translate(self.original_title, lang_code))
        self.back_btn.setText(translate("Go Back", lang_code))


# ==========================================
# SHARED BIG SCREEN MIXIN
# ==========================================
def build_big_screen_page(page, items, image_prefix, border_color, bg_fallback):
    page.current_index = 0
    page._is_rendering = False

    page.big_screen = QLabel()
    page.big_screen.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
    page.big_screen.setMinimumHeight(250)
    page.big_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
    page.big_screen.setStyleSheet("background-color: transparent; border: none;")
    page.page_layout.insertWidget(1, page.big_screen)

    page.scroll_area = QScrollArea()
    page.scroll_area.setFixedHeight(180)
    page.scroll_area.setWidgetResizable(True)
    page.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    page.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    page.scroll_area.horizontalScrollBar().setStyleSheet(
        "QScrollBar {height:0px; background: transparent;}")
    page.scroll_area.setStyleSheet("border: none; background: transparent;")
    QScroller.grabGesture(page.scroll_area.viewport(),
                          QScroller.ScrollerGestureType.LeftMouseButtonGesture)

    page.container_widget = QWidget()
    page.container_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    page.h_layout = QHBoxLayout(page.container_widget)
    page.h_layout.setSpacing(15)
    page.h_layout.setContentsMargins(10, 5, 10, 5)

    page.box_size = 140
    page.total_step = page.box_size + 15
    page._image_prefix = image_prefix
    page._items = items
    page._bg_fallback = bg_fallback
    page._box_widgets = []   # store box + label pairs for language update

    for i, item_name in enumerate(items):
        box = QPushButton(page.container_widget)
        box.setFixedSize(page.box_size, page.box_size)
        label = QLabel(item_name, box)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedSize(page.box_size, page.box_size)
        label.setStyleSheet(
            "padding: 10px; font-weight: bold; font-size: 13px; "
            "color: #2C4C49; border: none; background: transparent;")
        box.setStyleSheet(f"""
            QPushButton {{ background-color: #ffffff; border: 2px solid {border_color}; border-radius: 18px; }}
            QPushButton:pressed {{ background-color: {border_color}; }}
        """)
        box.clicked.connect(lambda checked, idx=i: page.on_box_clicked(idx))
        page.h_layout.addWidget(box)
        page._box_widgets.append((item_name, label))   # (original EN name, label widget)

    page.scroll_area.setWidget(page.container_widget)
    page.page_layout.insertWidget(2, page.scroll_area)
    page.page_layout.setStretchFactor(page.big_screen, 1)
    page.page_layout.setStretchFactor(page.scroll_area, 0)
    page.scroll_area.horizontalScrollBar().valueChanged.connect(page.handle_scroll_update)
    page.page_layout.setContentsMargins(25, 5, 25, 15)


def update_big_screen_shared(page, index):
    if page._is_rendering:
        return
    page._is_rendering = True
    w = page.big_screen.width()
    h = page.big_screen.height()
    if w <= 0 or h <= 0:
        page._is_rendering = False
        return

    image_path = f"assets/{page._image_prefix}_{index}.png"
    if os.path.exists(image_path):
        pixmap = QPixmap(image_path)
        scaled = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
        x_offset = (scaled.width() - w) // 2
        y_offset = (scaled.height() - h) // 4
        cropped = scaled.copy(x_offset, y_offset, w, h)

        rounded_pixmap = QPixmap(cropped.size())
        rounded_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded_pixmap)
        if painter.isActive():
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(cropped.rect()), 25.0, 25.0)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, cropped)
            painter.end()

        page.big_screen.setPixmap(rounded_pixmap)
        page.big_screen.setText("")
        page.big_screen.setStyleSheet("background-color: transparent; border: none;")
    else:
        page.big_screen.setPixmap(QPixmap())
        lang = getattr(page.app, '_current_lang', 'en')
        page.big_screen.setText(translate(page._items[index], lang))
        page.big_screen.setStyleSheet(
            f"background-color: {page._bg_fallback}; color: #2C4C49; font-size: 36px; "
            f"font-weight: bold; border-radius: 25px; border: none; padding: 20px;")
    page._is_rendering = False


def open_fullscreen_for_page(page, idx, back_page_index):
    emoji_map = {
        "food":          "🍽️",
        "feeling":       "😊",
        "entertainment": "📺",
        "recommend":     "💡",
        "position":      "💪",
    }
    emoji = emoji_map.get(page._image_prefix, "✨")
    lang = getattr(page.app, '_current_lang', 'en')
    display_name = translate(page._items[idx], lang)
    page.app.fullscreen_item_page.show_item(
        item_name=display_name,
        item_index=idx,
        image_prefix=page._image_prefix,
        bg_fallback=page._bg_fallback,
        emoji_fallback=emoji,
        back_index=back_page_index,
    )
    page.app.stack.setCurrentIndex(11)


def big_screen_update_language(page, lang_code):
    """Update the thumbnail label text for scrollable pages."""
    for original_name, label in page._box_widgets:
        label.setText(translate(original_name, lang_code))


# ==========================================
# FOOD PAGE (index 2)
# ==========================================
class FoodPage(BasePage):
    def __init__(self, app):
        super().__init__(app, "FOOD MENU")
        self.menu_items = [
            "Pad Kra Pao (Basil Stir-Fry)",
            "Gai Pad Med Mamuang (Cashew Chicken)",
            "Pad Kana Moo Krob (Crispy Pork Belly with Chinese Broccoli)",
            "Pad Prik King (Dry Red Curry Stir-Fry)",
            "Pad Pak Ruam (Mixed Vegetable Stir-Fry)",
            "Moo Ping (Grilled Pork Skewers)",
            "Tod Mun Pla (Thai Fish Cakes)",
            "Gaeng Keow Wan (Green Curry)",
            "Gaeng Daeng (Red Curry)",
            "Gaeng Massaman (Massaman Curry)",
            "Gaeng Panang (Panang Curry)",
            "Gaeng Som (Sour Curry)",
            "Gaeng Phed Ped Yang (Roast Duck Red Curry)",
            "Pad Thai",
            "Pad See Ew (Stir-Fried Wide Noodles)",
            "Pad Kee Mao (Drunken Noodles)",
            "Khao Pad (Thai Fried Rice)",
            "Khao Pad Sapparod (Pineapple Fried Rice)",
            "Khao Man Gai (Hainanese Chicken Rice)",
            "Khao Kha Moo (Braised Pork Leg on Rice)",
            "Khao Soi (Northern Thai Coconut Curry Noodle Soup)",
            "Tom Yum Goong (Spicy and Sour Shrimp Soup)",
            "Tom Kha Gai (Chicken Coconut Soup)",
            "Som Tum (Green Papaya Salad)",
            "Larb (Minced Meat Salad)",
            "Nam Tok Moo (Grilled Pork Salad)",
            "Yum Woon Sen (Glass Noodle Salad)",
            "Poh Pia Tod (Spring Rolls)",
            "Khao Niao Mamuang (Mango Sticky Rice)",
            "Roti Gluay (Banana Roti)",
            "Steak",
            "Hamburger",
            "Pizza",
            "French Fries"
        ]
        build_big_screen_page(self, self.menu_items, "food", "#8FC8C2", "#333333")

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'current_index'):
            update_big_screen_shared(self, self.current_index)

    def on_box_clicked(self, idx):
        self.current_index = idx
        update_big_screen_shared(self, idx)
        self.scroll_area.horizontalScrollBar().setValue(idx * self.total_step)
        open_fullscreen_for_page(self, idx, back_page_index=2)

    def handle_scroll_update(self, value):
        index = round(value / self.total_step)
        if 0 <= index < len(self._items) and index != self.current_index:
            self.current_index = index
            update_big_screen_shared(self, index)

    def update_big_screen(self, index):
        update_big_screen_shared(self, index)

    # Food names are intentionally NOT translated (as per user request)


# ==========================================
# FEELING PAGE (index 3)
# ==========================================
class FeelingPage(BasePage):
    def __init__(self, app):
        super().__init__(app, "FEELING & MOOD")
        self.feeling_items = [
            "Happiness", "Joy", "Painful",
            "Gratitude", "Relief", "Pride", "Confidence", "Hope",
            "Optimism", "Excitement", "Enthusiasm", "Elation", "Bliss", "Euphoria",
            "Amusement", "Love", "Fondness", "Caring", "Compassion",
            "Empathy", "Sympathy", "Tenderness", "Attachment", "Trust", "Admiration",
            "Respect", "Sadness", "Unhappiness", "Sorrow", "Grief", "Depression", "Despair",
            "Hopelessness", "Loneliness", "Heartbreak", "Disappointment", "Regret",
            "Guilt", "Shame", "Embarrassment", "Insecurity", "Worthlessness",
            "Neglect", "Hurt", "Anger", "Annoyance", "Irritation", "Frustration",
            "Aggravation", "Resentment", "Bitterness", "Hatred", "Rage", "Fury", "Hostility",
            "Jealousy", "Envy", "Fear", "Anxiety", "Worry", "Nervousness", "Stress",
            "Panic", "Terror", "Dread", "Apprehension", "Unease",
            "Disgust", "Revulsion", "Contempt", "Loathing",
            "Surprise", "Amazement", "Astonishment", "Shock",
            "Curiosity", "Interest", "Intrigue", "Fascination",
            "Boredom", "Apathy", "Indifference",
            "Confusion", "Perplexity", "Doubt", "Uncertainty",
            "Calmness", "Peacefulness", "Relaxation", "Serenity",
            "Awe", "Wonder", "Inspiration",
            "Anticipation", "Eagerness",
            "Overwhelm", "Restlessness",
            "Nostalgia", "Melancholy",
            "Skepticism", "Suspicion",
            "Acceptance", "Forgiveness",
            "Determination", "Motivation",
            "Fulfillment", "Disconnection", "Alienation"
        ]
        build_big_screen_page(self, self.feeling_items, "feeling", "#F9E79F", "#F9E79F")

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'current_index'):
            update_big_screen_shared(self, self.current_index)

    def on_box_clicked(self, idx):
        self.current_index = idx
        update_big_screen_shared(self, idx)
        self.scroll_area.horizontalScrollBar().setValue(idx * self.total_step)
        open_fullscreen_for_page(self, idx, back_page_index=3)

    def handle_scroll_update(self, value):
        index = round(value / self.total_step)
        if 0 <= index < len(self._items) and index != self.current_index:
            self.current_index = index
            update_big_screen_shared(self, index)

    def update_big_screen(self, index):
        update_big_screen_shared(self, index)

    def update_language(self, lang_code):
        super().update_language(lang_code)
        big_screen_update_language(self, lang_code)


# ==========================================
# POSITION & COMFORT PAGE (index 4)
# ==========================================
class PositionPage(BasePage):
    def __init__(self, app):
        super().__init__(app, "POSITION & COMFORT")
        self.position_items = [
            "Adjust Bed",
            "Pull Me Up",
            "Support Right Arm",
            "Turn Me to My Side",
            "Fix Pillows/Cushions",
            "Too Hot / Too Cold",
            "Transfer to Wheelchair",
            "Transfer to Bed",
            "Transfer to Commode/Toilet",
            "Move to Recliner"
        ]
        build_big_screen_page(self, self.position_items, "position", "#D6EAF8", "#D6EAF8")

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'current_index'):
            update_big_screen_shared(self, self.current_index)

    def on_box_clicked(self, idx):
        self.current_index = idx
        update_big_screen_shared(self, idx)
        self.scroll_area.horizontalScrollBar().setValue(idx * self.total_step)
        open_fullscreen_for_page(self, idx, back_page_index=4)

    def handle_scroll_update(self, value):
        index = round(value / self.total_step)
        if 0 <= index < len(self._items) and index != self.current_index:
            self.current_index = index
            update_big_screen_shared(self, index)

    def update_big_screen(self, index):
        update_big_screen_shared(self, index)

    def update_language(self, lang_code):
        super().update_language(lang_code)
        big_screen_update_language(self, lang_code)


# ==========================================
# ENTERTAINMENT PAGE (index 7)
# ==========================================
class EntertainmentPage(BasePage):
    def __init__(self, app):
        super().__init__(app, "ENTERTAINMENT")
        self.entertainment_items = [
            "ESPN", "ESPN2", "FOX Sports", "NBC Sports", "CBS Sports", "TNT Sports",
            "Peacock", "Netflix", "HBO", "Disney+", "ABC",
            "BBC", "National Geographic", "History Channel",
            "CNN", "Channel 3 (Ch3)", "Channel 7 (Ch7)",
            "ONE 31", "Thai PBS", "Amarin TV",
            "YouTube", "Facebook"
        ]
        build_big_screen_page(self, self.entertainment_items, "entertainment", "#D5F5E3", "#D5F5E3")

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'current_index'):
            update_big_screen_shared(self, self.current_index)

    def on_box_clicked(self, idx):
        self.current_index = idx
        update_big_screen_shared(self, idx)
        self.scroll_area.horizontalScrollBar().setValue(idx * self.total_step)
        open_fullscreen_for_page(self, idx, back_page_index=7)

    def handle_scroll_update(self, value):
        index = round(value / self.total_step)
        if 0 <= index < len(self._items) and index != self.current_index:
            self.current_index = index
            update_big_screen_shared(self, index)

    def update_big_screen(self, index):
        update_big_screen_shared(self, index)

    # Entertainment channel names intentionally NOT translated (as per user request)


# ==========================================
# RECOMMEND PAGE (index 8)
# ==========================================
class RecommendPage(BasePage):
    def __init__(self, app):
        super().__init__(app, "RECOMMENDATIONS")
        self.recommend_items = [
            "I need my glasses", "I need my hearing aid", "My phone needs charging",
            "I dropped something", "I need more light", "I need less light",
            "Please turn off the TV", "Please turn on the fan", "Please turn off the fan",
            "I need hand sanitizer", "I need tissues", "I need lip balm",
            "My mouth is dry", "I need to spit", "Please clean my hands",
            "I need my dentures", "Please remove my dentures",
            "I want to see my family", "I want to see my friend",
            "Please ask visitor to leave", "I want more visitors",
            "Please take my photo", "Please contact my doctor",
            "I want to speak to a nurse", "I cannot sleep", "I need a sleep aid",
            "Please be quiet", "The light is bothering me", "I want to nap",
            "I feel well rested", "I had a bad dream", "I need my night medication",
            "Please speak slowly", "Please repeat that", "I do not understand",
            "Please call my family", "I need a pen and paper", "Please write it down",
            "Please show me a picture", "I want to make a phone call",
            "I want to send a message", "Please read this to me",
            "I need an interpreter", "Please be patient with me",
            "My bed is uncomfortable", "I need my blanket",
            "Please raise my bed", "Please lower my bed", "I need more pillows"
        ]
        build_big_screen_page(self, self.recommend_items, "recommend", "#FCF3CF", "#FCF3CF")

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'current_index'):
            update_big_screen_shared(self, self.current_index)

    def on_box_clicked(self, idx):
        self.current_index = idx
        update_big_screen_shared(self, idx)
        self.scroll_area.horizontalScrollBar().setValue(idx * self.total_step)
        open_fullscreen_for_page(self, idx, back_page_index=8)

    def handle_scroll_update(self, value):
        index = round(value / self.total_step)
        if 0 <= index < len(self._items) and index != self.current_index:
            self.current_index = index
            update_big_screen_shared(self, index)

    def update_big_screen(self, index):
        update_big_screen_shared(self, index)

    def update_language(self, lang_code):
        super().update_language(lang_code)
        big_screen_update_language(self, lang_code)


# ==========================================
# BATHROOM PAGE (index 5)
# ==========================================
class BathroomPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #F0F8F7;")
        layout = QVBoxLayout(self)

        self.header = QLabel("BATHROOM ASSISTANCE")
        self.header.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("padding: 20px; color: #2C4C49;")
        layout.addWidget(self.header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(25)
        grid.setVerticalSpacing(60)
        grid.setContentsMargins(40, 10, 40, 10)

        self.options_data = [
            ("TOILET",   "I need to use the toilet.",         "#AED6F1", "assets/toilet_pic.png",   0, 0),
            ("SHOWER",   "I would like to take a shower.",    "#A2D9CE", "assets/shower_pic.png",   0, 1),
            ("WASH",     "I need to wash my hands/face.",     "#F9E79F", "assets/wash_pic.png",     0, 2),
            ("CLOTHES",  "I need help changing clothes.",     "#D7BDE2", "assets/clothes_pic.png",  1, 0),
            ("TEETH",    "I need to change the diaper.",      "#F5B7B1", "assets/diaper_pic.png",   1, 1),
            ("GROOMING", "I need help with hair or shaving.", "#FAD7A1", "assets/grooming_pic.png", 1, 2),
        ]
        self.cards = []
        for t, d, c, mf, r, col in self.options_data:
            card = CommBox(title=t, description=d, bg_color=c, media_file=mf,
                           show_btn=False, add_shadow=True, use_picture=True,
                           hide_title=True, callback=self.handle_bathroom_selection)
            self.cards.append(card)
            grid.addWidget(card, r, col)

        layout.addLayout(grid)
        self.back_btn = QPushButton("Go Back")
        self.back_btn.setFixedSize(200, 60)
        self.back_btn.setStyleSheet(
            "background-color: #BDBDBD; color: white; border-radius: 15px; "
            "font-weight: bold; font-size: 20px; border: none;")
        self.back_btn.clicked.connect(lambda: self.app.stack.setCurrentIndex(1))
        layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

    def handle_bathroom_selection(self, choice):
        match = next((entry for entry in self.options_data if entry[0] == choice), None)
        if match is None:
            return
        t, d, c, media_file, r, col = match

        emoji_map = {
            "TOILET": "🚽", "SHOWER": "🚿", "WASH": "🧼",
            "CLOTHES": "👕", "TEETH": "🧸", "GROOMING": "💈",
        }
        emoji = emoji_map.get(t, "✨")
        lang = getattr(self.app, '_current_lang', 'en')

        self.app.fullscreen_item_page.show_bathroom_item(
            item_name=translate(t, lang),
            description=translate(d, lang),
            media_file=media_file,
            bg_color=c,
            emoji_fallback=emoji,
            back_index=5,
        )
        self.app.stack.setCurrentIndex(11)

    def update_language(self, lang_code):
        self.header.setText(translate("BATHROOM ASSISTANCE", lang_code))
        self.back_btn.setText(translate("Go Back", lang_code))
        for card in self.cards:
            card.update_language(lang_code)


# ==========================================
# YES/NO PAGE (index 6)
# ==========================================
class YesNoPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)

        self.resp_title = QLabel("CHOOSE ANSWER")
        self.resp_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resp_title.setFont(QFont("Arial", 38, QFont.Weight.Bold))
        self.resp_title.setStyleSheet("color: #2C4C49; border: none;")
        layout.addWidget(self.resp_title)

        self.resp_cards_container = QHBoxLayout()
        self.resp_cards_container.setSpacing(40)

        self.yes_card, self.yes_btn, self.yes_lbl = self.create_styled_response_card(
            "YES", "#D5F5E3", "#4D908E", "assets/yes.png", lambda: self.show_result("YES"))
        self.no_card, self.no_btn, self.no_lbl = self.create_styled_response_card(
            "NO", "#FADBD8", "#A93226", "assets/no.png", lambda: self.show_result("NO"))

        self.resp_cards_container.addWidget(self.yes_card)
        self.resp_cards_container.addWidget(self.no_card)
        layout.addLayout(self.resp_cards_container)

        self.back_btn_resp = QPushButton("Go Back")
        self.back_btn_resp.setFixedSize(150, 50)
        self.back_btn_resp.setStyleSheet(
            "background-color: #BDBDBD; color: white; border-radius: 10px; "
            "font-weight: bold; border: none;")
        self.back_btn_resp.clicked.connect(lambda: self.app.stack.setCurrentIndex(1))
        layout.addWidget(self.back_btn_resp, alignment=Qt.AlignmentFlag.AlignCenter)

        self.result_container = QFrame()
        self.result_container.hide()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_icon = QLabel()
        self.result_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_layout.addWidget(self.result_icon)
        layout.addWidget(self.result_container)

    def create_styled_response_card(self, title, bg_color, btn_color, icon, callback):
        card = QFrame()
        card.setStyleSheet(f"background-color: {bg_color}; border-radius: 40px; border: none;")
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 10, 20, 20)

        lbl_icon = QLabel()
        if os.path.exists(icon):
            lbl_icon.setPixmap(QPixmap(icon).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_icon.setText("✅" if title == "YES" else "❌")
            lbl_icon.setFont(QFont("Arial", 150))
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(lbl_icon)

        t_lbl = QLabel(title)
        t_lbl.setFont(QFont("Arial", 75, QFont.Weight.Bold))
        t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t_lbl.setStyleSheet(f"color: {btn_color}; border: none;")
        v.addWidget(t_lbl)
        v.addStretch()

        btn = QPushButton("CONFIRM")
        btn.setFixedHeight(80)
        btn.setStyleSheet(
            f"background-color: {btn_color}; color: white; border-radius: 25px; "
            f"font-size: 24px; font-weight: bold; border: none;")
        btn.clicked.connect(callback)
        v.addWidget(btn)
        return card, btn, t_lbl

    def show_result(self, choice):
        self.resp_title.hide()
        self.back_btn_resp.hide()
        self.yes_card.hide()
        self.no_card.hide()

        bg = "#D5F5E3" if choice == "YES" else "#FADBD8"
        self.setStyleSheet(f"background-color: {bg}; border: none;")
        icon_path = "assets/yes.png" if choice == "YES" else "assets/no.png"

        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
            self.result_icon.setPixmap(pix)
        else:
            self.result_icon.setText("✅" if choice == "YES" else "❌")
            self.result_icon.setFont(QFont("Arial", 200))

        self.result_icon.show()
        self.result_container.show()
        QTimer.singleShot(3000, self.reset_and_go_home)

    def reset_and_go_home(self):
        self.setStyleSheet("background-color: white; border: none;")
        self.result_container.hide()
        self.resp_title.show()
        self.back_btn_resp.show()
        self.yes_card.show()
        self.no_card.show()
        self.app.stack.setCurrentIndex(1)

    def update_language(self, lang_code):
        self.resp_title.setText(translate("CHOOSE ANSWER", lang_code))
        self.back_btn_resp.setText(translate("Go Back", lang_code))
        self.yes_btn.setText(translate("CONFIRM", lang_code))
        self.no_btn.setText(translate("CONFIRM", lang_code))
        self.yes_lbl.setText(translate("YES", lang_code))
        self.no_lbl.setText(translate("NO", lang_code))


# ==========================================
# CLOCK PAGE (index 9)
# ==========================================
class ClockPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_lang = "en"
        self.setStyleSheet("background-color: #F0F8F7;")

        main_v = QVBoxLayout(self)
        main_v.setContentsMargins(0, 0, 0, 0)

        top_bar = QFrame()
        top_bar.setFixedHeight(120)
        top_bar.setStyleSheet("background-color: #8FC8C2; border: none;")
        top_layout = QHBoxLayout(top_bar)
        self.clock_title = QLabel("CLOCK SETTINGS")
        self.clock_title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.clock_title.setStyleSheet("color: white; border: none;")
        top_layout.addWidget(self.clock_title, alignment=Qt.AlignmentFlag.AlignCenter)
        main_v.addWidget(top_bar)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(100, 20, 100, 20)
        content_layout.setSpacing(20)

        mode_box = QHBoxLayout()
        self.btn_alarm_mode = QPushButton("ALARM")
        self.btn_timer_mode = QPushButton("TIMER")
        for b in [self.btn_alarm_mode, self.btn_timer_mode]:
            b.setFixedSize(300, 80)
            b.setCheckable(True)
            b.setStyleSheet("""
                QPushButton { background-color: #D1E8E5; border-radius: 40px; font-weight: bold;
                              font-size: 26px; color: #2C4C49; border: none; }
                QPushButton:checked { background-color: #2C4C49; color: white; }
            """)
        self.btn_alarm_mode.setChecked(True)
        self.btn_alarm_mode.clicked.connect(lambda: self.switch_clock_mode("ALARM"))
        self.btn_timer_mode.clicked.connect(lambda: self.switch_clock_mode("TIMER"))
        mode_box.addWidget(self.btn_alarm_mode)
        mode_box.addWidget(self.btn_timer_mode)
        content_layout.addLayout(mode_box)

        center_card = QFrame()
        center_card.setStyleSheet("background-color: white; border-radius: 40px; border: none;")
        card_layout = QVBoxLayout(center_card)
        card_layout.setContentsMargins(40, 40, 40, 40)

        spinner_hbox = QHBoxLayout()
        hr_vbox = QVBoxLayout()
        self.hr_up = QPushButton("▲")
        self.hr_down = QPushButton("▼")
        for btn in [self.hr_up, self.hr_down]:
            btn.setFixedSize(80, 80)
            btn.setStyleSheet(
                "font-size: 40px; color: #8FC8C2; background: transparent; "
                "border: 3px solid #8FC8C2; border-radius: 40px;")
        self.hr_up.clicked.connect(lambda: self.spin_time(h=1))
        self.hr_down.clicked.connect(lambda: self.spin_time(h=-1))
        hr_vbox.addWidget(self.hr_up)
        hr_vbox.addWidget(self.hr_down)

        self.time_spinner = QTimeEdit(QTime.currentTime())
        self.time_spinner.setDisplayFormat("HH:mm")
        self.time_spinner.setFixedSize(450, 200)
        self.time_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_spinner.setStyleSheet("""
            QTimeEdit { background-color: #F9F9F9; border: 3px solid #8FC8C2;
                        border-radius: 30px; font-size: 130px; font-weight: bold; color: #2C4C49; }
            QTimeEdit::up-button, QTimeEdit::down-button { width: 0px; }
        """)

        min_vbox = QVBoxLayout()
        self.min_up = QPushButton("▲")
        self.min_down = QPushButton("▼")
        for btn in [self.min_up, self.min_down]:
            btn.setFixedSize(80, 80)
            btn.setStyleSheet(
                "font-size: 40px; color: #8FC8C2; background: transparent; "
                "border: 3px solid #8FC8C2; border-radius: 40px;")
        self.min_up.clicked.connect(lambda: self.spin_time(m=1))
        self.min_down.clicked.connect(lambda: self.spin_time(m=-1))
        min_vbox.addWidget(self.min_up)
        min_vbox.addWidget(self.min_down)

        spinner_hbox.addLayout(hr_vbox)
        spinner_hbox.addWidget(self.time_spinner)
        spinner_hbox.addLayout(min_vbox)
        card_layout.addLayout(spinner_hbox)

        self.mode_label = QLabel("Tap arrows to set alarm")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.mode_label.setStyleSheet("border: none; color: #444444;")
        card_layout.addWidget(self.mode_label)
        content_layout.addWidget(center_card)

        act_layout = QHBoxLayout()
        self.start_btn = QPushButton("SET ALARM")
        self.start_btn.setFixedSize(350, 100)
        self.start_btn.setStyleSheet(
            "background-color: #4D908E; color: white; border-radius: 50px; "
            "font-weight: bold; font-size: 30px; border: none;")
        self.start_btn.clicked.connect(self.set_clock_action)

        self.back_btn_clock = QPushButton("CANCEL")
        self.back_btn_clock.setFixedSize(350, 100)
        self.back_btn_clock.setStyleSheet(
            "background-color: #BDBDBD; color: white; border-radius: 50px; "
            "font-weight: bold; font-size: 30px; border: none;")
        self.back_btn_clock.clicked.connect(lambda: self.app.stack.setCurrentIndex(1))

        act_layout.addWidget(self.back_btn_clock)
        act_layout.addWidget(self.start_btn)
        content_layout.addLayout(act_layout)
        main_v.addLayout(content_layout)

    def spin_time(self, h=0, m=0):
        current = self.time_spinner.time()
        self.time_spinner.setTime(current.addSecs((h * 3600) + (m * 60)))

    def switch_clock_mode(self, mode):
        if mode == "ALARM":
            self.btn_timer_mode.setChecked(False)
            self.start_btn.setText(translate("SET ALARM", self.current_lang))
            self.mode_label.setText(translate("Tap arrows to set alarm", self.current_lang))
            self.time_spinner.setTime(QTime.currentTime())
        else:
            self.btn_alarm_mode.setChecked(False)
            self.start_btn.setText(translate("START TIMER", self.current_lang))
            self.mode_label.setText(translate("Tap arrows to set duration", self.current_lang))
            self.time_spinner.setTime(QTime(0, 0))

    def set_clock_action(self):
        t = self.time_spinner.time()
        if self.btn_alarm_mode.isChecked():
            self.app.active_alarm_time = t.toString("HH:mm")
            self.app.welcome_page.alarm_status.setText(t.toString("HH:mm"))
            self.app.welcome_page.alarm_container.show()
            self.app.welcome_page.update_status_visibility()
            self.time_spinner.setTime(QTime.currentTime())
        else:
            self.app.timer_seconds_remaining = (t.hour() * 3600) + (t.minute() * 60)
            self.time_spinner.setTime(QTime(0, 0))
        self.app.stack.setCurrentIndex(0)

    def update_language(self, lang_code):
        self.current_lang = lang_code
        self.clock_title.setText(translate("CLOCK SETTINGS", lang_code))
        self.btn_alarm_mode.setText(translate("ALARM", lang_code))
        self.btn_timer_mode.setText(translate("TIMER", lang_code))
        self.back_btn_clock.setText(translate("CANCEL", lang_code))
        if self.btn_alarm_mode.isChecked():
            self.mode_label.setText(translate("Tap arrows to set alarm", lang_code))
            self.start_btn.setText(translate("SET ALARM", lang_code))
        else:
            self.mode_label.setText(translate("Tap arrows to set duration", lang_code))
            self.start_btn.setText(translate("START TIMER", lang_code))


# ==========================================
# PAGE 10: FULL SCREEN ALERT PAGE
# ==========================================
class AlertPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #FEF3E2;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        self.icon_label = QLabel("⏰")
        self.icon_label.setFont(QFont("Arial", 120))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent; border: none;")

        self.message_label = QLabel("ALARM!")
        self.message_label.setFont(QFont("Arial", 54, QFont.Weight.Bold))
        self.message_label.setStyleSheet("color: #D4A84B; background: transparent; border: none;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stop_btn = QPushButton("TURN OFF")
        self.stop_btn.setFixedSize(500, 150)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton { background-color: #E8A838; color: white; border-radius: 75px;
                          font-weight: bold; font-size: 48px; border: none; }
            QPushButton:pressed { background-color: #C08A2E; }
        """)
        self.stop_btn.clicked.connect(self.dismiss_alert)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_alert_style(self, message, is_emergency=False):
        lang_code = "th" if self.app.main_menu.lang_btn.text() == "THAI / ไทย" else "en"
        self.message_label.setText(translate(message, lang_code))
        if is_emergency:
            self.setStyleSheet("background-color: #FADBD8;")
            self.icon_label.setText("🚨")
            self.message_label.setStyleSheet("color: #C0392B; background: transparent; border: none;")
            self.stop_btn.setStyleSheet("""
                QPushButton { background-color: #C0392B; color: white; border-radius: 75px;
                              font-weight: bold; font-size: 48px; border: none; }
                QPushButton:pressed { background-color: #922B21; }
            """)
        else:
            self.setStyleSheet("background-color: #FEF3E2;")
            self.icon_label.setText("⏰")
            self.message_label.setStyleSheet("color: #D4A84B; background: transparent; border: none;")
            self.stop_btn.setStyleSheet("""
                QPushButton { background-color: #E8A838; color: white; border-radius: 75px;
                              font-weight: bold; font-size: 48px; border: none; }
                QPushButton:pressed { background-color: #C08A2E; }
            """)

    def dismiss_alert(self):
        self.app.sound_effect.stop()
        self.app.stack.setCurrentIndex(1)

    def update_language(self, lang_code):
        self.stop_btn.setText(translate("TURN OFF", lang_code))


# ==========================================
# MAIN APPLICATION
# ==========================================
class WellBeingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Daily Well-Being")
        self.active_alarm_time = None
        self.timer_seconds_remaining = 0
        self._current_lang = "en"   # track active language globally
        self.sound_effect = QSoundEffect()
        self.sound_effect.setLoopCount(10)
        if os.path.exists("assets/alarm.wav"):
            self.sound_effect.setSource(QUrl.fromLocalFile(os.path.abspath("assets/alarm.wav")))

        self.core_timer = QTimer(self)
        self.core_timer.timeout.connect(self.process_time_events)
        self.core_timer.start(1000)

        self.stack = QStackedWidget(self)

        self.welcome_page = WelcomePage(self)
        self.stack.addWidget(self.welcome_page)        # index 0

        self.main_menu = MainMenuPage(self)
        self.stack.addWidget(self.main_menu)           # index 1

        self.food_page = FoodPage(self)
        self.stack.addWidget(self.food_page)           # index 2

        self.feeling_page = FeelingPage(self)
        self.stack.addWidget(self.feeling_page)        # index 3

        self.position_page = PositionPage(self)
        self.stack.addWidget(self.position_page)       # index 4

        self.bathroom_page = BathroomPage(self)
        self.stack.addWidget(self.bathroom_page)       # index 5

        self.yes_no_page = YesNoPage(self)
        self.stack.addWidget(self.yes_no_page)         # index 6

        self.entertainment_page = EntertainmentPage(self)
        self.stack.addWidget(self.entertainment_page)  # index 7

        self.recommend_page = RecommendPage(self)
        self.stack.addWidget(self.recommend_page)      # index 8

        self.clock_page = ClockPage(self)
        self.stack.addWidget(self.clock_page)          # index 9

        self.alert_page = AlertPage(self)
        self.stack.addWidget(self.alert_page)          # index 10

        self.fullscreen_item_page = FullScreenItemPage(self)
        self.stack.addWidget(self.fullscreen_item_page)  # index 11

        self.pages = [
            self.welcome_page, self.main_menu, self.food_page, self.feeling_page,
            self.position_page, self.bathroom_page, self.yes_no_page,
            self.entertainment_page, self.recommend_page, self.clock_page,
            self.alert_page, self.fullscreen_item_page
        ]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

    def process_time_events(self):
        now_str = QTime.currentTime().toString("HH:mm")

        if self.active_alarm_time and now_str == self.active_alarm_time:
            self.active_alarm_time = None
            self.welcome_page.alarm_status.setText("")
            self.welcome_page.alarm_container.hide()
            self.welcome_page.update_status_visibility()
            self.trigger_alert("ALARM!")

        if self.timer_seconds_remaining > 0:
            self.timer_seconds_remaining -= 1
            m, s = divmod(self.timer_seconds_remaining, 60)
            self.welcome_page.timer_status.setText(f"⏳ Timer: {m:02d}:{s:02d} remaining")
            self.welcome_page.timer_status.setStyleSheet(
                "color: white; background-color: #E67E22; border-radius: 10px; padding: 5px; border: none;")
            self.welcome_page.cancel_timer_btn.show()
            self.welcome_page.update_status_visibility()
            if self.timer_seconds_remaining == 0:
                self.welcome_page.timer_status.setText("")
                self.welcome_page.cancel_timer_btn.hide()
                self.welcome_page.update_status_visibility()
                self.trigger_alert("TIMER FINISHED!")
        elif self.welcome_page.timer_status.text() != "":
            self.welcome_page.timer_status.setText("")
            self.welcome_page.timer_status.setStyleSheet("")
            self.welcome_page.cancel_timer_btn.hide()
            self.welcome_page.update_status_visibility()

    def trigger_alert(self, text):
        self.sound_effect.setLoopCount(50)
        self.sound_effect.play()
        is_emergency = "Emergency" in text or "pain" in text.lower()
        self.alert_page.set_alert_style(text, is_emergency)
        self.stack.setCurrentIndex(10)

    def update_language(self, lang_code):
        self._current_lang = lang_code
        for page in self.pages:
            if hasattr(page, 'update_language'):
                page.update_language(lang_code)
        # Refresh the big screen display on whichever scrollable page is currently shown
        current_page = self.stack.currentWidget()
        if hasattr(current_page, 'current_index') and hasattr(current_page, 'big_screen'):
            update_big_screen_shared(current_page, current_page.current_index)


# ==========================================
# EXTEND FullScreenItemPage with bathroom support
# ==========================================
def _show_bathroom_item(self, item_name, description, media_file, bg_color, emoji_fallback, back_index):
    self._back_index = back_index
    self._item_name = item_name
    self.name_label.setText(item_name)

    if os.path.exists(media_file):
        pixmap = QPixmap(media_file)
        screen_w = self.app.width()
        screen_h = self.app.height() - 140
        scaled = pixmap.scaled(screen_w, screen_h,
                               Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
        x_off = (scaled.width() - screen_w) // 2
        y_off = (scaled.height() - screen_h) // 4
        cropped = scaled.copy(x_off, y_off, screen_w, screen_h)

        rounded = QPixmap(cropped.size())
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        if painter.isActive():
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(cropped.rect()), 0, 0)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, cropped)
            painter.end()

        self.image_label.setPixmap(rounded)
        self.image_label.setText("")
        self.setStyleSheet("background-color: #1a1a1a;")
        self.image_label.setStyleSheet("background: transparent; border: none;")
    else:
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText(emoji_fallback)
        self.image_label.setFont(QFont("Arial", 120))
        self.setStyleSheet(f"background-color: {bg_color};")
        self.image_label.setStyleSheet(
            f"background-color: {bg_color}; color: #2C4C49; border: none;")

    self.name_label.setText(f"{item_name}\n{description}")

FullScreenItemPage.show_bathroom_item = _show_bathroom_item


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WellBeingApp()
    window.setFixedSize(1289, 800)
    window.show()
    sys.exit(app.exec())