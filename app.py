import streamlit as st
import pytz
from datetime import datetime, date, timedelta
import time
import requests
from hijri_converter import Gregorian

# إعداد الصفحة (يجب أن يكون في بداية الكود دائماً)
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

# محاولة استيراد مكتبة أوقات الصلاة بشكل آمن
try:
    from prayer_times_calculator import PrayerTimesCalculator
    PRAYER_LIB_AVAILABLE = True
except ImportError:
    PRAYER_LIB_AVAILABLE = False

# محاولة استيراد مكتبة الموقع الجغرافي بشكل آمن
try:
    from streamlit_js_eval import get_geolocation
    GEO_LIB_AVAILABLE = True
except ImportError:
    GEO_LIB_AVAILABLE = False

# إعداد المنطقة الزمنية
sa_tz = pytz.timezone('Asia/Riyadh')

# --- دوال مساعدة ---
@st.cache_data(ttl=600)
def fetch_weather_cached(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        temp = response['current_weather']['temperature']
        return f"{temp}°C"
    except Exception:
        return "--°C"

def get_season_data():
    today = date.today()
    year = today.year
    seasons = [
        ('الربيع', 'Spring', date(year, 3, 21), "🌸"),
        ('الصيف', 'Summer', date(year, 6, 21), "☀️"),
        ('الخريف', 'Autumn', date(year, 9, 23), "🍂"),
        ('الشتاء', 'Winter', date(year, 12, 21), "❄️")
    ]
    for name_ar, name_en, s_date, icon in seasons:
        if s_date > today:
            return name_ar, name_en, (s_date - today).days, icon
    
    next_spring = date(year + 1, 3, 21)
    return 'الربيع', 'Spring', (next_spring - today).days, "🌸"

def get_prayer_times(lat, lon, now):
    sunrise = sunset = "--:--"
    next_p_ar, next_p_en, t_left = "الفجر", "Fajr", "00:00:00"
    
    if PRAYER_LIB_AVAILABLE:
        try:
            calc = PrayerTimesCalculator(
                latitude=lat,
                longitude=lon,
                calculation_method='makkah',
                date=now.strftime("%Y-%m-%d")
            )
            times = calc.fetch_prayer_times()
            if times:
                sunrise = times.get('Sunrise', "--:--")
                sunset = times.get('Maghrib', "--:--")
                
                prayer_list = [
                    ('الفجر', 'Fajr', times.get('Fajr')),
                    ('الظهر', 'Dhuhr', times.get('Dhuhr')),
                    ('العصر', 'Asr', times.get('Asr')),
                    ('المغرب', 'Maghrib', times.get('Maghrib')),
                    ('العشاء', 'Isha', times.get('Isha'))
                ]
                
                curr_time_str = now.strftime("%H:%M")
                next_day = now.date() + timedelta(days=1)
                
                for ar_name, en_name, p_time in prayer_list:
                    if p_time and p_time > curr_time_str:
                        next_p_ar = ar_name
                        next_p_en = en_name
                        prayer_dt = datetime.strptime(f"{now.date()} {p_time}", "%Y-%m-%d %H:%M")
                        prayer_dt = sa_tz.localize(prayer_dt)
                        diff = prayer_dt - now
                        h, rem = divmod(diff.seconds, 3600)
                        m, s = divmod(rem, 60)
                        t_left = f"{h:02d}:{m:02d}:{s:02d}"
                        break
                else:
                    # إذا لم نجد صلاة قادمة اليوم، نعرض صلاة الفجر لليوم التالي
                    fajr_time = times.get('Fajr')
                    if fajr_time:
                        prayer_dt = datetime.strptime(f"{next_day} {fajr_time}", "%Y-%m-%d %H:%M")
                        prayer_dt = sa_tz.localize(prayer_dt)
                        diff = prayer_dt - now
                        h, rem = divmod(diff.seconds, 3600)
                        m, s = divmod(rem, 60)
                        t_left = f"{h:02d}:{m:02d}:{s:02d}"
        except Exception:
            pass
    
    return sunrise, sunset, next_p_ar, next_p_en, t_left

# --- التنسيق البصري (CSS) ---
st.markdown("""
<style>
    header, footer, .stDeployButton, #MainMenu { visibility: hidden !important; height: 0; }
    .block-container { padding: 0 !important; }

    .stApp {
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover;
        background-position: center;
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
        padding-top: 4vh;
    }

    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8); 
        margin: 0;
        line-height: 1.2;
        text-align: center;
    }

    .time-val { font-size: 14vw; font-weight: 900; }
    .ampm-val { font-size: 4vw; margin-right: 10px; color: #FFA500; }
    .info-line { font-size: 4vw; font-weight: 700; margin-top: 5px; }
    .eng-sub { font-size: 2vw; opacity: 0.8; font-weight: normal; display: block; }

    .data-bar {
        display: flex;
        gap: 20px;
        margin-top: 20px;
        background: rgba(255, 255, 255, 0.1);
        padding: 10px 25px;
        border-radius: 50px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .data-item { font-size: 2.5vw; font-weight: bold; color: #FFFFFF; text-align: center; line-height: 1.4; }

    .social-links { 
        margin-top: auto; 
        padding-bottom: 40px; 
        display: flex; 
        gap: 15px; 
    }
    .social-links a {
        color: white !important; 
        text-decoration: none; 
        font-size: 16px;
        padding: 10px 25px; 
        background: rgba(0,0,0,0.5); 
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.2);
        transition: 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# --- الحصول على الإحداثيات ---
if 'location_initialized' not in st.session_state:
    st.session_state.location_initialized = False
    st.session_state.lat = 26.32  # بريدة
    st.session_state.lon = 43.97

if not st.session_state.location_initialized and GEO_LIB_AVAILABLE:
    try:
        location = get_geolocation()
        if location and 'coords' in location:
            st.session_state.lat = location['coords']['latitude']
            st.session_state.lon = location['coords']['longitude']
        st.session_state.location_initialized = True
    except Exception:
        st.session_state.location_initialized = True

lat = st.session_state.lat
lon = st.session_state.lon

# --- الحصول على البيانات الحالية ---
now = datetime.now(sa_tz)

# التاريخ الهجري والميلادي
try:
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str = f"{h.day}/{h.month}/{h.year} هـ"
except Exception:
    hij_str = "--/--/---- هـ"
mil_str = f"{now.day}/{now.month}/{now.year} M"

# الطقس
weather_data = fetch_weather_cached(lat, lon)

# أوقات الصلاة
sunrise, sunset, next_p_ar, next_p_en, t_left = get_prayer_times(lat, lon, now)

# الفصل
season_ar, season_en, days_left, season_icon = get_season_data()

# تنسيق الوقت
hour_12 = now.strftime('%I').lstrip('0') or "12"
min_sec = now.strftime(':%M:%S')
raw_time = f"{hour_12}{min_sec}"
ampm_ar = "م" if now.hour >= 12 else "ص"
ampm_en = now.strftime('%p')

# --- عرض الواجهة ---
placeholder = st.empty()

with placeholder.container():
    html_content = f"""
        <div class='main-layout'>
            <div class='unified-text time-val'>
                {raw_time}<span class='ampm-val'>{ampm_ar} / {ampm_en}</span>
            </div>
            
            <div class='unified-text info-line'>
                {hij_str} | {mil_str}
            </div>
            
            <div class='unified-text info-line' style='color:#00FF00; margin-top:10px;'>
                متبقي على {next_p_ar}: {t_left}
                <span class='eng-sub'>Time to {next_p_en}: {t_left}</span>
            </div>

            <div class='data-bar'>
                <div class='data-item'>🌡️ {weather_data}<br><span style='font-size:1.5vw; font-weight:normal;'>Temp</span></div>
                <div class='data-item'>☀️ الشروق: {sunrise}<br><span style='font-size:1.5vw; font-weight:normal;'>Sunrise</span></div>
                <div class='data-item'>🌅 الغروب: {sunset}<br><span style='font-size:1.5vw; font-weight:normal;'>Sunset</span></div>
            </div>

            <div class='unified-text info-line' style='margin-top:25px;'>
                {season_icon} متبقي على {season_ar}: {days_left} يوم
                <span class='eng-sub'>{days_left} days left for {season_en}</span>
            </div>

            <div class='social-links'>
                <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
            </div>
        </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# --- تحديث تلقائي كل 60 ثانية ---
time.sleep(60)
st.rerun()
