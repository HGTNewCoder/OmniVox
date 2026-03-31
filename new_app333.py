import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QPushButton, QMessageBox, QStackedWidget, QTimeEdit,
                             QGraphicsDropShadowEffect, QComboBox)
from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import Qt, QDate, QTimer, QTime, QUrl
from PyQt6.QtMultimedia import QSoundEffect

# ==========================================
# HARDCODED TRANSLATION DICTIONARY
# ==========================================
THAI_TRANSLATIONS = {
    # Main Menu & Headers
    "MY DAILY WELL-BEING": "ความเป็นอยู่ที่ดีของฉัน",
    "FOOD": "อาหาร",
    "Request food or specify meal type.": "ขออาหารหรือระบุเมนู",
    "FEELING": "ความรู้สึก",
    "Describe current mood and emotion.": "บอกความรู้สึกของคุณ",
    "EXERCISE": "ออกกำลังกาย",
    "Request activity or physical exercise.": "ทำกิจกรรมหรือออกกำลัง",
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
    
    # Emergency Bell
    "CALL FOR HELP": "ขอความช่วยเหลือ",
    "Press to alert a staff member immediately.": "กดเพื่อแจ้งเจ้าหน้าที่ทันที",
    "CALL NOW": "เรียกเลย",
    "TALK WITH US": "พูดคุยกับเรา",
    
    # Sub-pages
    "FOOD MENU": "เมนูอาหาร",
    "FEELING & MOOD": "ความรู้สึกและอารมณ์",
    "BATHROOM ASSISTANCE": "ความช่วยเหลือห้องน้ำ",
    "RECOMMENDATIONS": "คำแนะนำ",
    "Go Back": "ย้อนกลับ",
    
    # Bathroom Specifics
    "TOILET": "เข้าห้องน้ำ",
    "I need to use the toilet.": "ฉันต้องการเข้าห้องน้ำ",
    "SHOWER": "อาบน้ำ",
    "I would like to take a shower.": "ฉันต้องการอาบน้ำ",
    "WASH": "ล้างหน้า/ล้างมือ",
    "I need to wash my hands/face.": "ฉันต้องการล้างหน้าและมือ",
    "CLOTHES": "เปลี่ยนเสื้อผ้า",
    "I need help changing clothes.": "ฉันต้องการเปลี่ยนเสื้อผ้า",
    "TEETH": "เปลี่ยนผ้าอ้อม", # Mapping to your description
    "I need to change the diaper.": "ฉันต้องการเปลี่ยนผ้าอ้อม",
    "GROOMING": "จัดแต่งทรงผม",
    "I need help with hair or shaving.": "ฉันต้องการความช่วยเหลือเรื่องทรงผมหรือโกนหนวด",
    
    # Yes / No Page
    "CHOOSE ANSWER": "เลือกคำตอบ",
    "YES": "ใช่",
    "NO": "ไม่ใช่",
    "CONFIRM": "ยืนยัน",
    
    # Clock Page
    "CLOCK SETTINGS": "ตั้งค่าเวลา",
    "ALARM": "นาฬิกาปลุก",
    "TIMER": "จับเวลา",
    "Tap arrows to set alarm": "แตะลูกศรเพื่อตั้งปลุก",
    "Tap arrows to set duration": "แตะลูกศรเพื่อตั้งเวลา",
    "SET ALARM": "ตั้งปลุก",
    "START TIMER": "เริ่มจับเวลา",
    "CANCEL": "ยกเลิก"
}

def translate(text, lang_code):
    """Returns the translated string if lang_code is 'th', otherwise returns original English text."""
    if not text:
        return ""
    if lang_code == "en":
        return text
    # Fetch from dictionary, fallback to the English text if not found
    return THAI_TRANSLATIONS.get(text, text)

