import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# محاولة استيراد مكتبة أوقات الصلاة
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    st.error("يرجى تثبيت مكتبة prayer-times-calculator")

# إعدادات الصفحة
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')

# --- التصميم: تنظيف شامل للمنبه وتنسيق العناصر ---
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
        padding-top: 8vh;
    }

    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.7); 
        margin: 0;
        line-height: 1.2;
        text-align: center;
    }

    .time-display { font-size: 16vw; font-weight: 900; }
    .ampm-display { font-size: 5vw; margin-right: 10px; color: #00FF00 !important; } /* لون AM/PM مميز */

    .info-line { font-size: 4.8vw; font-weight: 700; margin-top: 5px; }

    .social-footer { 
        margin-top: auto; 
        padding-bottom: 40px; 
        display: flex;
        gap: 20px;
    }
    .social-footer a {
        color: white !important; 
        text-decoration: none; 
        font-size: 16px; 
        font-weight: bold;
        padding: 12px 24px; 
        background: rgba(0,0,0,0.5); 
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# جلب الإحداثيات
location = get_geolocation()
# إحداثيات افتراضية (بريدة) في حال فشل الجلب
lat, lon = 26.32, 43.97 
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# استخدام placeholder واحد للتحديث لمنع تكرار العناصر
placeholder = st.empty()

while True:
    try:
        now = datetime.now(sa_tz)
        h = Gregorian(now.year, now.month, now.day).to_hijri()
        hij_str = f"{h.day}/{h.month}/{h.year} هـ"
        mil_str = f"{now.day}/{now.month}/{now.year} م"
        
        next_p_name, time_left = "الفجر", "00:00:00"
        
        # حساب أوقات الصلاة
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        
        if times:
            p_list = [
                ('الفجر', times['Fajr']), 
                ('الظهر', times['Dhuhr']), 
                ('العصر', times['Asr']), 
                ('المغرب', times['Maghrib']), 
                ('العشاء', times['Isha'])
            ]
            
            curr_f = now.strftime("%H:%M:%S")
            found = False
            for name, p_t in p_list:
                p_f = f"{p_t}:00"
                if p_f > curr_f:
                    next_p_name = name
                    target = sa_tz.localize(datetime.strptime(p_f, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    h_v, rem = divmod(diff.seconds, 3600)
                    m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    found = True
                    break
            
            # إذا مرت كل صلوات اليوم، الهدف هو فجر الغد
            if not found:
                time_left = "00:00:00" # يمكن تحسينها لحساب فجر اليوم التالي

        with placeholder.container():
            raw_t = now.strftime('%I:%M:%S')
            if raw_t.startswith('0'): raw_t = raw_t[1:]
            ampm = now.strftime('%p')

            st.markdown(f"""
                <div class='main-layout'>
                    <div class='unified-text time-display'>{raw_t}<span class='ampm-display'>{ampm}</span></div>
                    <div class='unified-text info-line'>{hij_str} | {mil_str}</div>
                    <div class='unified-text info-line'>متبقي على صلاة {next_p_name}: {time_left}</div>

                    <div class='social-footer'>
                        <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                        <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
