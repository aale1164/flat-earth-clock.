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

# --- تصميم ملكي: وضوح فائق وتنسيق متوازن ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }

    /* الصندوق الرئيسي لجعل كل شيء بارز */
    .glass-panel {
        background: rgba(0, 0, 0, 0.75);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 35px;
        padding: 25px;
        text-align: center;
        margin: 10px auto;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
    }

    .time-display { 
        font-size: 19vw; font-weight: 900; color: #FFFFFF; 
        line-height: 1; margin: 0; text-shadow: 0 0 20px rgba(0,255,0,0.2);
    }
    
    .ampm-label { font-size: 7vw; color: #00FF00; font-weight: bold; }

    .date-label { font-size: 5.5vw; color: #FFA500; font-weight: 700; margin: 15px 0; }

    /* كرت الصلاة المحدث: أبيض ناصع بحدود خضراء */
    .prayer-card {
        background: #FFFFFF; 
        padding: 20px; 
        border-radius: 25px;
        margin: 20px auto 10px auto; 
        width: 100%; 
        max-width: 380px;
        border-bottom: 8px solid #008800;
    }

    .p-name { font-size: 24px; color: #222; font-weight: bold; margin-bottom: 5px; }
    .p-time { font-size: 13vw; color: #008800; font-weight: 900; font-family: 'Courier New', monospace; }

    /* تنسيق زر التنبيه تحت المربع مباشرة */
    .stToggle {
        margin: 20px auto;
        padding: 10px;
        background: rgba(255,255,255,0.05);
        border-radius: 50px;
        border: 1px solid rgba(0,255,0,0.3);
    }

    .footer-links { margin-top: 30px; }
    .footer-links a { 
        color: white !important; 
        text-decoration: none; 
        padding: 8px 15px; 
        background: rgba(255,255,255,0.15); 
        border-radius: 12px;
        font-size: 14px;
        margin: 0 5px;
    }
</style>
""", unsafe_allow_html=True)

# الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_dt, mil_dt = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p, rem_t, adhan_trigger = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            plist = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr = now.strftime("%H:%M:%S")
            for name, ptime in plist:
                pt_full = f"{ptime}:00"
                if pt_full > curr:
                    next_p = name
                    target = sa_tz.localize(datetime.strptime(pt_full, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    hh, rr = divmod(diff.seconds, 3600); mm, ss = divmod(rr, 60)
                    rem_t = f"{hh:02d}:{mm:02d}:{ss:02d}"
                    break
                if curr == pt_full
