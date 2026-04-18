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

# إعداد الصفحة لملء الشاشة
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- التصميم النهائي: إزالة الخطوط، ملء الشاشة، نصوص عائمة ثابتة ---
st.markdown("""
<style>
    /* 1. حذف الخط الأبيض العلوي وكل زوائد المنصة تماماً */
    header, footer, .stDeployButton, #MainMenu {
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 2. جعل التطبيق يملأ الشاشة بالكامل بدون هوامش */
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }

    .stApp {
        background: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.1)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: 100% 100%; /* جعل الخلفية بنفس حجم الواجهة بالضبط */
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        direction: rtl; 
        font-family: 'Tajawal', sans-serif;
    }

    /* 3. تثبيت المحتوى في منتصف الشاشة كلياً */
    .main-wrapper {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh; /* ملء ارتفاع الشاشة */
        text-align: center;
    }

    /* 4. تنسيق الساعة (ثابتة وعائمة) */
    .time-val { 
        font-size: 25vw; 
        font-weight: 900; 
        color: #FFFFFF; 
        line-height: 0.8; 
        text-shadow: 0px 0px 30px rgba(0,0,0,1); /* ظل عميق للوضوح */
        margin: 0;
    }
    .ampm-val { font-size: 8vw; color: #00FF00; font-weight: bold; }

    .date-val { 
        font-size: 7vw; 
        color: #FFA500; 
        font-weight: 800; 
        margin: 15px 0;
        text-shadow: 0px 0px 15px rgba(0,0,0,1);
    }

    .prayer-title { 
        font-size: 28px; color: #FFFFFF; font-weight: 900; 
        text-shadow: 0px 0px 10px rgba(0,0,0,1);
        margin-top: 20px;
    }
    .prayer-timer-val { 
        font-size: 18vw; color: #00FF00; font-weight: 900; 
        font-family: 'Courier New', monospace;
        text-shadow: 0px 0px 20px rgba(0,0,0,1);
    }

    /* روابط التواصل */
    .footer-links { margin-top: 30px; }
    .footer-links a { 
        color: white !important; text-decoration: none; font-weight: bold; 
        padding: 10px 20px; background: rgba(0,0,0,0.4); border-radius: 20px;
        margin: 5px; border: 1px solid rgba(255,255,255,0.2);
    }

    /* تنسيق زر التبديل ليكون شفافاً */
    .stToggle { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# زر الأذان (مخفي بذكاء)
st.markdown("<div style='position: fixed; top: 10px; right: 10px; z-index: 1000;'>", unsafe_allow_html=True)
adhan_on = st.toggle("🔔 أذان", value=True, key="ultimate_toggle")
st.markdown("</div>", unsafe_allow_html=True)

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

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')

        st.markdown(f"""
            <div class='main-wrapper'>
                <div class='time-val'>{raw_t}<span class='ampm-val'>{ampm}</span></div>
                <div class='date-val'>{hij_str} | {mil_str}</div>
                <div class='prayer-title'>متبقي على صلاة {next_p_name}</div>
                <div class='prayer-timer-val'>{time_left}</div>
                <div class='footer-links'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if play_now and adhan_on:
            st.markdown(f'<audio src="{ADHAN_URL}" autoplay></audio>', unsafe_allow_html=True)

    time.sleep(1)
