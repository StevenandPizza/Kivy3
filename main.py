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
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.utils import platform
from kivy.graphics import RoundedRectangle
import math
import random
import os

Window.clearcolor = (0.96, 0.97, 0.98, 1)

if platform not in ('android', 'ios'):
    Window.size = (400, 720)

try:
    from plyer import vibrator
except ImportError:
    vibrator = None


# ==========================================
# SPLASH SCREEN
# ==========================================
class FakeSplashScreen(MDScreen):
    progress_val = NumericProperty(0)
    status_text = StringProperty("")
    _clocks = []

    def on_enter(self, *args):
        fade_in = Animation(opacity=1, duration=0.8)

        def start_loading(*args):
            logo_anim = Animation(opacity=0.6, duration=0.8) + Animation(opacity=1, duration=0.8)
            logo_anim.repeat = True
            logo_anim.start(self.ids.splash_logo)

            self.status_text = "Initializing application..."
            c1 = Clock.schedule_interval(self._update_progress, 0.04)
            c2 = Clock.schedule_once(self._change_status_1, 1.2)
            c3 = Clock.schedule_once(self._change_status_2, 2.5)
            c4 = Clock.schedule_once(self._change_status_3, 3.5)
            self._clocks = [c1, c2, c3, c4]

        fade_in.bind(on_complete=start_loading)
        fade_in.start(self.ids.splash_layout)

    def cleanup(self):
        for c in self._clocks:
            try:
                Clock.unschedule(c)
            except Exception:
                pass
        self._clocks.clear()
        try:
            self.ids.splash_logo.anim_running = False
        except Exception:
            pass

    def _update_progress(self, dt):
        self.progress_val += 1
        if self.progress_val >= 100:
            self.cleanup()
            MDApp.get_running_app().finish_splash()

    def _change_status_1(self, dt): self.status_text = "Optimizing performance..."
    def _change_status_2(self, dt): self.status_text = "Synchronizing data..."
    def _change_status_3(self, dt): self.status_text = "Ready to launch!"


Builder.load_string('''
<FakeSplashScreen>:
    name: 'fake_splash'
    md_bg_color: 0.96, 0.97, 0.98, 1

    MDFloatLayout:
        id: splash_layout
        opacity: 0

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
''')


# ==========================================
# ROULETTE GRAPHIC
# ==========================================
class RouletteGraphic(FloatLayout):
    spin_angle = NumericProperty(0)
    items = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._labels = []
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=0, origin=self.center)
        with self.canvas.after:
            PopMatrix()
        self.bind(spin_angle=self._update_rotation, center=self._update_origin)

    def _update_rotation(self, *args):
        self.rot.angle = self.spin_angle

    def _update_origin(self, *args):
        self.rot.origin = self.center

    def draw_wheel(self, items):
        self.items = items
        self._labels.clear()
        self.clear_widgets()
        self.canvas.clear()

        if not self.items:
            return

        N = len(self.items)
        A = 360.0 / N
        colors = [
            (0.9, 0.3, 0.3, 1), (0.2, 0.6, 0.8, 1), (0.9, 0.7, 0.1, 1),
            (0.2, 0.7, 0.4, 1), (0.6, 0.3, 0.7, 1), (0.9, 0.5, 0.2, 1),
        ]

        with self.canvas:
            for i in range(N):
                Color(*colors[i % len(colors)])
                Ellipse(pos=self.pos, size=self.size, angle_start=i * A, angle_end=(i + 1) * A)

        for i, item in enumerate(self.items):
            angle_pos = i * A + (A / 2)
            rad = math.radians(90 - angle_pos)
            r = self.width * 0.25

            cx = self.center_x + r * math.cos(rad)
            cy = self.center_y + r * math.sin(rad)

            lbl = Label(
                text=str(item)[:8], font_size='14sp', bold=True, color=(1, 1, 1, 1),
                size_hint=(None, None), size=(dp(80), dp(40))
            )
            lbl.center = (cx, cy)
            self.add_widget(lbl)
            self._labels.append(lbl)


# ==========================================
# MAIN SCREEN - COMPLETELY NEW UI
# ==========================================
main_kv = '''
<MainScreen>:
    name: 'main_app'
    md_bg_color: 0.96, 0.97, 0.98, 1

    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    MDBoxLayout:
        orientation: 'vertical'
        spacing: 0
        padding: 0

        # ========== CONTENT - ScreenManager with NoTransition ==========
        ScreenManager:
            id: content_sm
            transition: app.no_trans

            Screen:
                name: 'tab_number'
                md_bg_color: 0.96, 0.97, 0.98, 1

                canvas.before:
                    Color:
                        rgba: 0.96, 0.97, 0.98, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: [dp(20), dp(15), dp(20), dp(10)]
                    spacing: dp(12)

                    MDLabel:
                        text: 'LUCKY NUMBERS'
                        font_style: 'H5'
                        bold: True
                        theme_text_color: 'Primary'
                        halign: 'center'
                        size_hint_y: None
                        height: dp(36)

                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(54)
                        spacing: dp(10)

                        MDTextField:
                            id: max_input
                            hint_text: 'Enter max number'
                            input_filter: 'int'
                            halign: 'center'
                            mode: "round"
                            fill_color: 1, 1, 1, 1
                            line_color_normal: 0.2, 0.5, 0.95, 0.4
                            line_color_focus: 0.2, 0.5, 0.95, 1

                        MDRaisedButton:
                            text: 'SET UP'
                            size_hint_x: 0.3
                            size_hint_y: 1
                            md_bg_color: 0.2, 0.5, 0.95, 1
                            shadow_color: 0.2, 0.5, 0.95, 0.3
                            elevation: 3
                            on_release: app.setup_numbers()

                    MDSeparator:
                        height: dp(1)
                        color: 0.9, 0.92, 0.94, 1

                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: 0.35

                        Widget:
                            MDLabel:
                                id: result_label
                                text: '?'
                                font_style: 'H1'
                                halign: 'center'
                                valign: 'middle'
                                theme_text_color: 'Custom'
                                text_color: 0.2, 0.5, 0.95, 1
                                bold: True
                                pos_hint: {"center_x": .5, "center_y": .6}

                            MDLabel:
                                id: status_label
                                text: 'Ready...'
                                halign: 'center'
                                theme_text_color: 'Secondary'
                                size_hint_y: None
                                height: dp(24)
                                pos_hint: {"center_x": .5, "center_y": .25}

                    MDFillRoundFlatButton:
                        id: draw_btn
                        text: '  DRAW NOW  '
                        font_size: '18sp'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(52)
                        disabled: True
                        md_bg_color: 0.2, 0.5, 0.95, 1
                        shadow_color: 0.2, 0.5, 0.95, 0.4
                        elevation: 4
                        on_release: app.start_draw_animation('number')

                    MDCard:
                        padding: dp(12)
                        radius: [12, 12, 12, 12]
                        elevation: 1
                        size_hint_y: 0.35
                        md_bg_color: 1, 1, 1, 1

                        ScrollView:
                            MDLabel:
                                id: history_label
                                text: 'No history yet...'
                                size_hint_y: None
                                height: self.texture_size[1]
                                text_size: self.width, None
                                theme_text_color: 'Secondary'

            Screen:
                name: 'tab_name'
                md_bg_color: 0.96, 0.97, 0.98, 1

                canvas.before:
                    Color:
                        rgba: 0.96, 0.97, 0.98, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: [dp(20), dp(15), dp(20), dp(10)]
                    spacing: dp(12)

                    MDLabel:
                        text: 'RANDOM PICKER'
                        font_style: 'H5'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: 0.66, 0.33, 0.97, 1
                        halign: 'center'
                        size_hint_y: None
                        height: dp(36)

                    MDTextField:
                        id: names_input
                        hint_text: 'Enter names (one per line)'
                        helper_text: 'One name per line'
                        helper_text_mode: 'persistent'
                        mode: "round"
                        multiline: True
                        size_hint_y: 0.3
                        fill_color: 1, 1, 1, 1
                        line_color_normal: 0.66, 0.33, 0.97, 0.4
                        line_color_focus: 0.66, 0.33, 0.97, 1

                    MDRaisedButton:
                        text: 'LOAD LIST'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(48)
                        md_bg_color: 0.66, 0.33, 0.97, 1
                        shadow_color: 0.66, 0.33, 0.97, 0.3
                        elevation: 3
                        on_release: app.setup_names()

                    MDSeparator:
                        height: dp(1)
                        color: 0.9, 0.92, 0.94, 1

                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: 0.3

                        Widget:
                            MDLabel:
                                id: name_result_label
                                text: 'Who is next?'
                                font_style: 'H4'
                                halign: 'center'
                                valign: 'middle'
                                theme_text_color: 'Custom'
                                text_color: 0.66, 0.33, 0.97, 1
                                bold: True
                                pos_hint: {"center_x": .5, "center_y": .6}

                            MDLabel:
                                id: name_status_label
                                text: 'Waiting for names...'
                                halign: 'center'
                                theme_text_color: 'Secondary'
                                size_hint_y: None
                                height: dp(24)
                                pos_hint: {"center_x": .5, "center_y": .25}

                    MDFillRoundFlatButton:
                        id: name_draw_btn
                        text: '  PICK SOMEONE  '
                        font_size: '18sp'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(52)
                        disabled: True
                        md_bg_color: 0.66, 0.33, 0.97, 1
                        shadow_color: 0.66, 0.33, 0.97, 0.4
                        elevation: 4
                        on_release: app.start_draw_animation('name')

            Screen:
                name: 'tab_wheel'
                md_bg_color: 0.96, 0.97, 0.98, 1

                canvas.before:
                    Color:
                        rgba: 0.96, 0.97, 0.98, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: [dp(15), dp(10), dp(15), dp(10)]
                    spacing: dp(8)

                    MDLabel:
                        text: 'SPIN THE WHEEL'
                        font_style: 'H5'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: 0.18, 0.8, 0.44, 1
                        halign: 'center'
                        size_hint_y: None
                        height: dp(36)

                    MDTextField:
                        id: wheel_input
                        hint_text: 'Enter items (one per line)'
                        helper_text: 'Minimum 2 items'
                        helper_text_mode: 'persistent'
                        mode: "round"
                        multiline: True
                        size_hint_y: 0.2
                        fill_color: 1, 1, 1, 1
                        line_color_normal: 0.18, 0.8, 0.44, 0.4
                        line_color_focus: 0.18, 0.8, 0.44, 1

                    MDFloatLayout:
                        size_hint_y: 0.45

                        RouletteGraphic:
                            id: graphic_wheel
                            size_hint: None, None
                            size: dp(260), dp(260)
                            pos_hint: {"center_x": .5, "center_y": .5}

                        MDIcon:
                            icon: "menu-down"
                            font_size: "55sp"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 0.8
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
                        height: dp(36)

                    MDFillRoundFlatButton:
                        id: wheel_btn
                        text: '  SPIN NOW!  '
                        font_size: '20sp'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(54)
                        md_bg_color: 0.18, 0.8, 0.44, 1
                        shadow_color: 0.18, 0.8, 0.44, 0.4
                        elevation: 4
                        on_release: app.start_wheel()

            Screen:
                name: 'tab_team'
                md_bg_color: 0.96, 0.97, 0.98, 1

                canvas.before:
                    Color:
                        rgba: 0.96, 0.97, 0.98, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: [dp(20), dp(15), dp(20), dp(10)]
                    spacing: dp(12)

                    MDLabel:
                        text: 'TEAM SPLITTER'
                        font_style: 'H5'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: 0.9, 0.49, 0.13, 1
                        halign: 'center'
                        size_hint_y: None
                        height: dp(36)

                    MDTextField:
                        id: team_names_input
                        hint_text: 'Enter player names (one per line)'
                        helper_text: 'One name per line'
                        helper_text_mode: 'persistent'
                        mode: "round"
                        multiline: True
                        size_hint_y: 0.3
                        fill_color: 1, 1, 1, 1
                        line_color_normal: 0.9, 0.49, 0.13, 0.4
                        line_color_focus: 0.9, 0.49, 0.13, 1

                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(54)
                        spacing: dp(10)

                        MDTextField:
                            id: team_count_input
                            hint_text: 'Number of teams'
                            input_filter: 'int'
                            halign: 'center'
                            mode: "round"
                            fill_color: 1, 1, 1, 1
                            line_color_normal: 0.9, 0.49, 0.13, 0.4
                            line_color_focus: 0.9, 0.49, 0.13, 1

                        MDRaisedButton:
                            text: 'SPLIT'
                            size_hint_x: 0.3
                            size_hint_y: 1
                            md_bg_color: 0.9, 0.49, 0.13, 1
                            shadow_color: 0.9, 0.49, 0.13, 0.3
                            elevation: 3
                            on_release: app.split_teams()

                    MDCard:
                        padding: dp(12)
                        radius: [12, 12, 12, 12]
                        elevation: 1
                        size_hint_y: 0.55
                        md_bg_color: 1, 1, 1, 1

                        ScrollView:
                            MDLabel:
                                id: team_result_label
                                text: 'Results will appear here...'
                                size_hint_y: None
                                height: self.texture_size[1]
                                text_size: self.width, None
                                theme_text_color: 'Secondary'

        # ========== CUSTOM BOTTOM TAB BAR ==========
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            md_bg_color: 1, 1, 1, 1
            spacing: 0
            padding: 0

            canvas.before:
                Color:
                    rgba: 0.9, 0.92, 0.94, 1
                Rectangle:
                    pos: self.pos
                    size: self.width, dp(1)
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.x, self.y + dp(1)
                    size: self.width, self.height - dp(1)

            MDBoxLayout:
                id: tab_number_btn
                orientation: 'vertical'
                size_hint_x: 0.25
                spacing: dp(2)
                padding: [0, dp(6), 0, dp(4)]

                MDIcon:
                    id: tab_number_icon
                    icon: 'numeric'
                    font_size: '24sp'
                    halign: 'center'
                    size_hint_y: 0.6
                    theme_text_color: 'Custom'
                    text_color: app._tab_active_color
                    on_release: app.switch_tab('tab_number')

                MDLabel:
                    text: 'Numbers'
                    font_size: '10sp'
                    halign: 'center'
                    size_hint_y: 0.4
                    theme_text_color: 'Custom'
                    text_color: app._tab_active_color
                    on_release: app.switch_tab('tab_number')

            MDBoxLayout:
                id: tab_name_btn
                orientation: 'vertical'
                size_hint_x: 0.25
                spacing: dp(2)
                padding: [0, dp(6), 0, dp(4)]

                MDIcon:
                    id: tab_name_icon
                    icon: 'account-star'
                    font_size: '24sp'
                    halign: 'center'
                    size_hint_y: 0.6
                    theme_text_color: 'Custom'
                    text_color: app._tab_inactive_color
                    on_release: app.switch_tab('tab_name')

                MDLabel:
                    text: 'Names'
                    font_size: '10sp'
                    halign: 'center'
                    size_hint_y: 0.4
                    theme_text_color: 'Custom'
                    text_color: app._tab_inactive_color
                    on_release: app.switch_tab('tab_name')

            MDBoxLayout:
                id: tab_wheel_btn
                orientation: 'vertical'
                size_hint_x: 0.25
                spacing: dp(2)
                padding: [0, dp(6), 0, dp(4)]

                MDIcon:
                    id: tab_wheel_icon
                    icon: 'sync-circle'
                    font_size: '24sp'
                    halign: 'center'
                    size_hint_y: 0.6
                    theme_text_color: 'Custom'
                    text_color: app._tab_inactive_color
                    on_release: app.switch_tab('tab_wheel')

                MDLabel:
                    text: 'Wheel'
                    font_size: '10sp'
                    halign: 'center'
                    size_hint_y: 0.4
                    theme_text_color: 'Custom'
                    text_color: app._tab_inactive_color
                    on_release: app.switch_tab('tab_wheel')

            MDBoxLayout:
                id: tab_team_btn
                orientation: 'vertical'
                size_hint_x: 0.25
                spacing: dp(2)
                padding: [0, dp(6), 0, dp(4)]

                MDIcon:
                    id: tab_team_icon
                    icon: 'account-group'
                    font_size: '24sp'
                    halign: 'center'
                    size_hint_y: 0.6
                    theme_text_color: 'Custom'
                    text_color: app._tab_inactive_color
                    on_release: app.switch_tab('tab_team')

                MDLabel:
                    text: 'Teams'
                    font_size: '10sp'
                    halign: 'center'
                    size_hint_y: 0.4
                    theme_text_color: 'Custom'
                    text_color: app._tab_inactive_color
                    on_release: app.switch_tab('tab_team')
'''
Builder.load_string(main_kv)


