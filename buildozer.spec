[app]
title = System Update
package.name = system.update.tool
package.domain = org.krollos
source.dir = .
version = 2.0
requirements = python3,kivy,plyer,requests,urllib3,certifi

# الصلاحيات كاملة لضمان العمل على أندرويد 15
android.permissions = INTERNET, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.api = 34
android.minapi = 21
android.archs = arm64-v8a
orientation = portrait
