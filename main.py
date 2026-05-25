from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, StringProperty
from kivy.graphics import Color, Ellipse, PushMatrix, PopMatrix, Rotate
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
import math
import random
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, FadeTransition

# Cố định màu nền cửa sổ ngay lập tức để tránh vệt đen từ lõi
Window.clearcolor = (0.96, 0.97, 0.98, 1)

if platform not in ('android', 'ios'):
    Window.size = (400, 700)

try:
    from plyer import vibrator
except ImportError:
    vibrator = None

# ==========================================
# [PHẦN 1] MÀN HÌNH CHÀO (ENGLISH VERSION)
# ==========================================
class FakeSplashScreen(MDScreen):
    progress_val = NumericProperty(0)
    status_text = StringProperty("Initializing application...")

    def on_enter(self, *args):
        logo_anim = Animation(opacity=0.6, duration=0.8) + Animation(opacity=1, duration=0.8)
        logo_anim.repeat = True
        logo_anim.start(self.ids.splash_logo)
        
        Clock.schedule_interval(self._update_progress, 0.04)
        
        Clock.schedule_once(self._change_status_1, 1.2)
        Clock.schedule_once(self._change_status_2, 2.5)
        Clock.schedule_once(self._change_status_3, 3.5)

    def _update_progress(self, dt):
        self.progress_val += 1
        if self.progress_val >= 100:
            Clock.unschedule(self._update_progress)
            MDApp.get_running_app().finish_splash()

    def _change_status_1(self, dt): self.status_text = "Optimizing performance..."
    def _change_status_2(self, dt): self.status_text = "Synchronizing data..."
    def _change_status_3(self, dt): self.status_text = "Ready to launch!"

fake_splash_kv = '''
<FakeSplashScreen>:
    name: 'fake_splash'
    md_bg_color: 0.96, 0.97, 0.98, 1

    MDFloatLayout:
        FitImage:
            id: splash_logo
            source: 'icon.png'
            size_hint: None, None
            size: dp(140), dp(140)
            pos_hint: {"center_x": .5, "center_y": .6}

        MDProgressBar:
            id: progress_bar
            value: root.progress_val
            size_hint_x: 0.6
            pos_hint: {"center_x": .5, "center_y": .42}
            color: app.theme_cls.primary_color
            
        MDLabel:
            text: root.status_text
            font_style: 'Caption'
            theme_text_color: "Secondary"
            halign: "center"
            size_hint_y: None
            height: dp(30)
            pos_hint: {"center_x": .5, "center_y": .38}
'''
Builder.load_string(fake_splash_kv)

# ==========================================
# [PHẦN 2] ĐỒ HỌA VÒNG QUAY (KHÓA ĐỒNG BỘ CANVAS)
# ==========================================
class RouletteGraphic(FloatLayout):
    spin_angle = NumericProperty(0)
    items = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Khóa origin vào chính giữa để xoay nguyên khối
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=0, origin=self.center)
        with self.canvas.after:
            PopMatrix()
        self.bind(spin_angle=self._update_rotation, center=self._update_layout, size=self._update_layout)

    def _update_rotation(self, *args):
        self.rot.angle = self.spin_angle

    def _update_layout(self, *args):
        self.rot.origin = self.center
        if self.items:
            self.draw_wheel(self.items)

    def draw_wheel(self, items):
        self.items = items
        self.clear_widgets()
        self.canvas.clear()
        
        if not self.items: return
        
        N = len(self.items)
        A = 360.0 / N
        colors = [(0.9, 0.3, 0.3, 1), (0.2, 0.6, 0.8, 1), (0.9, 0.7, 0.1, 1), 
                  (0.2, 0.7, 0.4, 1), (0.6, 0.3, 0.7, 1), (0.9, 0.5, 0.2, 1)]
                  
        with self.canvas:
            for i in range(N):
                Color(*colors[i % len(colors)])
                Ellipse(pos=self.pos, size=self.size, angle_start=i*A, angle_end=(i+1)*A)

        for i, item in enumerate(self.items):
            angle_pos = i * A + (A / 2)
            rad = math.radians(90 - angle_pos)
            r = self.width * 0.25 
            
            cx = self.center_x + r * math.cos(rad)
            cy = self.center_y + r * math.sin(rad)
            
            lbl = Label(text=str(item)[:8], font_size='14sp', bold=True, color=(1,1,1,1),
                        size_hint=(None, None), size=(dp(80), dp(40)))
            
            with lbl.canvas.before:
                PushMatrix()
                Rotate(angle=angle_pos, origin=(cx, cy))
            with lbl.canvas.after:
                PopMatrix()
                
            lbl.center = (cx, cy)
            self.add_widget(lbl)