class MainScreen(MDScreen):
    pass


# ==========================================
# MAIN APP
# ==========================================
class StevenRandomApp(MDApp):
    sm = ObjectProperty(None)
    _main_ids = None
    _anim_clock = None
    _sounds_loaded = False
    _tab_colors = {
        'tab_number': (0.2, 0.5, 0.95, 1),
        'tab_name': (0.66, 0.33, 0.97, 1),
        'tab_wheel': (0.18, 0.8, 0.44, 1),
        'tab_team': (0.9, 0.49, 0.13, 1),
    }
    _tab_active_color = (0.5, 0.5, 0.5, 1)
    _tab_inactive_color = (0.7, 0.72, 0.75, 1)

    available_numbers = []
    drawn_numbers = []
    available_names = []

    animation_ticks = 0
    final_chosen = None
    current_mode = 'number'

    snd_click = None
    snd_win = None
    snd_spin = None
    no_trans = NoTransition()

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(FakeSplashScreen())
        self.sm.add_widget(MainScreen())
        self.sm.current = 'fake_splash'

        return self.sm

    def _ensure_sounds(self):
        if self._sounds_loaded:
            return
        click_path = self._find_file('click.ogg')
        win_path = self._find_file('win.ogg')
        spin_path = self._find_file('spin.ogg')
        self.snd_click = SoundLoader.load(click_path) if click_path else None
        self.snd_win = SoundLoader.load(win_path) if win_path else None
        self.snd_spin = SoundLoader.load(spin_path) if spin_path else None
        self._sounds_loaded = True

    def _find_file(self, filename):
        if os.path.exists(filename):
            return filename
        for ext in ['.ogg', '.mp3', '.wav']:
            base = filename.rsplit('.', 1)[0]
            path = base + ext
            if os.path.exists(path):
                return path
        return None

    def finish_splash(self):
        self.sm.current = 'main_app'
        Clock.schedule_once(lambda dt: self._post_init(), 0.1)

    def _post_init(self):
        ids = self._get_ids()
        self.no_trans = NoTransition()
        ids.content_sm.transition = self.no_trans
        self.switch_tab('tab_number')

    def switch_tab(self, tab_name):
        ids = self._get_ids()
        ids.content_sm.current = tab_name

        for name, color in self._tab_colors.items():
            icon = ids.get(f'{name}_icon')
            label = ids.get(f'{name}_icon')
            if icon:
                icon.text_color = color if name == tab_name else self._tab_inactive_color
            lbl_widget = ids.get(f'{name}_btn').children[1]
            if lbl_widget and hasattr(lbl_widget, 'text_color'):
                lbl_widget.text_color = color if name == tab_name else self._tab_inactive_color

    def _get_ids(self):
        if self._main_ids is None:
            self._main_ids = self.sm.get_screen('main_app').ids
        return self._main_ids

    def stop_all_sounds(self):
        self._ensure_sounds()
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
        ids = self._get_ids()
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
        ids = self._get_ids()
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
        ids = self._get_ids()
        self.stop_all_sounds()
        self.safe_play(self.snd_click)
        self.current_mode = mode

        if mode == 'number':
            if not self.available_numbers:
                return
            ids.draw_btn.disabled = True
            self.final_chosen = random.choice(self.available_numbers)
        elif mode == 'name':
            if not self.available_names:
                return
            ids.name_draw_btn.disabled = True
            self.final_chosen = random.choice(self.available_names)

        self.animation_ticks = 0
        self._cancel_animation()
        self._anim_clock = Clock.schedule_interval(self._animate_values, 0.05)

    def _cancel_animation(self):
        if self._anim_clock is not None:
            try:
                Clock.unschedule(self._anim_clock)
            except Exception:
                pass
            self._anim_clock = None

    def _animate_values(self, dt):
        ids = self._get_ids()
        self.animation_ticks += 1

        if self.animation_ticks < 19 and self.animation_ticks % 2 == 0:
            self.safe_play(self.snd_spin)

        if self.current_mode == 'number':
            ids.result_label.text = str(random.choice(self.available_numbers))
        else:
            ids.name_result_label.text = random.choice(self.available_names)

        if self.animation_ticks >= 20:
            self._cancel_animation()
            self._finish_draw()

    def _finish_draw(self):
        ids = self._get_ids()
        if self.snd_spin:
            self.snd_spin.stop()
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
        ids = self._get_ids()
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
        target_rotation = current_spins + (360 * random.randint(5, 8)) + angle_of_winner

        anim = Animation(spin_angle=target_rotation, duration=4.0, transition='out_quad')
        anim.bind(on_complete=self._finish_wheel)
        anim.start(gw)

    def _finish_wheel(self, *args):
        ids = self._get_ids()
        if self.snd_spin:
            self.snd_spin.stop()
        Clock.schedule_once(lambda dt: self.safe_play(self.snd_win), 0.1)
        ids.wheel_result_label.text = self.final_chosen
        ids.wheel_btn.disabled = False

    def split_teams(self):
        ids = self._get_ids()
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
                result_text += f"[color=#3377ff][b]TEAM {i + 1}:[/b][/color]\n"
                result_text += " • " + "\n • ".join(teams[i]) + "\n\n"

            ids.team_result_label.markup = True
            ids.team_result_label.text = result_text


if __name__ == '__main__':
    StevenRandomApp().run()
