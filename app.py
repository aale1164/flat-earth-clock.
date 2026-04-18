import streamlit as st
import pytz
from datetime import datetime, date
import time
import requests
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# محاولة استيراد مكتبة أوقات الصلاة
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')

# --- وظيفة حساب الفصول ---
def get_season_countdown():
    today = date.today()
    seasons = [
        ('الصيف', date(today.year, 6, 21)),
        ('الخريف', date(today.year, 9, 23)),
        ('الشتاء', date(today.year, 12, 21)),
        ('الربيع', date(today.year + (1 if today > date(today.year, 3, 21) else 0), 3, 21))
    ]
    for name, s_date in sorted(seasons, key=lambda x: x[1]):
        if s_date > today:
            return name, (s_date - today).days
    return seasons[0] # افتراضي

# --- التصميم المتطور (Modern Glassmorphism) ---
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
        padding-top: 5vh;
    }

    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 12px rgba(0,0,0,0.8); 
        margin: 0;
        line-height: 1.1;
        text-align: center;
    }

    .time-val { font-size: 15vw; font-weight: 900; }
    .ampm-val { font-size: 4vw; margin-right: 10px; color: #FFA500; }

    .info-line { font-size: 4vw; font-weight: 700; margin-top: 5px; opacity: 0.9; }

    /* حاوية البيانات الفلكية والطقس */
    .astro-grid {
        display: flex;
        gap: 15px;
        margin-top: 20px;
        background: rgba(255, 255, 255, 0.1);
        padding: 10px 20px;
        border-radius: 20px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .astro-item { font-size: 3.5vw; font-weight: bold; color: #FFFFFF; }

    .footer-links { margin-top: auto; padding-bottom: 30px; display: flex; gap: 10px; }
    .footer-links a {
        color: white !important; text-decoration: none; font-size: 14px;
        padding: 8px 15px; background: rgba(0,0,0,0.4); border-radius: 15px;
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
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    # بيانات الصلاة والفلك
    next_p_name, time_left = "الفجر", "00:00:00"
    sunrise, sunset = "--:--", "--:--"
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            sunrise = times['Sunrise']
            sunset = times['Maghrib'] # الغروب هو وقت المغرب تقريباً
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr_f = now.strftime("%H:%M:%S")
            for name, p_t in p_list:
                if f"{p_t}:00" > curr_f:
                    next_p_name = name
                    target = sa_tz.localize(datetime.strptime(f"{p_t}:00", "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    h_v, rem = divmod(diff.seconds, 3600); m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    break
    except: pass

    season_name, days_to = get_season_countdown()

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')

        st.markdown(f"""
            <div class='main-layout'>
                <div class='unified-text time-val'>{raw_t}<span class='ampm-val'>{ampm}</span></div>
                <div class='unified-text info-line'>{hij_str} | {mil_str}</div>
                <div class='unified-text info-line' style='color:#00FF00;'>متبقي على {next_p_name}: {time_left}</div>

                <div class='astro-grid'>
                    <div class='astro-item'>☀️ الشروق: {sunrise}</div>
                    <div class='astro-item'>🌅 الغروب: {sunset}</div>
                </div>

                <div class='unified-text info-line' style='margin-top:20px; font-size:3.8vw;'>
                    🍂 متبقي على فصل {season_name}: {days_to} يوم
                </div>

                <div class='footer-links'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
