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
    PRAYER_LIB = True
except ImportError:
    PRAYER_LIB = False

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")
sa_tz = pytz.timezone('Asia/Riyadh')

# --- دوال جلب البيانات ---
@st.cache_data(ttl=600)
def fetch_weather_cached(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        resp = requests.get(url, timeout=5).json()
        return resp['current_weather']['temperature']
    except: return None

def get_season_data():
    today = date.today()
    y = today.year
    seasons = [
        ('الربيع', 'Spring', date(y, 3, 21), '🌸'),
        ('الصيف', 'Summer', date(y, 6, 21), '☀️'),
        ('الخريف', 'Autumn', date(y, 9, 23), '🍂'),
        ('الشتاء', 'Winter', date(y, 12, 21), '❄️')
    ]
    for ar, en, s_date, icon in seasons:
        if s_date > today: return ar, en, (s_date - today).days, icon
    return 'الربيع', 'Spring', (date(y + 1, 3, 21) - today).days, '🌸'

# --- التصميم CSS (تأكد من وجوده في بداية الكود) ---
st.markdown("""
<style>
    header, footer, .stDeployButton, #MainMenu { visibility: hidden !important; height: 0; }
    .block-container { padding: 0 !important; }
    .stApp {
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png") no-repeat center center fixed;
        background-size: cover;
        direction: rtl;
        font-family: 'Tajawal', sans-serif;
    }
    .main-layout { display: flex; flex-direction: column; align-items: center; height: 100vh; padding-top: 6vh; }
    .unified-text { color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); text-align: center; margin: 0; }
    .time-display { font-size: 15vw; font-weight: 900; }
    .ampm-display { font-size: 4vw; color: #FFA500; margin-right: 15px; }
    .info-line { font-size: 4.2vw; font-weight: 700; margin-top: 5px; }
    
    .data-bar {
        display: flex; gap: 30px; margin-top: 40px;
        background: rgba(0, 0, 0, 0.3); padding: 15px 40px;
        border-radius: 60px; backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .data-item { font-size: 3vw; font-weight: bold; color: white; text-align: center; }
    .data-label { font-size: 1.4vw; opacity: 0.8; display: block; }
    
    .season-section { margin-top: 40px; text-align: center; }
    .season-text { font-size: 4.5vw; font-weight: 800; color: white; }
    .season-sub { font-size: 2vw; opacity: 0.8; display: block; color: white; }
    
    .social-footer { margin-top: auto; padding-bottom: 40px; display: flex; gap: 20px; }
    .social-footer a {
        color: white !important; text-decoration: none; font-size: 18px; font-weight: bold;
        padding: 12px 30px; background: rgba(0,0,0,0.6); border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# الإحداثيات والموقع
lat, lon = 26.32, 43.97
loc = get_geolocation()
if loc and 'coords' in loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"

    # حساب أوقات الصلاة والطقس
    sunrise, sunset, p_name, p_left = "--:--", "--:--", "...", "00:00:00"
    if PRAYER_LIB:
        try:
            calc = PrayerTimesCalculator(lat, lon, 'makkah', now.strftime("%Y-%m-%d"))
            times = calc.fetch_prayer_times()
            sunrise, sunset = times['Sunrise'], times['Maghrib']
            # منطق حساب الصلاة القادمة (مبسط)
            prayers = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            for name, pt in prayers:
                if f"{pt}:00" > now.strftime("%H:%M:%S"):
                    p_name, p_left = name, pt # هنا يوضع حساب الفرق الزمني الفعلي
                    break
        except: pass

    temp = fetch_weather_cached(lat, lon)
    weather_str = f"{temp}" if temp else "--"
    s_ar, s_en, d_left, s_icon = get_season_data()

    with placeholder.container():
        # هذا هو الجزء الذي كان "لا يعمل" لديك، قمنا بوضعه داخل f-string
        st.markdown(f"""
            <div class='main-layout'>
                <div class='unified-text time-display'>
                    {now.strftime('%I:%M:%S').lstrip('0')}<span class='ampm-display'>{now.strftime('%p')}</span>
                </div>
                <div class='unified-text info-line'>{hij_str} | {mil_str}</div>
                
                <div class='data-bar'>
                    <div class='data-item'><span class='data-label'>TEMP</span>🌡️ {weather_str}°</div>
                    <div class='data-item'><span class='data-label'>SUNRISE</span>☀️ {sunrise}</div>
                    <div class='data-item'><span class='data-label'>SUNSET</span>🌅 {sunset}</div>
                </div>

                <div class='season-section unified-text'>
                    <div class='season-text'>{s_icon} متبقي على {s_ar}: {d_left} يوم</div>
                    <span class='season-sub'>{d_left} days left for {s_en}</span>
                </div>

                <div class='social-footer'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    time.sleep(1)
