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

st.set_page_config(page_title="ساعة الصلاة - الحرم المكي", layout="centered")

# توقيت السعودية
sa_tz = pytz.timezone('Asia/Riyadh')

# تصميم الواجهة CSS للجوال مع التركيز على زر التنبيه المكي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }
    .main-container { text-align: center; color: white; width: 100%; padding-top: 10px; }
    .time-text { font-size: 16vw; font-weight: bold; display: inline-block; margin: 0; }
    .ampm-text { font-size: 6vw; color: #00FF00; vertical-align: super; margin-right: 2px; }
    .date-row { font-size: 5vw; color: #FFA500; font-weight: bold; margin-top: 5px; }
    
    /* مربع العداد */
    .prayer-card {
        background: rgba(0,255,0,0.1); padding: 15px; border-radius: 20px;
        border: 2px solid #00FF00; margin: 20px auto 15px auto; width: 90%; max-width: 350px;
    }
    .countdown { font-size: 10vw; color: #00FF00; font-weight: bold; font-family: 'Courier New', monospace; }
    
    /* تصميم زر التنبيه المكي الجديد */
    .stCheckbox {
        display: inline-block;
        background: rgba(0, 255, 0, 0.2);
        padding: 10px 20px;
        border-radius: 50px;
        border: 1px solid #00FF00;
        margin-top: 10px;
    }
    .stCheckbox label { color: #fff !important; font-weight: bold !important; font-size: 18px !important; }
    
    .footer { margin-top: 30px; opacity: 0.8; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# الرابط المباشر لأذان الحرم المكي
MECCA_ADHAN = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# طلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# عرض زر التنبيه في الواجهة الرئيسية بدلاً من القائمة الجانبية
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
enable_adhan = st.toggle("🔔 تنبيه بأذان الحرم المكي", value=True)
st.markdown("</div>", unsafe_allow_html=True)

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%
