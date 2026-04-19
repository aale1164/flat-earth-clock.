import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد مكتبة أوقات الصلاة
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

# إعداد الصفحة لإخفاء العناصر الافتراضية لـ Streamlit
st.set_page_config(page_title="ساعة الصلاة الاحترافية - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')

# --- دمج التنسيق الجديد داخل التطبيق ---
st.markdown("""
<style>
    /* إخفاء واجهة Streamlit */
    header, footer, .stDeployButton, #MainMenu { visibility: hidden !important; height: 0; }
    .block-container { padding: 0 !important; }

    * {
        box-sizing: border-box;
    }
    
    body, .stApp {
        margin: 0;
        padding: 0;
        font-family: 'Tajawal', sans-serif;
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png") no-repeat center center fixed;
        background-size: cover;
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        color: white;
        overflow: hidden;
    }

    .container {
        width: 100%;
        max-width: 1200px;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding: 5vh 20px 0 20px;
        z-index: 10;
    }

    .unified-text {
        text-shadow: 2px 2px 15px rgba(0,0,0,0.9);
        text-align: center;
        margin: 0;
    }

    .time-val {
        font-size: 15vw;
        font-weight: 900;
        line-height: 1;
    }

    /* ميديا كويري للشاشات المتوسطة والكبيرة */
    @media (min-width: 768px) {
        .time-val { font-size: 10vw; }
        .info-line { font-size: 3.5vw; }
        .eng-sub { font-size: 1.8vw; }
        .data-item { font-size: 2.5vw; }
        .small-label { font-size: 1.2vw; }
        .social-links a { font-size: 1.2vw; padding: 10px 25px; }
    }
    
    @media (min-width: 1200px) {
        .time-val { font-size: 8vw; }
        .info-line { font-size: 2.8vw; }
    }

    .ampm-val {
        font-size: 4vw;
        color: #FFA500;
        margin-right: 15px;
    }

    .info-line {
        font-size: 4.5vw;
        font-weight: 700;
        margin-top: 10px;
    }

    .eng-sub {
        font-size: 2.2vw;
        opacity: 0.85;
        font-weight: 400;
        display: block;
    }

    /* شريط البيانات السفلي (الشروق والغروب ودرجة الحرارة) */
    .data-bar {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 20px 30px;
        margin-top: 25px;
        background: rgba(255, 255, 255, 0.12);
        padding: 15px 35px;
        border-radius: 60px;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 90%;
    }

    .data-item {
        font-size: 3vw;
        font-weight: bold;
        text-align: center;
        line-height: 1.3;
        min-width: 100px;
    }

    .small-label {
        font-size: 1.5vw;
        font-weight: normal;
        opacity: 0.9;
        display: block;
    }

    /* روابط التواصل الاجتماعي */
    .social-links {
        margin-top: auto;
        padding-bottom: 5vh;
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        justify-content: center;
    }

    .social-links a {
        color: white;
        text-decoration: none;
        font-size: 1.5vw;
        padding: 12px 30px;
        background: rgba(0,0,0,0.6);
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }

    .social-links a:hover {
        background: rgba(255, 165, 0, 0.7);
        border-color: #FFA500;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# الحصول على الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97  # افتراضي
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

placeholder = st.empty()

# دالة لحساب المتبقي على الصيف
def get_summer_days():
    now = datetime.now(sa_tz)
    summer = datetime(now.year, 6, 21, tzinfo=sa_tz)
    if now > summer: summer = datetime(now.year+1, 6, 21, tzinfo=sa_tz)
    return (summer - now).days

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    # جلب أوقات الصلاة
    p_name, p_left, sunrise, sunset = "...", "00:00:00", "--:--", "--:--"
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
        ampm = "AM" if now.strftime('%p') == "AM" else "PM"
        
        # عرض الواجهة بناءً على التنسيق المطلوب
        st.markdown(f"""
        <div class="container">
            <div class="unified-text time-val">
                {raw_t}<span class="ampm-val">{ampm}</span>
            </div>
            
            <div class="unified-text info-line">
                {h.day}/{h.month}/{h.year} هـ | {now.day}/{now.month}/{now.year} م
                <span class="eng-sub">Remaining for {p_name}: {p_left}</span>
            </div>

            <div class="data-bar">
                <div class="data-item">
                    <span class="small-label">TEMP</span>25.5°C
                </div>
                <div class="data-item">
                    <span class="small-label">SUNRISE</span>{sunrise}
                </div>
                <div class="data-item">
                    <span class="small-label">SUNSET</span>{sunset}
                </div>
                <div class="data-item">
                    <span class="small-label">SUMMER</span>{get_summer_days()} Days
                </div>
            </div>

            <div class="social-links">
                <a href="https://twitter.com/aale1164" target="_blank">𝕏 @aale1164</a>
                <a href="https://www.snapchat.com/add/aale112" target="_blank">👻 aale112</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
