import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد مكتبة الحسابات
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

# إعداد الصفحة لإزالة الشوائب تماماً
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- هندسة التصميم: إزالة الخطوط، رفع الساعة، توحيد الظلال ---
st.markdown("""
<style>
    /* حذف كل زوائد ستريمليت والخطوط البيضاء */
    header, footer, .stDeployButton, #MainMenu { visibility: hidden !important; height: 0; }
    div.block-container { padding: 0 !important; margin: 0 !important; }

    .stApp {
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: 100% 100%;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        direction: rtl;
    }

    .master-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100vh;
        width: 100vw;
        justify-content: flex-start;
        padding-top: 2vh; /* لرفع الساعة فوق القمر */
    }

    /* الستايل الموحد: أبيض بظل مائي شفاف */
    .glow-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.6); 
        font-family: 'Tajawal', sans-serif;
        line-height: 1.1;
        text-align: center;
    }

    /* الساعة */
    .clock-large { font-size: 16vw; font-weight: 900; }
    .ampm-small { font-size: 5vw; margin-right: 10px; }

    /* التاريخ */
    .date-small { font-size: 5vw; font-weight: 700; margin-top: -10px; }

    /* حاوية الأذان (المنتصف) */
    .adhan-mid {
        margin: 12vh 0 5vh 0;
        background: rgba(255, 255, 255, 0.1);
        padding: 8px 25px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* متبقي على الصلاة */
    .pray-label { font-size: 6vw; font-weight: 800; margin-top: 15px; }
    .pray-timer { font-size: 14vw; font-weight: 900; font-family: 'Courier New', monospace; }

    /* الروابط */
    .footer-box a {
        color: white !important; text-decoration: none; font-size: 14px;
        padding: 8px 15px; background: rgba(0,0,0,0.3); border-radius: 20px;
        margin: 5px; border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# استخدام Placeholder واحد فقط لتحديث الشاشة
ui_space = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Magh
