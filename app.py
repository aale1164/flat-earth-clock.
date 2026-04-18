import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد مكتبة أوقات الصلاة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

# إعداد الصفحة لإخفاء كل العيوب والخطوط البيضاء
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- هندسة التصميم والواجهة ---
st.markdown("""
<style>
    /* 1. تنظيف الواجهة وإخفاء الخطوط البيضاء */
    header, footer, .stDeployButton, #MainMenu { visibility: hidden !important; height: 0; position: fixed; }
    div.block-container { padding: 0 !important; margin: 0 !important; }

    .stApp {
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: 100% 100%;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        direction: rtl;
    }

    /* حاوية المحتوى الرئيسية */
    .app-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100vh;
        width: 100vw;
        justify-content: flex-start;
        padding-top: 3vh; /* لرفع الساعة فوق القمر */
        text-align: center;
    }

    /* ستايل النصوص: أبيض مع ظل شفاف ناعم */
    .water-glow {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 12px rgba(0,0,0,0.5); 
        font-family: 'Tajawal', sans-serif;
        line-height: 1.1;
        margin: 0;
    }

    /* الساعة والتاريخ (الجزء العلوي) */
    .main-time { font-size: 16vw; font-weight: 900; }
    .main-ampm { font-size: 5vw; margin-right: 8px; }
    .sub-date { font-size: 5vw; font-weight: 700; margin-top: -5px; }

    /* المنبه (الجزء الأوسط) */
    .adhan-badge {
        margin: 10vh 0 5vh 0;
        background: rgba(255, 255, 255, 0.1);
        padding: 8px 25px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        font-weight: bold;
        font-size: 18px;
    }

    /* عداد الصلاة (الجزء السفلي) */
    .pray-name { font-size: 6.5vw; font-weight: 800; margin-top: 20px; }
    .pray-timer { font-size: 15vw; font-weight: 900; font-family: 'Courier New', monospace; }

    /* روابط التواصل */
    .social-links { margin-top: auto; padding-bottom: 25px; }
    .social-links a {
        color: white !important; text-decoration: none; font-size: 14px;
        padding: 8px 18px; background: rgba(0,0,0,0.3); border-radius: 20px;
        margin: 5px; border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# الحصول على الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# مكان تحديث البيانات
placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            # تم التأكد من كتابة القائمة كاملة لإغلاق الأقواس والاقتباسات
            p_list = [
                ('الفجر', times['Fajr']), 
                ('الظهر', times['Dhuhr']), 
                ('العصر', times['Asr']), 
                ('المغرب', times['Maghrib']), 
                ('العشاء', times['Isha'])
            ]
            curr_f = now.strftime("%H:%M:%S")
            for name, p_t in p_list:
                p_f = f"{p_t}:00"
                if p_f > curr_f:
                    next_p_name = name
                    target = sa_tz.localize(datetime.strptime(p_f, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    h_v, rem = divmod(diff.seconds, 3600)
                    m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    break
                if curr_f == p_f: play_now = True
    except: pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