# ==========================================
# [PHẦN 3] GIAO DIỆN CHÍNH (FULL CHỨC NĂNG, KHÔNG LẰN ĐEN)
# ==========================================
main_screen_kv = '''
<MainScreen>:
    name: 'main_app'
    md_bg_color: 0.96, 0.97, 0.98, 1

    MDBottomNavigation:
        panel_color: 1, 1, 1, 1
        selected_color_background: app.theme_cls.primary_color
        text_color_active: app.theme_cls.primary_color

        MDBottomNavigationItem:
            name: 'tab_number'
            text: 'Numbers'
            icon: 'numeric'
            md_bg_color: 0.96, 0.97, 0.98, 1
            
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                md_bg_color: 0.96, 0.97, 0.98, 1
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
                    elevation: 1
                    md_bg_color: 1, 1, 1, 1
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
                    md_bg_color: 1, 1, 1, 1
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
            md_bg_color: 0.96, 0.97, 0.98, 1
            
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                md_bg_color: 0.96, 0.97, 0.98, 1
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
                    elevation: 1
                    md_bg_color: 1, 1, 1, 1
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
            md_bg_color: 0.96, 0.97, 0.98, 1
            
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                md_bg_color: 0.96, 0.97, 0.98, 1
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
            md_bg_color: 0.96, 0.97, 0.98, 1
            
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                md_bg_color: 0.96, 0.97, 0.98, 1
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
                    md_bg_color: 1, 1, 1, 1
                    size_hint_y: 0.6
                    ScrollView:
                        MDLabel:
                            id: team_result_label
                            text: 'Results will appear here...'
                            size_hint_y: None
                            height: self.texture_size[1]
                            text_size: self.width, None
'''
Builder.load_string(main_screen_kv)

class MainScreen(MDScreen):
    pass

