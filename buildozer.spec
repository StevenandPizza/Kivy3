[app]

# (str) Title of your application
title = Random STEVEN

# (str) Package name
package.name = randomsteven

# (str) Package domain (needed for android/ios packaging)
package.domain = org.steven

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
# Đã thêm mp3 và wav để sẵn sàng cho tính năng âm thanh
source.include_exts = py,png,jpg,kv,atlas,mp3,wav
#Thêm logo
icon.filename = %(source.dir)s/icon.png
# (str) Adaptive icon of the application (used if Android API level is 26+ at runtime)
icon.adaptive_foreground.filename = %(source.dir)s/icon.png
icon.adaptive_background.filename = %(source.dir)s/icon.png
# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# Đã thêm kivymd và plyer (thư viện rung)
requirements = python3,kivy,kivymd,plyer,pyjnius>=1.4.9

# (list) Supported orientations
# Chốt màn hình dọc để giao diện không bị vỡ khi xoay ngang máy
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# Cấp quyền rung vật lý cho thiết bị
android.permissions = VIBRATE

# (int) Target Android API, should be as high as possible.
# Nâng cấp lên API 35 theo chuẩn Android mới nhất
android.api = 35

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
