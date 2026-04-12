from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Color, Ellipse, PushMatrix, PopMatrix, Rotate
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
import math
import random
from kivy.utils import platform

# Chỉnh kích thước giả lập trên PC
if platform not in ('android', 'ios'):
    Window.size = (400, 700)

try:
    from plyer import vibrator
except ImportError:
    vibrator = None

# ==========================================
# CLASS HỖ TRỢ: CHỮ XOAY THEO VÒNG QUAY
# ==========================================
class RotatedLabel(Label):
    angle = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(80), dp(40))
        self.halign = 'center'
        self.valign = 'middle'
        self.bind(size=self.setter('text_size'))
        
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=self.angle, origin=self.center)
        with self.canvas.after:
            PopMatrix()
            
    def on_angle(self, instance, value):
        if hasattr(self, 'rot'):
            self.rot.angle = value
            
    def on_center(self, instance, value):
        if hasattr(self, 'rot'):
            self.rot.origin = value

# ==========================================
# CLASS ĐỒ HỌA: VÒNG QUAY (FIX CHUẨN KIM & CHỮ)
# ==========================================
class RouletteGraphic(FloatLayout):
    spin_angle = NumericProperty(0)
    items = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.labels = []
        # Tự động cập nhật chữ khi vòng quay xoay
        self.bind(spin_angle=self.update_graphics, pos=self.update_graphics, size=self.update_graphics)
        
    def draw_wheel(self, items):
        self.items = items
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.before.clear()
        self.clear_widgets()
        
        if not self.items: return
        
        N = len(self.items)
        A = 360.0 / N
        colors = [(0.9, 0.3, 0.3, 1), (0.2, 0.6, 0.8, 1), (0.9, 0.7, 0.1, 1), 
                  (0.2, 0.7, 0.4, 1), (0.6, 0.3, 0.7, 1), (0.9, 0.5, 0.2, 1)]
                  
        with self.canvas.before:
            PushMatrix()
            # Xoay toàn bộ phần nền màu
            Rotate(angle=self.spin_angle, origin=self.center)
            for i in range(N):
                Color(*colors[i % len(colors)])
                Ellipse(pos=self.pos, size=self.size, angle_start=i*A, angle_end=(i+1)*A)
            PopMatrix()

        # Vẽ chữ và di chuyển chữ theo góc xoay spin_angle
        for i, item in enumerate(self.items):
            # Trong Kivy, 0 độ là vị trí 3 giờ. 
            # Góc hiện tại của item = Góc gốc + Góc đang xoay
            current_angle = i * A + (A / 2) + self.spin_angle
            
            rad = math.radians(current_angle)
            r = self.width * 0.35
            cx = self.center_x + r * math.cos(rad)
            cy = self.center_y + r * math.sin(rad)
            
            text_str = str(item)
            short_text = text_str[:6] + ".." if len(text_str) > 7 else text_str
            
            lbl = RotatedLabel(text=short_text, font_size='14sp', bold=True, color=(1,1,1,1))
            lbl.angle = current_angle # Chữ xoay theo hướng ô
            lbl.center = (cx, cy)
            self.add_widget(lbl)

