[app]

# (str) Title of your application
title = Random Anything

# (str) Package name
package.name = randomsteven

# (str) Package domain
package.domain = org.steven

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ogg

# Màn hình chờ tàng hình
presplash.filename = %(source.dir)s/blank.png

# Biểu tượng ứng dụng
icon.filename = %(source.dir)s/icon.png

# Đổ màu nền xung quanh cái logo
presplash.color = #F5F7FA
android.presplash_color = #F5F7FA

# BẬT LẠI Adaptive Icon để đạt chuẩn UI Rules của Android 16
icon.adaptive_foreground.filename = %(source.dir)s/icon.png
icon.adaptive_background.filename = %(source.dir)s/blank.png

# Phiên bản
version = 1.7

# (list) Application requirements
requirements = python3,kivy==2.3.1,kivymd==1.1.1,plyer,pillow==10.4.0

# Chốt màn hình dọc
orientation = portrait

# ==========================================
# Android specific
# ==========================================

# (int) Target Android API (Nâng lên 36 cho Android 16)
android.api = 36

# (int) Minimum API support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 36

# (str) Android NDK version to use (Bắt buộc lên 27c để hỗ trợ 16KB Page Size)
android.ndk = 27c

# (bool) Chấp nhận license tự động
android.accept_sdk_license = True

# (list) Permissions
android.permissions = VIBRATE, INTERNET

# (list) Các kiến trúc chip cho máy Android hiện đại (Bắt buộc cho Google Play)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Fullscreen
fullscreen = 0

# (bool) Copy library
android.copy_libs = 1

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# Xuất file APK để cài trực tiếp trên điện thoại
android.release_artifact = apk

# ==========================================
# Buildozer settings
# ==========================================
[buildozer]

# Log level 2 để soi lỗi kỹ hơn khi build
log_level = 2

warn_on_root = 1

# Trigger rebuild

