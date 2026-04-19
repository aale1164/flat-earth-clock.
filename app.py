import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبة الخاصة بأوقات الصلاة
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')

# --- التنسيق الجديد: توزيع العناصر لتجنب تغطية الشمس ---
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
        justify-content: space-between; /* توزيع المحتوى بين الأعلى والأسفل */
        padding: 5vh 0;
    }

    /* القسم العلوي: الساعة والتاريخ والمصلى */
    .top-section {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8); 
        margin: 0;
        text-align: center;
    }

    .time-main { font-size: 16vw; font-weight: 900; line-height: 1; }
    .ampm-mini { font-size: 5vw; margin-right: 10px; }
    .info-line { font-size: 4.5vw; font-weight: 700; margin-top: 10px; }
    .prayer-timer { color: #00FF00 !important; font-size: 4.5vw; font-weight: bold; margin-top: 5px; }

    /* القسم السفلي: المعلومات الإضافية (الشروق، الغروب، الصيف) */
    .bottom-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        padding-bottom: 20px;
    }

    .info-box {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        padding: 10px 30px;
        display: flex;
        gap: 20px;
        font-size: 3.5vw;
        font-weight: bold;
        margin-bottom: 15px;
    }

    .summer-timer {
        font-size: 4vw;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .social-footer { display: flex; gap: 15px; }
    .social-footer a {
        color: white !important; text-decoration: none; font-size: 14px;
        padding: 8px 18px; background: rgba(0,0,0,0.4); border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# جلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

placeholder = st.empty()

# حساب متبقي على الصيف (مثال: 21 يونيو)
def get_summer_countdown():
    now = datetime.now(sa_tz)
    summer_start = datetime(now.year, 6, 21, tzinfo=sa_tz)
    if now > summer_start:
        summer_start = datetime(now.year + 1, 6, 21, tzinfo=sa_tz)
    return (summer_start - now).days

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    # حساب أوقات الصلاة
    p_name, p_left, sunrise, sunset = "الفجر", "00:00:00", "05:37", "18:30"
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        sunrise, sunset = times['Sunrise'], times['Maghrib']
        p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
        curr_f = now.strftime("%H:%M:%S")
        for name, p_t in p_list:
            if f"{p_t}:00" > curr_f:
                p_name = name
                target = sa_tz.localize(datetime.strptime(f"{p_t}:00", "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                diff = target - now
                p_left = str(diff).split('.')[0].zfill(8)
                break
    except: pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = "ص" if now.strftime('%p') == "AM" else "م"

        st.markdown(f"""
            <div class='main-layout'>
                <div class='top-section'>
                    <div class='unified-text time-main'>{raw_t} <span class='ampm-mini'>{ampm}</span></div>
                    <div class='unified-text info-line'>{hij_str} | {mil_str}</div>
                    <div class='unified-text prayer-timer'>متبقي على صلاة {p_name}: {p_left}</div>
                </div>

                <div class='bottom-section'>
                    <div class='unified-text info-box'>
                        <span>🌡️ 25.5°C</span>
                        <span>☀️ الشروق: {sunrise}</span>
                        <span>🌅 الغروب: {sunset}</span>
                    </div>
                    <div class='unified-text summer-timer'>☀️ متبقي على الصيف: {get_summer_countdown()} يوم</div>
                    
                    <div class='social-footer'>
                        <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                        <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