# ==========================================
# GIAO DIỆN KV (FULL TAB)
# ==========================================
KV = '''
MDScreen:
    md_bg_color: 0.96, 0.97, 0.98, 1

    MDBottomNavigation:
        panel_color: 1, 1, 1, 1
        selected_color_background: app.theme_cls.primary_color
        text_color_active: app.theme_cls.primary_color

        MDBottomNavigationItem:
            name: 'tab_number'
            text: 'Numbers'
            icon: 'numeric'
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                MDLabel:
                    text: 'LUCKY NUMBERS'
                    font_style: 'H5'
                    bold: True
                    theme_text_color: 'Primary'
                    halign: 'center'
                    size_hint_y: None
                    height: dp(30)
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    MDTextField:
                        id: max_input
                        hint_text: 'Enter max number'
                        input_filter: 'int'
                        halign: 'center'
                    MDRaisedButton:
                        text: 'SET UP'
                        size_hint_y: 1
                        on_release: app.setup_numbers()
                MDCard:
                    orientation: 'vertical'
                    padding: dp(10)
                    radius: [15, 15, 15, 15]
                    elevation: 2
                    MDLabel:
                        id: result_label
                        text: '?'
                        font_style: 'H1'
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: app.theme_cls.primary_color
                        bold: True
                    MDLabel:
                        id: status_label
                        text: 'Ready...'
                        halign: 'center'
                        theme_text_color: 'Secondary'
                        size_hint_y: None
                        height: dp(30)
                MDFillRoundFlatButton:
                    id: draw_btn
                    text: 'DRAW NOW'
                    size_hint_x: 1
                    size_hint_y: None
                    height: dp(50)
                    disabled: True
                    on_release: app.start_draw_animation('number')
                MDCard:
                    padding: dp(15)
                    radius: [10, 10, 10, 10]
                    elevation: 1
                    size_hint_y: 0.6
                    ScrollView:
                        MDLabel:
                            id: history_label
                            text: 'No history yet...'
                            size_hint_y: None
                            height: self.texture_size[1]
                            text_size: self.width, None

        MDBottomNavigationItem:
            name: 'tab_name'
            text: 'Names'
            icon: 'account-star'
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                MDLabel:
                    text: 'RANDOM PICKER'
                    font_style: 'H5'
                    bold: True
                    theme_text_color: 'Custom'
                    text_color: 0.66, 0.33, 0.97, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(30)
                MDTextField:
                    id: names_input
                    hint_text: 'Enter names'
                    helper_text: '(One name per line)'
                    helper_text_mode: 'persistent'
                    mode: "rectangle"
                    multiline: True
                    size_hint_y: 0.4
                MDRaisedButton:
                    text: 'LOAD LIST'
                    size_hint_x: 1
                    md_bg_color: 0.66, 0.33, 0.97, 1
                    on_release: app.setup_names()
                MDCard:
                    orientation: 'vertical'
                    padding: dp(10)
                    radius: [15, 15, 15, 15]
                    elevation: 2
                    size_hint_y: 0.4
                    MDLabel:
                        id: name_result_label
                        text: 'Who is next?'
                        font_style: 'H4'
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: 0.66, 0.33, 0.97, 1
                        bold: True
                    MDLabel:
                        id: name_status_label
                        text: 'Waiting for names...'
                        halign: 'center'
                        size_hint_y: None
                        height: dp(30)
                MDFillRoundFlatButton:
                    id: name_draw_btn
                    text: 'PICK SOMEONE'
                    size_hint_x: 1
                    size_hint_y: None
                    height: dp(50)
                    disabled: True
                    md_bg_color: 0.66, 0.33, 0.97, 1
                    on_release: app.start_draw_animation('name')

        MDBottomNavigationItem:
            name: 'tab_wheel'
            text: 'Wheel'
            icon: 'sync-circle'
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                MDLabel:
                    text: 'SPIN THE WHEEL'
                    font_style: 'H5'
                    bold: True
                    theme_text_color: 'Custom'
                    text_color: 0.18, 0.8, 0.44, 1 
                    halign: 'center'
                    size_hint_y: None
                    height: dp(30)
                MDTextField:
                    id: wheel_input
                    hint_text: 'Enter items'
                    helper_text: '(One item per line)'
                    helper_text_mode: 'persistent'
                    mode: "rectangle"
                    multiline: True
                    size_hint_y: 0.3
                MDFloatLayout:
                    size_hint_y: 0.5
                    RouletteGraphic:
                        id: graphic_wheel
                        size_hint: None, None
                        size: dp(260), dp(260)
                        pos_hint: {"center_x": .5, "center_y": .5}
                    MDIcon:
                        icon: "menu-down"
                        font_size: "60sp"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        pos_hint: {"center_x": .5, "center_y": .95}
                MDLabel:
                    id: wheel_result_label
                    text: 'TAP SPIN'
                    font_style: 'H4'
                    halign: 'center'
                    theme_text_color: 'Custom'
                    text_color: 0.18, 0.8, 0.44, 1
                    bold: True
                    size_hint_y: None
                    height: dp(40)
                MDFillRoundFlatButton:
                    id: wheel_btn
                    text: 'SPIN NOW!'
                    font_size: '22sp'
                    size_hint_x: 1
                    size_hint_y: None
                    height: dp(60)
                    md_bg_color: 0.18, 0.8, 0.44, 1
                    on_release: app.start_wheel()

        MDBottomNavigationItem:
            name: 'tab_team'
            text: 'Teams'
            icon: 'account-group'
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                MDLabel:
                    text: 'TEAM SPLITTER'
                    font_style: 'H5'
                    bold: True
                    theme_text_color: 'Custom'
                    text_color: 0.9, 0.49, 0.13, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(30)
                MDTextField:
                    id: team_names_input
                    hint_text: 'Enter player names'
                    helper_text: '(One name per line)'
                    helper_text_mode: 'persistent'
                    mode: "rectangle"
                    multiline: True
                    size_hint_y: 0.4
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    MDTextField:
                        id: team_count_input
                        hint_text: 'Number of teams'
                        input_filter: 'int'
                        halign: 'center'
                    MDFillRoundFlatButton:
                        text: 'SPLIT TEAMS'
                        size_hint_y: 1
                        md_bg_color: 0.9, 0.49, 0.13, 1
                        on_release: app.split_teams()
                MDCard:
                    padding: dp(15)
                    radius: [10, 10, 10, 10]
                    elevation: 1
                    size_hint_y: 0.6
                    ScrollView:
                        MDLabel:
                            id: team_result_label
                            text: 'Results will appear here...'
                            size_hint_y: None
                            height: self.texture_size[1]
                            text_size: self.width, None
'''

