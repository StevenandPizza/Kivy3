import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform

# Chỉnh kích thước cửa sổ giả lập giống màn hình điện thoại (Chỉ có tác dụng trên máy tính)
# Chỉnh kích thước cửa sổ giả lập (Chỉ có tác dụng trên máy tính)
if platform not in ('android', 'ios'):
    Window.size = (400, 700)

# KV Language: Giao diện sạch sẽ và tách biệt
KV = '''
<RandomAppWidget>:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(15)
    
    # Đổ màu nền cho toàn bộ app (Màu xám nhạt hiện đại)
    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.98, 1  
        Rectangle:
            pos: self.pos
            size: self.size

    # --- TIÊU ĐỀ ---
    Label:
        text: 'RANDOM CÙNG STEVEN'
        font_size: sp(26)
        bold: True
        color: 0.17, 0.24, 0.31, 1
        size_hint_y: None
        height: dp(40)

    # --- KHU VỰC NHẬP SỐ LỚN NHẤT ---
    BoxLayout:
        size_hint_y: None
        height: dp(50)
        spacing: dp(10)
        
        TextInput:
            id: max_input
            hint_text: 'Nhập số...'
            input_filter: 'int'
            multiline: False
            font_size: sp(18)
            halign: 'center'
            padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
            
        Button:
            text: 'Thiết Lập'
            size_hint_x: 0.5
            background_normal: ''
            background_color: 0.2, 0.6, 0.86, 1
            bold: True
            on_release: root.setup_numbers()

    # --- KHU VỰC HIỂN THỊ KẾT QUẢ ---
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [15,]
        
        Label:
            id: result_label
            text: '?'
            font_size: sp(90)
            bold: True
            color: 0.66, 0.33, 0.97, 1
            
        Label:
            id: status_label
            text: 'Sẵn sàng...'
            font_size: sp(14)
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: dp(40)

    # --- NÚT QUAY SỐ ---
    Button:
        id: draw_btn
        text: 'QUAY SỐ NGAY'
        size_hint_y: None
        height: dp(65)
        background_normal: ''
        background_color: 0.18, 0.8, 0.44, 1
        font_size: sp(20)
        bold: True
        disabled: True
        on_release: root.draw_number()

    # --- LỊCH SỬ CÁC SỐ ĐÃ RÚT ---
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.6
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [10,]
        padding: dp(15)
        
        Label:
            text: 'Lịch sử đã quay:'
            color: 0.17, 0.24, 0.31, 1
            bold: True
            size_hint_y: None
            height: dp(30)
            text_size: self.size
            halign: 'left'
            
        ScrollView:
            Label:
                id: history_label
                text: 'Chưa có lịch sử...'
                color: 0.3, 0.3, 0.3, 1
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'left'
                valign: 'top'

    # --- NÚT LÀM MỚI ---
    Button:
        text: 'Tạo Lại Dãy Số Mới'
        size_hint_y: None
        height: dp(50)
        background_normal: ''
        background_color: 0.9, 0.49, 0.13, 1
        bold: True
        on_release: root.reset_app()
'''

class RandomAppWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.available_numbers = []
        self.drawn_numbers = []

    def setup_numbers(self):
        val = self.ids.max_input.text
        if val and val.isdigit() and int(val) > 0:
            max_val = int(val)
            self.available_numbers = list(range(1, max_val + 1))
            self.drawn_numbers = []
            
            # Cập nhật Giao diện
            self.ids.result_label.text = "?"
            self.ids.history_label.text = "Chưa có lịch sử..."
            self.ids.status_label.text = f"Đã tạo 1 đến {max_val}. Còn lại: {len(self.available_numbers)}"
            self.ids.draw_btn.disabled = False 

    def draw_number(self):
        if not self.available_numbers:
            return
            
        # Quay số ngẫu nhiên
        chosen = random.choice(self.available_numbers)
        self.available_numbers.remove(chosen)
        self.drawn_numbers.append(chosen)
        
        # Cập nhật Giao diện
        self.ids.result_label.text = str(chosen)
        self.ids.status_label.text = f"Số vừa rút: {chosen}. Còn lại: {len(self.available_numbers)}"
        
        # Nối chuỗi lịch sử (Số mới nhất lên đầu)
        history_str = ", ".join(map(str, reversed(self.drawn_numbers)))
        self.ids.history_label.text = history_str
        
        # Khóa nút nếu hết số
        if not self.available_numbers:
            self.ids.draw_btn.disabled = True
            self.ids.status_label.text = "Đã quay hết các số!"

    def reset_app(self):
        self.ids.max_input.text = ''
        self.available_numbers = []
        self.drawn_numbers = []
        self.ids.result_label.text = "?"
        self.ids.status_label.text = "Sẵn sàng..."
        self.ids.history_label.text = "Chưa có lịch sử..."
        self.ids.draw_btn.disabled = True

class RandomApp(App):
    def build(self):
        Builder.load_string(KV)
        return RandomAppWidget()

if __name__ == '__main__':
    RandomApp().run()
