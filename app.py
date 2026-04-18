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

st.set_page_config(page_title="Clock", layout="centered")

sa_tz = pytz.timezone('Asia/Riyadh')
AD_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# تصميم شفاف وهادئ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }
    .glass {
        background: rgba(0, 0, 0, 0.4); 
        border-radius: 35px;
        padding: 20px;
        text-align: center;
        margin: 10px auto;
        backdrop-filter: blur(5px);
    }
    .t-txt { 
        font-size: 18vw; font-weight: 900; 
        color: rgba(255, 255, 255, 0.85); 
        line-height: 1; margin: 0; 
    }
    .p-card {
        background: #FFFFFF; padding: 20px; 
        border-radius: 25px; margin: 20px auto; 
        width: 100%; max-width: 380px;
        border-bottom: 8px solid #008800;
    }
    .p-time { 
        font-size: 12vw; color: #008800; 
        font-weight: 900; font-family: 'Courier New'; 
    }
</style>
""", unsafe_allow_html=True)

# الموقع
loc = get_geolocation()
lat, lon = 26.32, 43.97
if loc and 'coords' in loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    # أسطر قصيرة جداً لمنع الانقطاع
    h_str = f"{h.day}/{h.month}/{h.year} هـ"
    m_str = f"{now.day}/{now.month}/{now.year} م"
    
    p_name, t_rem, play = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(lat, lon, 'makkah', now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            plist = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr = now.strftime("%H:%M:%S")
            for name, pt in plist:
                target_s = f"{pt}:00"
                if target_s > curr:
                    p_name = name
                    fmt = "%H:%M:%S"
                    obj = datetime.strptime(target_s, fmt)
                    t_obj = sa_tz.localize(obj.replace(year=now.year, month=now.month, day=
