import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد مكتبة الصلاة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# تصميم CSS: وضوح عالي، إضاءة معتدلة، ألوان بارزة
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@800&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; background-attachment: fixed;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }
    .main-container { text-align: center; color: white; width: 100%; }
    .time-text { font-size: 17vw; font-weight: 800; color: #FFFFFF; text-shadow: 2px 2px 10px rgba(0,0,0,0.7); }
    .ampm-text { font-size: 6vw; color: #00FF00; vertical-align: super; font-weight: bold; }
    .date-row { font-size: 5.5vw; color: #FFA500; font-weight: 800; margin-bottom: 10px; }
    .prayer-card {
        background: #FFFFFF; padding: 15px; border-radius: 20px;
        box-shadow: 0 8px 15px rgba(0,0,0,0.4); margin: 20px auto; 
        width: 90%; max-width: 350px; border-bottom: 5px solid #008800;
    }
    .prayer-label { font-size: 20px; color: #333333; font-weight: bold; margin: 0; }
    .countdown { font-size: 11vw; color: #008800; font-weight: bold; font-family: 'Courier New', monospace; }
    .footer { margin-top: 25px; font-size: 16px; font-weight: bold; }
    .footer a { color: #FFFFFF !important; text-decoration: none; border-bottom: 1px solid #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# زر التنبيه المكي - واضح وغير شفاف
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 8, 1])
with col2:
    adhan_on = st.toggle("🔔 أذان الحرم المكي (مفعل)", value=True, key="fixed_mecca_toggle")

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str = f"{h.day}/{h.month}/{h.year} هـ"
    mil_str = f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr_f = now.strftime("%H:%M:%S")
            for name, p_t in p_list:
