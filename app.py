import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبة
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة - تصميم زجاجي", layout="centered")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- تصميم شفاف (Glassmorphism) لإلغاء "الفضيحة" ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.2)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }

    /* الحاوية الزجاجية الشفافة */
    .glass-box {
        text-align: center;
        background: rgba(255, 255, 255, 0.05); /* شفافية عالية جداً */
        backdrop-filter: blur(10px); /* تأثير التغبيش الزجاجي */
        -webkit-backdrop-filter: blur(10px);
        padding: 30px 10px;
        border-radius: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 10px auto;
    }

    .time-text { 
        font-size: 22vw; font-weight: 900; color: #FFFFFF; 
        text-shadow: 0 4px 15px rgba(0,0,0,1); /* ظل أسود قوي لإبراز الأبيض الشفاف */
        line-height: 0.9; margin: 0; 
    }
    
    .ampm-text { font-size: 8vw; color: #00FF00; font-weight: bold; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    
    .date-text { 
        font-size: 6vw; color: #FFA500; font-weight: 700; 
        margin: 15px 0; text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    }

    /* كرت الصلاة الشفاف */
    .prayer-card-glass {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px 10px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 20px auto;
        width: 100%;
        max-width: 380px;
    }

    .prayer-label { font-size: 24px; color: #FFFFFF; font-weight: 700; margin-bottom: 5px; opacity: 0.9; }
    
    .countdown { 
        font-size: 14vw; color: #00FF00; font-weight: 900; 
        font-family: 'Courier New', monospace; 
        text-shadow: 0 0 20px rgba(0,255,0,0.4); /* توهج أخضر خفيف */
    }

    /* الفوتر */
    .footer-btn {
        display: inline-block;
        padding: 8px 18px;
        background: rgba(0,0,0,0.3);
        border-radius: 15px;
        color: white !important;
        text-decoration: none;
        font-size: 14px;
        margin: 5px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 1. جلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# 2. زر التنبيه المكي الشفاف
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 10, 1])
with c2:
    adhan_on = st.toggle("🔔 أذان الحرم المكي الشريف", value=True, key="glass_mecca_toggle")

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%