class StevenRandomApp(MDApp):
    sm = ObjectProperty(None)
    
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
        
        self.snd_click = SoundLoader.load('click.ogg')
        self.snd_win   = SoundLoader.load('win.ogg')
        self.snd_spin  = SoundLoader.load('spin.ogg')

        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(FakeSplashScreen())
        self.sm.add_widget(MainScreen())
        self.sm.current = 'fake_splash'
            
        return self.sm

    def finish_splash(self):
        self.sm.current = 'main_app'

    def get_main_ids(self):
        return self.sm.get_screen('main_app').ids

    def stop_all_sounds(self):
        for snd in [self.snd_spin, self.snd_win, self.snd_click]:
            try:
                if snd and snd.state == 'play':
                    snd.stop()
            except Exception:
                pass

    def safe_play(self, sound):
        try:
            if sound:
                if sound.state == 'play':
                    sound.stop()
                sound.seek(0)
                sound.play()
        except Exception:
            pass

    def setup_numbers(self):
        ids = self.get_main_ids()
        self.stop_all_sounds()
        self.safe_play(self.snd_click)
        val = ids.max_input.text
        if val and val.isdigit() and int(val) > 0:
            self.available_numbers = list(range(1, int(val) + 1))
            self.drawn_numbers = []
            ids.result_label.text = "?"
            ids.history_label.text = "No history yet..."
            ids.status_label.text = f"Total: {len(self.available_numbers)}"
            ids.draw_btn.disabled = False

    def setup_names(self):
        ids = self.get_main_ids()
        self.stop_all_sounds()
        self.safe_play(self.snd_click)
        raw_text = ids.names_input.text
        names_list = [n.strip() for n in raw_text.split('\n') if n.strip()]
        if names_list:
            self.available_names = names_list
            ids.name_result_label.text = "Ready!"
            ids.name_status_label.text = f"Loaded {len(self.available_names)} names."
            ids.name_draw_btn.disabled = False

    def start_draw_animation(self, mode):
        ids = self.get_main_ids()
        self.stop_all_sounds()
        self.safe_play(self.snd_click)
        self.current_mode = mode

        if mode == 'number':
            if not self.available_numbers: return
            ids.draw_btn.disabled = True
            self.final_chosen = random.choice(self.available_numbers)
        elif mode == 'name':
            if not self.available_names: return
            ids.name_draw_btn.disabled = True
            self.final_chosen = random.choice(self.available_names)

        self.animation_ticks = 0
        Clock.schedule_interval(self._animate_values, 0.05)

    def _animate_values(self, dt):
        ids = self.get_main_ids()
        self.animation_ticks += 1

        if self.animation_ticks < 19 and self.animation_ticks % 2 == 0:
            self.safe_play(self.snd_spin)
        
        if self.current_mode == 'number':
            ids.result_label.text = str(random.choice(self.available_numbers))
        else:
            ids.name_result_label.text = random.choice(self.available_names)
        
        if self.animation_ticks >= 20:
            Clock.unschedule(self._animate_values)
            self._finish_draw()

    def _finish_draw(self):
        ids = self.get_main_ids()
        if self.snd_spin: self.snd_spin.stop()
        Clock.schedule_once(lambda dt: self.safe_play(self.snd_win), 0.1)

        if self.current_mode == 'number':
            chosen = self.final_chosen
            self.available_numbers.remove(chosen)
            self.drawn_numbers.append(chosen)
            ids.result_label.text = str(chosen)
            ids.status_label.text = f"Remaining: {len(self.available_numbers)}"
            ids.history_label.text = ", ".join(map(str, reversed(self.drawn_numbers)))
            ids.draw_btn.disabled = False if self.available_numbers else True
        else:
            chosen = self.final_chosen
            self.available_names.remove(chosen)
            ids.name_result_label.text = str(chosen)
            ids.name_status_label.text = f"Remaining: {len(self.available_names)}"
            ids.name_draw_btn.disabled = False if self.available_names else True

    def start_wheel(self):
        ids = self.get_main_ids()
        self.stop_all_sounds()
        self.safe_play(self.snd_click)

        raw_text = ids.wheel_input.text
        items = [n.strip() for n in raw_text.split('\n') if n.strip()]
        
        if len(items) < 2:
            ids.wheel_result_label.text = "Min 2 items!"
            return
            
        gw = ids.graphic_wheel
        gw.draw_wheel(items)
        
        ids.wheel_btn.disabled = True
        ids.wheel_result_label.text = "SPINNING..."

        Clock.schedule_once(lambda dt: self.safe_play(self.snd_spin), 0.15)

        winner_idx = random.randint(0, len(items) - 1)
        self.final_chosen = items[winner_idx]
        
        N = len(items)
        A = 360.0 / N
        angle_of_winner = winner_idx * A + (A / 2)
        
        current_spins = (gw.spin_angle // 360) * 360
        
        # ==========================================
        # FIX LỖI SKIBIDI TRẢ RA RONALDO: 
        # Xóa số 360 trừ đi, trả lại đúng góc của ô trúng thưởng
        # ==========================================
        target_rotation = current_spins + (360 * random.randint(5, 8)) + angle_of_winner
        
        anim = Animation(spin_angle=target_rotation, duration=4.0, transition='out_quad')
        anim.bind(on_complete=self._finish_wheel)
        anim.start(gw)

    def _finish_wheel(self, *args):
        ids = self.get_main_ids()
        if self.snd_spin: self.snd_spin.stop()
        Clock.schedule_once(lambda dt: self.safe_play(self.snd_win), 0.1)
        ids.wheel_result_label.text = self.final_chosen
        ids.wheel_btn.disabled = False

    def split_teams(self):
        ids = self.get_main_ids()
        self.stop_all_sounds()
        self.safe_play(self.snd_click)
        raw_text = ids.team_names_input.text
        names_list = [n.strip() for n in raw_text.split('\n') if n.strip()]
        team_count_str = ids.team_count_input.text
        
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
            
            ids.team_result_label.markup = True
            ids.team_result_label.text = result_text

if __name__ == '__main__':
    StevenRandomApp().run()
