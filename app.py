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

# --- تصميم ملكي: شفافية للساعة ووضوح تام ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; background-attachment: fixed;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }

    .glass-panel {
        background: rgba(0, 0, 0, 0.45); /* زيادة الشفافية للخلفية */
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 35px;
        padding: 25px;
        text-align: center;
        margin: 10px auto;
        backdrop-filter: blur(5px); /* تأثير زجاجي ناعم */
    }

    .time-display { 
        font-size: 19vw; font-weight: 900; 
        color: rgba(255, 255, 255, 0.85); /* ساعة شفافة وأنيقة */
        line-height: 1; margin: 0; 
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    
    .ampm-label { font-size: 7vw; color: #00FF00; font-weight: bold; }
    .date-label { font-size: 5.5vw; color: #FFA500; font-weight: 700; margin: 15px 0; }

    .prayer-card {
        background: #FFFFFF; 
        padding: 20px; 
        border-radius: 25px;
        margin: 20px auto 10px auto; 
        width: 100%; max-width: 380px;
        border-bottom: 8px solid #008800;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }

    .p-name { font-size: 24px; color: #222; font-weight: bold; margin-bottom: 5px; }
    .p-time { font-size: 13vw; color: #008800; font-weight: 900; font-family: 'Courier New', monospace; }

    .footer-links { margin-top: 30px; text-align:center; }
    .footer-links a { 
        color: white !important; text-decoration: none; 
        padding: 8px 15px; background: rgba(255,255,255,0.1); 
        border-radius: 12px; font-size: 14px; margin: 0 5px;
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
    
    # إصلاح الأسطر المنقطعة
    hij_dt = f"{h.day}/{h.month}/{h.year} هـ"
    mil_dt = f"{now
