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

# إعداد الصفحة لملء الشاشة وإخفاء الزوائد
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

# توقيت السعودية
sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- هندسة التصميم: إزالة الشوائب وتثبيت العناصر فوق الخلفية ---
st.markdown("""
<style>
    /* حذف الخطوط البيضاء وأشرطة ستريمليت تماماً */
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

    /* الحاوية الرئيسية للهيكل الجديد */
    .master-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100vh;
        width: 100vw;
        text-align: center;
        justify-content: space-between;
        padding: 5vh 0;
    }

    /* ستايل النصوص الموحد (أبيض بظل مائي شفاف) */
    .text-glow {
        color: #FFFFFF !important;
        text-shadow: 0px 0px 15px rgba(0,0,0,0.7); 
        font-family: 'Tajawal', sans-serif;
        line-height: 1.1;
    }

    /* الساعة فوق القمر ومصغرة */
    .main-clock { font-size: 16vw; font-weight: 900; margin: 0; }
    .ampm-label { font-size: 5vw; margin-right: 8px; }

    /* التاريخ تحت الساعة مباشرة */
    .date-label { font-size: 5vw; font-weight: 700; margin-top: -1vh; }

    /* حاوية الأذان في المنتصف */
    .mid-section {
        margin: 5vh 0;
        background: rgba(255, 255, 255, 0.1);
        padding: 10px 30px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* متبقي على الصلاة في الأسفل وبنفس نمط الساعة */
    .bottom-label { font-size: 6vw; font-weight: 800; }
    .bottom-timer { font-size: 14vw; font-weight: 900; font-family: 'Courier New', monospace; }

    /* روابط التواصل */
    .social-box a {
        color: white !important; text-decoration: none; font-size: 14px;
        padding: 8px 15px; background: rgba(0,0,0,0.4); border-radius: 20px;
        margin: 5px; border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# الحصول على الإحداثيات
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# Placeholder واحد للمحتوى بالكامل لتجنب أخطاء Duplicate Key
content_space = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr_f = now.strftime("%H:%M:%S")
            for name, p_t in p_list:
                p_f = f"{p_t}:00"
                if p_f > curr_f:
                    next_p_name = name
                    target = sa_tz.localize(datetime.strptime(p_f, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    h_v, rem = divmod(diff.seconds, 3600); m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    break
                if curr_f == p_f: play_now = True
    except: pass

    with content_space.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')

        # الهيكل البرمجي الصافي بدون تداخل الـ HTML
        st.markdown(f"""
            <div class='master-container'>
                <div class='top-box'>
                    <div class='text-glow main-clock'>{raw_
