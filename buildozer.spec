[app]

# (str) Title of your application
title = Random STEVEN

# (str) Package name
package.name = randomsteven

# (str) Package domain
package.domain = org.steven

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

# Biểu tượng ứng dụng (Đảm bảo bạn có file icon.png trong thư mục gốc)
icon.filename = %(source.dir)s/icon.png
icon.adaptive_foreground.filename = %(source.dir)s/icon.png
icon.adaptive_background.filename = %(source.dir)s/icon.png

# Phiên bản
version = 1.0

# (list) Application requirements
# Thêm pillow để hỗ trợ xử lý hình ảnh cho KivyMD nếu cần
requirements = python3,kivy==2.3.0,kivymd>=1.2.0,plyer,pyjnius>=1.4.9,pillow

# Chốt màn hình dọc
orientation = portrait

# ==========================================
# Android specific
# ==========================================

# (int) Target Android API (Android 15)
android.api = 35

# (int) Minimum API support (Android 5.0)
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 35

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Chấp nhận license tự động
android.accept_sdk_license = True

# --- LƯU Ý QUAN TRỌNG ---
# Để file .yml quản lý đường dẫn, chúng ta để trống hoặc khóa 2 dòng này lại
# android.sdk_path = 
# android.ndk_path = 

# (list) Permissions
android.permissions = VIBRATE, INTERNET

# (list) Các kiến trúc chip cho máy Android hiện đại
android.archs = arm64-v8a, armeabi-v7a

# (bool) Fullscreen
fullscreen = 0

# (bool) Copy library
android.copy_libs = 1

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# ==========================================
# Buildozer settings
# ==========================================
[buildozer]

# Log level 2 để soi lỗi kỹ hơn khi build
log_level = 2

warn_on_root = 1

# Định dạng xuất xưởng: aab cho Google Play Store
android.release_artifact = aab
