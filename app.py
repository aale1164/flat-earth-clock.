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

# --- دوال جلب البيانات (مع تخزين مؤقت) ---
@st.cache_data(ttl=600)
def fetch_weather_cached(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        resp = requests.get(url, timeout=5).json()
        return resp['current_weather']['temperature']
    except:
        return None

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
        if s_date > today:
            return ar, en, (s_date - today).days, icon
    next_spring = date(y + 1, 3, 21)
    return 'الربيع', 'Spring', (next_spring - today).days, '🌸'

# --- الحصول على الإحداثيات ---
lat, lon = 26.32, 43.97  # بريدة
try:
    loc = get_geolocation()
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
except:
    pass

# --- التصميم CSS (مع تحسينات للشفافية والتباعد) ---
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
        padding-top: 6vh;
    }

    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.7); 
        margin: 0;
        line-height: 1.2;
        text-align: center;
    }

    .time-display { font-size: 16vw; font-weight: 900; }
    .ampm-display { font-size: 5vw; margin-right: 10px; color: #FFD966; }

    .info-line { 
        font-size: 4.5vw; 
        font-weight: 700; 
        margin-top: 8px;
        opacity: 0.9;              /* شفافية خفيفة */
    }

    /* صندوق البيانات (طقس، شروق، غروب) - نزول إضافي */
    .data-bar {
        display: flex;
        gap: 25px;
        margin-top: 30px;           /* تمت زيادته لينزل أكثر */
        background: rgba(20, 20, 20, 0.25);
        padding: 12px 30px;
        border-radius: 60px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        opacity: 0.9;               /* شفافية الصندوق نفسه */
    }

    .data-item {
        font-size: 3.2vw;
        font-weight: bold;
        color: #FFFFFF;
        text-align: center;
        line-height: 1.4;
        opacity: 0.85;              /* شفافية الأرقام */
    }

    .data-label {
        font-size: 1.8vw;
        font-weight: normal;
        opacity: 0.7;
        display: block;
    }

    /* سطر الفصل - ينزل أكثر */
    .season-line {
        font-size: 4vw;
        font-weight: 700;
        margin-top: 35px;           /* زيادة المسافة عن الصندوق */
        opacity: 0.9;
    }

    .season-sub {
        font-size: 2.2vw;
        opacity: 0.7;
        font-weight: normal;
        display: block;
    }

    .social-footer { 
        margin-top: auto; 
        padding-bottom: 30px; 
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
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

placeholder = st.empty()

# --- حلقة التحديث ---
while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str = f"{h.day}/{h.month}/{h.year} هـ"
    mil_str = f"{now.day}/{now.month}/{now.year} م"

    # الصلاة القادمة
    next_p_name, time_left = "الفجر", "00:00:00"
    sunrise, sunset = "--:--", "--:--"
    if PRAYER_LIB:
        try:
            calc = PrayerTimesCalculator(lat, lon, 'makkah', now.strftime("%Y-%m-%d"))
            times = calc.fetch_prayer_times()
            if times:
                sunrise = times.get('Sunrise', '--:--')
                sunset = times.get('Maghrib', '--:--')
                prayers = [
                    ('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']),
                    ('العصر', times['Asr']), ('المغرب', times['Maghrib']),
                    ('العشاء', times['Isha'])
                ]
                curr = now.strftime("%H:%M:%S")
                for name, pt in prayers:
                    if f"{pt}:00" > curr:
                        next_p_name = name
                        target = sa_tz.localize(datetime.strptime(f"{pt}:00", "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                        diff = target - now
                        h_v, rem = divmod(diff.seconds, 3600)
                        m_v, s_v = divmod(rem, 60)
                        time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                        break
        except:
            pass

    # الطقس والفصل
    temp = fetch_weather_cached(lat, lon)
    weather_str = f"{temp}°C" if temp is not None else "--°C"
    season_ar, season_en, days_left, season_icon = get_season_data()

    # تنسيق الوقت
    raw_t = now.strftime('%I:%M:%S')
    if raw_t.startswith('0'):
        raw_t = raw_t[1:]
    ampm = now.strftime('%p')

    with placeholder.container():
        st.markdown(f"""
            <div class='main-layout'>
                <div class='unified-text time-display'>
                    {raw_t}<span class='ampm-display'>{ampm}</span>
                </div>
                <div class='unified-text info-line'>{hij_str} | {mil_str}</div>
                <div class='unified-text info-line' style='color:#B5FFB5;'>
                    متبقي على صلاة {next_p_name}: {time_left}
                </div>

                <!-- صندوق البيانات: طقس، شروق، غروب -->
                <div class='data-bar'>
                    <div class='data-item'>🌡️ {weather_str}<span class='data-label'>Temp</span></div>
                    <div class='data-item'>☀️ الشروق: {sunrise}<span class='data-label'>Sunrise</span></div>
                    <div class='data-item'>🌅 الغروب: {sunset}<span class='data-label'>Sunset</span></div>
                </div>

                <!-- سطر الفصل -->
                <div class='unified-text season-line'>
                    {season_icon} متبقي على {season_ar}: {days_left} يوم
                    <span class='season-sub'>{days_left} days left for {season_en}</span>
                </div>

                <div class='social-footer'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