class StevenRandomApp(MDApp):
    available_numbers = []
    drawn_numbers = []
    available_names = []
    wheel_items = []
    
    animation_ticks = 0
    final_chosen = None
    current_mode = 'number'
    
    snd_click = None
    snd_win = None
    snd_spin = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        try:
            self.snd_click = SoundLoader.load('click.mp3')
            self.snd_win = SoundLoader.load('win.mp3')
            self.snd_spin = SoundLoader.load('spin.mp3')
        except Exception:
            pass
            
        return Builder.load_string(KV)

    # --- HÀM ÂM THANH ---
    def safe_play(self, sound):
        try:
            if sound:
                sound.stop()
                sound.play()
        except Exception: pass

    # --- TAB NUMBERS ---
    def setup_numbers(self):
        self.safe_play(self.snd_click)
        val = self.root.ids.max_input.text
        if val and val.isdigit() and int(val) > 0:
            self.available_numbers = list(range(1, int(val) + 1))
            self.drawn_numbers = []
            self.root.ids.result_label.text = "?"
            self.root.ids.history_label.text = "No history yet..."
            self.root.ids.status_label.text = f"Total: {len(self.available_numbers)}"
            self.root.ids.draw_btn.disabled = False

    # --- TAB NAMES ---
    def setup_names(self):
        self.safe_play(self.snd_click)
        raw_text = self.root.ids.names_input.text
        names_list = [n.strip() for n in raw_text.split('\n') if n.strip()]
        if names_list:
            self.available_names = names_list
            self.root.ids.name_result_label.text = "Ready!"
            self.root.ids.name_status_label.text = f"Loaded {len(self.available_names)} names."
            self.root.ids.name_draw_btn.disabled = False

    # --- ANIMATION BỐC SỐ/TÊN ---
    def start_draw_animation(self, mode):
        self.safe_play(self.snd_click)
        self.current_mode = mode
        if mode == 'number':
            if not self.available_numbers: return
            self.root.ids.draw_btn.disabled = True
            self.final_chosen = random.choice(self.available_numbers)
        elif mode == 'name':
            if not self.available_names: return
            self.root.ids.name_draw_btn.disabled = True
            self.final_chosen = random.choice(self.available_names)

        self.animation_ticks = 0
        Clock.schedule_interval(self._animate_values, 0.05)

    def _animate_values(self, dt):
        self.animation_ticks += 1
        if self.animation_ticks % 2 == 0: self.safe_play(self.snd_spin)
        
        if self.current_mode == 'number':
            self.root.ids.result_label.text = str(random.choice(self.available_numbers))
        else:
            self.root.ids.name_result_label.text = random.choice(self.available_names)
        
        if self.animation_ticks >= 20:
            Clock.unschedule(self._animate_values)
            self._finish_draw()

    def _finish_draw(self):
        if self.snd_spin: self.snd_spin.stop()
        self.safe_play(self.snd_win)
        
        if self.current_mode == 'number':
            chosen = self.final_chosen
            self.available_numbers.remove(chosen)
            self.drawn_numbers.append(chosen)
            self.root.ids.result_label.text = str(chosen)
            self.root.ids.status_label.text = f"Remaining: {len(self.available_numbers)}"
            self.root.ids.history_label.text = ", ".join(map(str, reversed(self.drawn_numbers)))
            self.root.ids.draw_btn.disabled = False if self.available_numbers else True
        else:
            chosen = self.final_chosen
            self.available_names.remove(chosen)
            self.root.ids.name_result_label.text = str(chosen)
            self.root.ids.name_status_label.text = f"Remaining: {len(self.available_names)}"
            self.root.ids.name_draw_btn.disabled = False if self.available_names else True

    # --- TAB VÒNG QUAY ---
    def start_wheel(self):
        self.safe_play(self.snd_click)
        raw_text = self.root.ids.wheel_input.text
        items = [n.strip() for n in raw_text.split('\n') if n.strip()]
        
        if len(items) < 2:
            self.root.ids.wheel_result_label.text = "Min 2 items!"
            return
            
        gw = self.root.ids.graphic_wheel
        gw.draw_wheel(items)
        
        self.root.ids.wheel_btn.disabled = True
        self.root.ids.wheel_result_label.text = "SPINNING..."
        self.safe_play(self.snd_spin)

        # Chọn người thắng
        winner_idx = random.randint(0, len(items) - 1)
        self.final_chosen = items[winner_idx]
        
        # LOGIC TOÁN HỌC: Kim ở đỉnh (90 độ). 
        # Để item i ở vị trí 90 độ, ta cần xoay: 90 - (góc_item_i)
        N = len(items)
        A = 360.0 / N
        angle_of_winner = winner_idx * A + (A / 2)
        
        # Xoay thêm 5-10 vòng cho hoành tráng
        target_rotation = 90 - angle_of_winner + (360 * random.randint(5, 8))
        
        # Reset góc để không bị xoay ngược
        gw.spin_angle = gw.spin_angle % 360
        
        anim = Animation(spin_angle=target_rotation, duration=4.0, transition='out_quad')
        anim.bind(on_complete=self._finish_wheel)
        anim.start(gw)

    def _finish_wheel(self, *args):
        if self.snd_spin: self.snd_spin.stop()
        self.safe_play(self.snd_win)
        self.root.ids.wheel_result_label.text = self.final_chosen
        self.root.ids.wheel_btn.disabled = False

    # --- TAB CHIA ĐỘI ---
    def split_teams(self):
        self.safe_play(self.snd_click)
        raw_text = self.root.ids.team_names_input.text
        names_list = [n.strip() for n in raw_text.split('\n') if n.strip()]
        team_count_str = self.root.ids.team_count_input.text
        
        if names_list and team_count_str.isdigit():
            team_count = int(team_count_str)
            random.shuffle(names_list)
            teams = {i: [] for i in range(team_count)}
            for index, name in enumerate(names_list):
                teams[index % team_count].append(name)
            
            result_text = ""
            for i in range(team_count):
                result_text += f"[b]TEAM {i+1}:[/b]\n"
                result_text += " • " + "\n • ".join(teams[i]) + "\n\n"
            
            self.root.ids.team_result_label.markup = True
            self.root.ids.team_result_label.text = result_text

if __name__ == '__main__':
    StevenRandomApp().run()
