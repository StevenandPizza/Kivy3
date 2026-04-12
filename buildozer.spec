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

# Biểu tượng ứng dụng
icon.filename = %(source.dir)s/icon.png
icon.adaptive_foreground.filename = %(source.dir)s/icon.png
icon.adaptive_background.filename = %(source.dir)s/icon.png

# Phiên bản
version = 1.0

# (list) Application requirements
requirements = python3,kivy==2.3.0,kivymd>=1.2.0,plyer,pyjnius>=1.4.9

# Chốt màn hình dọc
orientation = portrait

# ==========================================
# Android specific (CẤU HÌNH API 35 CHUẨN)
# ==========================================

# (int) Target Android API
android.api = 35

# (int) Minimum API support (Android 5.0)
android.minapi = 21

# (bool) Chấp nhận license tự động
android.accept_sdk_license = True

# --- PHẦN QUAN TRỌNG NHẤT ĐỂ FIX LỖI API 35 ---
# Ép Buildozer dùng "kho phụ tùng" của GitHub Actions
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724

# (list) Permissions
android.permissions = VIBRATE, INTERNET

# (list) Các kiến trúc chip (Bắt buộc cho Play Store)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Fullscreen
fullscreen = 0

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (bool) Copy library
android.copy_libs = 1

# ==========================================
# Buildozer settings
# ==========================================
[buildozer]

# Log level 2 để soi lỗi kỹ hơn
log_level = 2

warn_on_root = 1

# Định dạng xuất xưởng: aab cho Google Play
android.release_artifact = aab
