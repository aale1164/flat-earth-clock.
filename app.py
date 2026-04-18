import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

# إعداد الصفحة لإخفاء كافة العناصر الزائدة
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')

# --- التصميم: واجهة نقية مع إزاحة ذكية للأسفل ---
st.markdown("""
<style>
    header, footer, .stDeployButton, #MainMenu { visibility: hidden !important; height: 0; }
    .block-container { padding: 0 !important; }

    .stApp {
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: 100% 100%;
        background-attachment: fixed;
        direction: rtl;
        font-family: 'Tajawal', sans-serif;
    }

    .main-layout {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100vh;
        justify-content: flex-start;
        padding-top: 5vh; /* وضع الساعة فوق القمر */
    }

    /* ستايل النصوص الموحد */
    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.6); 
        margin: 0;
        line-height: 1.2;
        text-align: center;
    }

    /* الساعة */
    .time-display { font-size: 16vw; font-weight: 900; }
    .ampm-display { font-size: 5vw; margin-right: 10px; }

    /* التاريخ */
    .date-line { font-size: 4.8vw; font-weight: 700; margin-top: 5px; }

    /* متبقي على الصلاة: إزاحة إضافية للأسفل لتجنب الشمس */
    .prayer-line { 
        font-size: 4.8vw; 
        font-weight: 700; 
        margin-top: 45vh; /* إزاحة كبيرة لضمان النزول تحت منطقة الشمس */
    }

</style>
""", unsafe_allow_html=True)

# جلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97 
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left = "الفجر", "00:00:00"
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']),