# ==========================================
# COMMBOX: DYNAMIC TRANSLATION ENABLED
# ==========================================
class CommBox(QFrame):
    def __init__(self, title, description, bg_color, media_file, is_bell=False, show_btn=True, large_text=False, add_shadow=False, use_picture=False, hide_title=False, callback=None):
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
        
        if is_bell or not show_btn:
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
        self.bell_inner_frame.setStyleSheet(f"background-color: {self.original_color}; border-radius: 20px; border: none;")
        
        inner_layout = QHBoxLayout(self.bell_inner_frame)
        inner_layout.setContentsMargins(30, 15, 30, 15)
        inner_layout.setSpacing(25)

        self.bell_display = QLabel()
        if media_file and os.path.exists(media_file):
            pixmap = QPixmap(media_file)
            self.bell_display.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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
        self.call_now_btn_label.setStyleSheet("background-color: #C0392B; color: white; border-radius: 12px; font-weight: bold; font-size: 20px;")

        inner_layout.addWidget(self.bell_display)
        inner_layout.addLayout(text_v_layout)
        inner_layout.addStretch()
        inner_layout.addWidget(self.call_now_btn_label)

        self.main_v_layout.addWidget(self.bell_inner_frame)

    def setup_standard_ui(self, title, description, bg_color, media_file):
        self.top_half = QFrame()
        self.top_half.setStyleSheet(f"background-color: {bg_color}; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none;")
        top_layout = QVBoxLayout(self.top_half)
        
        if self.use_picture:
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(0)
        
        if not self.hide_title:
            self.title_label = QLabel(title)
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if self.large_text:
                self.title_label.setFont(QFont("Arial", 26, QFont.Weight.Bold))
                self.title_label.setStyleSheet("color: #2C4C49; padding: 15px;" if self.use_picture else "color: #2C4C49; padding-top: 10px;")
            else:
                self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                if self.use_picture: self.title_label.setStyleSheet("padding: 10px;")
                
            top_layout.addWidget(self.title_label)
        
        if self.use_picture and media_file and os.path.exists(media_file):
            self.pic_frame = QFrame()
            safe_path = media_file.replace('\\', '/')
            self.pic_frame.setStyleSheet(f"QFrame {{ border-image: url({safe_path}) 0 0 0 0 stretch stretch; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none; }}")
            top_layout.addWidget(self.pic_frame, 1) 
        else:
            self.media_display = QLabel()
            self.media_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if media_file and os.path.exists(media_file):
                pixmap = QPixmap(media_file)
                self.media_display.setPixmap(pixmap.scaled(140, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                emoji_map = {"TOILET": "🚽", "SHOWER": "🚿", "WASH": "🧼", "CLOTHES": "👕", "FOOD": "🥪", "FEELING": "😊", "EXERCISE": "💪", "ENTERTAINMENT": "📺", "YES / NO": "✅", "RECOMMEND ANSWER": "💡", "CLOCK": "⏰"}
                self.media_display.setText(emoji_map.get(title, "✨"))
                self.media_display.setFont(QFont("Arial", 70 if self.large_text else 40))
                
            top_layout.addWidget(self.media_display)

        self.bottom_half = QFrame()
        self.bottom_half.setStyleSheet("background-color: white; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; border: none;")
        bottom_layout = QVBoxLayout(self.bottom_half)
        bottom_layout.addStretch(1) 
        
        self.desc_label = QLabel(description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setFont(QFont("Arial", 18 if (self.large_text or self.hide_title) else 15, QFont.Weight.Bold))
        self.desc_label.setStyleSheet("color: #444444;" if (self.large_text or self.hide_title) else "") 
            
        bottom_layout.addWidget(self.desc_label)
        bottom_layout.addStretch(1) 

        if self.show_btn:
            self.btn = QPushButton("TALK WITH US")
            self.btn.setFixedHeight(45)
            self.btn.setStyleSheet("QPushButton { background-color: #4D908E; color: white; border-radius: 12px; font-weight: bold; border: none; }")
            self.btn.clicked.connect(self.handle_click)
            bottom_layout.addWidget(self.btn)
        
        if self.hide_title: weights = (75, 25)
        elif self.large_text: weights = (60, 40)
        else: weights = (40, 60)
        self.main_v_layout.addWidget(self.top_half, weights[0])
        self.main_v_layout.addWidget(self.bottom_half, weights[1])

    def handle_click(self):
        if self.callback: self.callback(self.title)

    def mousePressEvent(self, event):
        if self.is_bell:
            self.bell_inner_frame.setStyleSheet("background-color: #900C3F; border-radius: 20px; border: none;")
            QTimer.singleShot(200, lambda: self.bell_inner_frame.setStyleSheet(f"background-color: {self.original_color}; border-radius: 20px; border: none;"))
            if self.callback: self.callback("BELL")
        elif not self.show_btn:
            if self.hide_title and self.use_picture and hasattr(self, 'pic_frame'):
                safe_path = self.media_file.replace('\\', '/')
                self.pic_frame.setStyleSheet(f"QFrame {{ border-image: url({safe_path}) 0 0 0 0 stretch stretch; border-top-left-radius: 20px; border-top-right-radius: 20px; border: 6px solid #8FC8C2; }}")
            else:
                self.top_half.setStyleSheet(f"background-color: #BDBDBD; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none;")
            
            self.bottom_half.setStyleSheet("background-color: #E0E0E0; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; border: none;")
            QTimer.singleShot(150, self.restore_colors)
            if self.callback: self.callback(self.title)

    def restore_colors(self):
        if self.hide_title and self.use_picture and hasattr(self, 'pic_frame'):
            safe_path = self.media_file.replace('\\', '/')
            self.pic_frame.setStyleSheet(f"QFrame {{ border-image: url({safe_path}) 0 0 0 0 stretch stretch; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none; }}")
        else:
            self.top_half.setStyleSheet(f"background-color: {self.original_color}; border-top-left-radius: 20px; border-top-right-radius: 20px; border: none;")
        self.bottom_half.setStyleSheet("background-color: white; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; border: none;")

    # --- Dictionary Based Translation Method ---
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
# PAGE 0: MAIN MENU
# ==========================================
class MainMenuPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #F0F8F7;")
        layout = QVBoxLayout(self)
        
        header_container = QFrame()
        header_container.setStyleSheet("background-color: #8FC8C2; border: none;")
        header_h_layout = QHBoxLayout(header_container)
        header_h_layout.setContentsMargins(20, 15, 20, 15)
        header_h_layout.addStretch(1)

        text_v_layout = QVBoxLayout()
        self.header_label = QLabel("MY DAILY WELL-BEING")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        self.header_label.setStyleSheet("color: #2C4C49;")
        
        self.date_label = QLabel(QDate.currentDate().toString('dddd, MMMM d, yyyy'))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setFont(QFont("Arial", 18))
        self.date_label.setStyleSheet("color: #2C4C49;")

        self.timer_status = QLabel("")
        self.timer_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_v_layout.addWidget(self.header_label)
        text_v_layout.addWidget(self.date_label)
        text_v_layout.addWidget(self.timer_status)
        header_h_layout.addLayout(text_v_layout)
        header_h_layout.addStretch(1)
        
        # --- LANGUAGE TOGGLE BUTTON ---
        self.lang_btn = QPushButton("ENGLISH")
        self.lang_btn.setFixedSize(160, 60)
        self.lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang_btn.setStyleSheet("""
            QPushButton { 
                background-color: white; 
                color: #2C4C49; 
                border-radius: 15px; 
                font-weight: bold; 
                font-size: 18px; 
                border: none;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        
        self.lang_btn.clicked.connect(self.toggle_language)
        header_h_layout.addWidget(self.lang_btn)

        layout.addWidget(header_container)

        self.grid = QGridLayout()
        self.grid.setContentsMargins(25, 10, 25, 10); self.grid.setSpacing(20)
        self.card_data = [
            ("FOOD", "Request food or specify meal type.", "#AED6F1", "food.png", 0, 0),
            ("FEELING", "Describe current mood and emotion.", "#F9E79F", "feeling.png", 0, 1),
            ("EXERCISE", "Request activity or physical exercise.", "#D6EAF8", "exercise.png", 0, 2),
            ("BATHROOM", "Request bathroom assistance.", "#D1F2EB", "bathroom.png", 0, 3),
            ("YES / NO", "Confirmatory responses for staff.", "#FADBD8", "yes_no.png", 1, 0),
            ("ENTERTAINMENT", "Request leisure activity or TV.", "#D5F5E3", "entertainment.png", 1, 1),
            ("RECOMMEND ANSWER", "Suggestion from staff or system.", "#FCF3CF", "recommend.png", 1, 2),
            ("CLOCK", "Check the time or daily schedule.", "#E8DAEF", "clock.png", 1, 3),
        ]
        self.cards = []
        for title, desc, col, img, r, c in self.card_data:
            card = CommBox(title=title, description=desc, bg_color=col, media_file=img, callback=self.navigate)
            self.cards.append(card)
            self.grid.addWidget(card, r, c)
            
        self.bell_card = CommBox(title="", description="", bg_color="#FFEADB", media_file="bell.png", is_bell=True, callback=self.navigate)
        self.grid.addWidget(self.bell_card, 2, 0, 1, 4) 
        layout.addLayout(self.grid)

    def toggle_language(self):
        # Check current text and switch to the other
        if self.lang_btn.text() == "ENGLISH":
            self.lang_btn.setText("THAI / ไทย")
            self.app.update_language("th")
        else:
            self.lang_btn.setText("ENGLISH")
            self.app.update_language("en")

    def navigate(self, title):
        pages = {"FOOD": 1, "FEELING": 2, "EXERCISE": 3, "BATHROOM": 4, "YES / NO": 5, "ENTERTAINMENT": 6, "RECOMMEND ANSWER": 7}
        if title in pages: self.app.stack.setCurrentIndex(pages[title])
        elif title == "CLOCK": self.app.stack.setCurrentIndex(8)
        elif title == "BELL": QMessageBox.warning(self, "Emergency", "Staff Alerted!")

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
# SUB-PAGES
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
        self.back_btn.setStyleSheet("background-color: #BDBDBD; color: white; border-radius: 15px; font-weight: bold; font-size: 20px; border: none;")
        self.back_btn.clicked.connect(lambda: self.app.stack.setCurrentIndex(0))
        layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.page_layout = layout

    def update_language(self, lang_code):
        self.header.setText(translate(self.original_title, lang_code))
        self.back_btn.setText(translate("Go Back", lang_code))

class FoodPage(BasePage):
    def __init__(self, app): super().__init__(app, "FOOD MENU")

class FeelingPage(BasePage):
    def __init__(self, app): super().__init__(app, "FEELING & MOOD")

class ExercisePage(BasePage):
    def __init__(self, app): super().__init__(app, "EXERCISE")

class EntertainmentPage(BasePage):
    def __init__(self, app): super().__init__(app, "ENTERTAINMENT")

class RecommendPage(BasePage):
    def __init__(self, app): super().__init__(app, "RECOMMENDATIONS")

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
            ("TOILET", "I need to use the toilet.", "#AED6F1", "toilet_pic.png", 0, 0), 
            ("SHOWER", "I would like to take a shower.", "#A2D9CE", "shower_pic.png", 0, 1), 
            ("WASH", "I need to wash my hands/face.", "#F9E79F", "wash_pic.jpg", 0, 2), 
            ("CLOTHES", "I need help changing clothes.", "#D7BDE2", "clothes_pic.jpg", 1, 0), 
            ("TEETH", "I need to change the diaper.", "#F5B7B1", "diaper_pic.png", 1, 1),       
            ("GROOMING", "I need help with hair or shaving.", "#FAD7A1", "grooming_pic.png", 1, 2), 
        ]
        self.cards = []
        for t, d, c, mf, r, col in self.options_data:
            card = CommBox(title=t, description=d, bg_color=c, media_file=mf, show_btn=False, add_shadow=True, use_picture=True, hide_title=True, callback=self.handle_bathroom_selection)
            self.cards.append(card)
            grid.addWidget(card, r, col)
            
        layout.addLayout(grid)
        self.back_btn = QPushButton("Go Back")
        self.back_btn.setFixedSize(200, 60); self.back_btn.setStyleSheet("background-color: #BDBDBD; color: white; border-radius: 15px; font-weight: bold; font-size: 20px; border: none;")
        self.back_btn.clicked.connect(lambda: self.app.stack.setCurrentIndex(0))
        layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

    def handle_bathroom_selection(self, choice):
        self.app.trigger_alert(f"Assistance Requested: {choice}")
        self.app.stack.setCurrentIndex(0)
        
    def update_language(self, lang_code):
        self.header.setText(translate("BATHROOM ASSISTANCE", lang_code))
        self.back_btn.setText(translate("Go Back", lang_code))
        for card in self.cards:
            card.update_language(lang_code)

class YesNoPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20); layout.setSpacing(20)
        self.resp_title = QLabel("CHOOSE ANSWER")
        self.resp_title.setAlignment(Qt.AlignmentFlag.AlignCenter); self.resp_title.setFont(QFont("Arial", 38, QFont.Weight.Bold))
        self.resp_title.setStyleSheet("color: #2C4C49; border: none;")
        layout.addWidget(self.resp_title)
        self.resp_cards_container = QHBoxLayout(); self.resp_cards_container.setSpacing(40)
        
        self.yes_card, self.yes_btn, self.yes_lbl = self.create_styled_response_card("YES", "#D5F5E3", "#4D908E", "yes.png", lambda: self.show_result("YES"))
        self.no_card, self.no_btn, self.no_lbl = self.create_styled_response_card("NO", "#FADBD8", "#A93226", "no.png", lambda: self.show_result("NO"))
        
        self.resp_cards_container.addWidget(self.yes_card); self.resp_cards_container.addWidget(self.no_card)
        layout.addLayout(self.resp_cards_container)
        self.back_btn_resp = QPushButton("Go Back")
        self.back_btn_resp.setFixedSize(150, 50); self.back_btn_resp.setStyleSheet("background-color: #BDBDBD; color: white; border-radius: 10px; font-weight: bold; border: none;")
        self.back_btn_resp.clicked.connect(lambda: self.app.stack.setCurrentIndex(0))
        layout.addWidget(self.back_btn_resp, alignment=Qt.AlignmentFlag.AlignCenter)
        self.result_container = QFrame(); self.result_container.hide()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_icon = QLabel(); self.result_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_layout.addWidget(self.result_icon)
        layout.addWidget(self.result_container)

    def create_styled_response_card(self, title, bg_color, btn_color, icon, callback):
        card = QFrame(); card.setStyleSheet(f"background-color: {bg_color}; border-radius: 40px; border: none;")
        v = QVBoxLayout(card); v.setContentsMargins(20, 10, 20, 20)
        lbl_icon = QLabel()
        if os.path.exists(icon):
            lbl_icon.setPixmap(QPixmap(icon).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_icon.setText("✅" if title == "YES" else "❌"); lbl_icon.setFont(QFont("Arial", 150))
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(lbl_icon)
        t_lbl = QLabel(title); t_lbl.setFont(QFont("Arial", 75, QFont.Weight.Bold)); t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); t_lbl.setStyleSheet(f"color: {btn_color}; border: none;")
        v.addWidget(t_lbl); v.addStretch()
        btn = QPushButton("CONFIRM"); btn.setFixedHeight(80); btn.setStyleSheet(f"background-color: {btn_color}; color: white; border-radius: 25px; font-size: 24px; font-weight: bold; border: none;")
        btn.clicked.connect(callback); v.addWidget(btn)
        return card, btn, t_lbl

    def show_result(self, choice):
        self.app.stack.setCurrentIndex(5)
        self.resp_title.hide()
        self.back_btn_resp.hide()
        self.yes_card.hide()
        self.no_card.hide()

        bg = "#D5F5E3" if choice == "YES" else "#FADBD8"
        self.setStyleSheet(f"background-color: {bg}; border: none;")
        icon_path = "yes.png" if choice == "YES" else "no.png"
    
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.result_icon.setPixmap(pix)
        else:
            self.result_icon.setText("✅" if choice == "YES" else "❌")
            self.result_icon.setFont(QFont("Arial", 200))

        self.result_icon.show()
        self.result_container.show()
        QTimer.singleShot(3000, self.reset_and_go_home)

    def reset_and_go_home(self):
        self.setStyleSheet("background-color: white; border: none;")
        self.result_container.hide(); self.resp_title.show(); self.back_btn_resp.show()
        self.yes_card.show(); self.no_card.show()
        self.app.stack.setCurrentIndex(0)
        
    def update_language(self, lang_code):
        self.resp_title.setText(translate("CHOOSE ANSWER", lang_code))
        self.back_btn_resp.setText(translate("Go Back", lang_code))
        self.yes_btn.setText(translate("CONFIRM", lang_code))
        self.no_btn.setText(translate("CONFIRM", lang_code))
        self.yes_lbl.setText(translate("YES", lang_code))
        self.no_lbl.setText(translate("NO", lang_code))

class ClockPage(QFrame):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setStyleSheet("background-color: #F0F8F7;")
        main_v = QVBoxLayout(self); main_v.setContentsMargins(0, 0, 0, 0)
        top_bar = QFrame(); top_bar.setFixedHeight(120); top_bar.setStyleSheet("background-color: #8FC8C2; border: none;")
        top_layout = QHBoxLayout(top_bar)
        self.clock_title = QLabel("CLOCK SETTINGS"); self.clock_title.setFont(QFont("Arial", 32, QFont.Weight.Bold)); self.clock_title.setStyleSheet("color: white; border: none;")
        top_layout.addWidget(self.clock_title, alignment=Qt.AlignmentFlag.AlignCenter); main_v.addWidget(top_bar)
        content_layout = QVBoxLayout(); content_layout.setContentsMargins(100, 20, 100, 20); content_layout.setSpacing(20)
        mode_box = QHBoxLayout(); self.btn_alarm_mode = QPushButton("ALARM"); self.btn_timer_mode = QPushButton("TIMER")
        for b in [self.btn_alarm_mode, self.btn_timer_mode]:
            b.setFixedSize(300, 80); b.setCheckable(True); b.setStyleSheet("QPushButton { background-color: #D1E8E5; border-radius: 40px; font-weight: bold; font-size: 26px; color: #2C4C49; border: none; } QPushButton:checked { background-color: #2C4C49; color: white; }")
        self.btn_alarm_mode.setChecked(True)
        self.btn_alarm_mode.clicked.connect(lambda: self.switch_clock_mode("ALARM"))
        self.btn_timer_mode.clicked.connect(lambda: self.switch_clock_mode("TIMER"))
        mode_box.addWidget(self.btn_alarm_mode); mode_box.addWidget(self.btn_timer_mode); content_layout.addLayout(mode_box)
        center_card = QFrame(); center_card.setStyleSheet("background-color: white; border-radius: 40px; border: none;")
        card_layout = QVBoxLayout(center_card); card_layout.setContentsMargins(40, 40, 40, 40)
        spinner_hbox = QHBoxLayout(); hr_vbox = QVBoxLayout(); self.hr_up = QPushButton("▲"); self.hr_down = QPushButton("▼")
        for btn in [self.hr_up, self.hr_down]: 
            btn.setFixedSize(80, 80); btn.setStyleSheet("font-size: 40px; color: #8FC8C2; background: transparent; border: 3px solid #8FC8C2; border-radius: 40px;")
        self.hr_up.clicked.connect(lambda: self.spin_time(h=1)); self.hr_down.clicked.connect(lambda: self.spin_time(h=-1))
        hr_vbox.addWidget(self.hr_up); hr_vbox.addWidget(self.hr_down)
        self.time_spinner = QTimeEdit(QTime.currentTime()); self.time_spinner.setDisplayFormat("HH:mm"); self.time_spinner.setFixedSize(450, 200); self.time_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter); self.time_spinner.setStyleSheet("QTimeEdit { background-color: #F9F9F9; border: 3px solid #8FC8C2; border-radius: 30px; font-size: 130px; font-weight: bold; color: #2C4C49; } QTimeEdit::up-button, QTimeEdit::down-button { width: 0px; }")
        min_vbox = QVBoxLayout(); self.min_up = QPushButton("▲"); self.min_down = QPushButton("▼")
        for btn in [self.min_up, self.min_down]: 
            btn.setFixedSize(80, 80); btn.setStyleSheet("font-size: 40px; color: #8FC8C2; background: transparent; border: 3px solid #8FC8C2; border-radius: 40px;")
        self.min_up.clicked.connect(lambda: self.spin_time(m=1)); self.min_down.clicked.connect(lambda: self.spin_time(m=-1))
        min_vbox.addWidget(self.min_up); min_vbox.addWidget(self.min_down)
        spinner_hbox.addLayout(hr_vbox); spinner_hbox.addWidget(self.time_spinner); spinner_hbox.addLayout(min_vbox)
        card_layout.addLayout(spinner_hbox)
        self.mode_label = QLabel("Tap arrows to set alarm"); self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.mode_label.setFont(QFont("Arial", 32, QFont.Weight.Bold)); self.mode_label.setStyleSheet("border: none; color: #444444;") 
        card_layout.addWidget(self.mode_label); content_layout.addWidget(center_card)
        act_layout = QHBoxLayout()
        self.start_btn = QPushButton("SET ALARM"); self.start_btn.setFixedSize(350, 100); self.start_btn.setStyleSheet("background-color: #4D908E; color: white; border-radius: 50px; font-weight: bold; font-size: 30px; border: none;")
        self.start_btn.clicked.connect(self.set_clock_action)
        self.back_btn_clock = QPushButton("CANCEL"); self.back_btn_clock.setFixedSize(350, 100); self.back_btn_clock.setStyleSheet("background-color: #BDBDBD; color: white; border-radius: 50px; font-weight: bold; font-size: 30px; border: none;")
        self.back_btn_clock.clicked.connect(lambda: self.app.stack.setCurrentIndex(0))
        act_layout.addWidget(self.back_btn_clock); act_layout.addWidget(self.start_btn); content_layout.addLayout(act_layout)
        main_v.addLayout(content_layout)
        
        self.current_lang = "en"

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
        if self.btn_alarm_mode.isChecked(): self.app.active_alarm_time = t.toString("HH:mm")
        else: self.app.timer_seconds_remaining = (t.hour() * 3600) + (t.minute() * 60)
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
# MAIN APPLICATION
# ==========================================
class WellBeingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Daily Well-Being")
        self.active_alarm_time = None
        self.timer_seconds_remaining = 0
        self.sound_effect = QSoundEffect()
        self.sound_effect.setLoopCount(-2)
        if os.path.exists("alarm.wav"):
            self.sound_effect.setSource(QUrl.fromLocalFile(os.path.abspath("alarm.wav")))
            
        self.core_timer = QTimer(self)
        self.core_timer.timeout.connect(self.process_time_events)
        self.core_timer.start(1000)
        
        self.stack = QStackedWidget(self)
        self.main_menu = MainMenuPage(self)
        self.food_page = FoodPage(self)
        self.feeling_page = FeelingPage(self)
        self.exercise_page = ExercisePage(self)
        self.bathroom_page = BathroomPage(self)
        self.yes_no_page = YesNoPage(self)
        self.entertainment_page = EntertainmentPage(self)
        self.recommend_page = RecommendPage(self)
        self.clock_page = ClockPage(self)
        
        self.pages = [
            self.main_menu, self.food_page, self.feeling_page, 
            self.exercise_page, self.bathroom_page, self.yes_no_page, 
            self.entertainment_page, self.recommend_page, self.clock_page
        ]
        
        for page in self.pages:
            self.stack.addWidget(page)
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

    def process_time_events(self):
        now_str = QTime.currentTime().toString("HH:mm")
        if self.active_alarm_time and now_str == self.active_alarm_time:
            self.active_alarm_time = None
            self.trigger_alert("ALARM!")
        if self.timer_seconds_remaining > 0:
            self.timer_seconds_remaining -= 1
            m, s = divmod(self.timer_seconds_remaining, 60)
            self.main_menu.timer_status.setText(f"⏳ Timer: {m:02d}:{s:02d} remaining")
            self.main_menu.timer_status.setStyleSheet("color: white; background-color: #E67E22; border-radius: 10px; padding: 5px; border: none;")
            if self.timer_seconds_remaining == 0:
                self.main_menu.timer_status.setText("")
                self.trigger_alert("TIMER FINISHED!")
        elif self.main_menu.timer_status.text() != "":
            self.main_menu.timer_status.setText("")
            self.main_menu.timer_status.setStyleSheet("")

    def trigger_alert(self, text):
        self.sound_effect.play()
        QMessageBox.information(self, "Alert", text)
        self.sound_effect.stop()

    def update_language(self, lang_code):
        # We recursively call the update_language logic built into each page component
        for page in self.pages:
            if hasattr(page, 'update_language'):
                page.update_language(lang_code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WellBeingApp()
    window.showMaximized()
    sys.exit(app.exec())
