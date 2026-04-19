import streamlit as st
import pytz
from datetime import datetime, date, timedelta
import time
import requests
from hijri_converter import Gregorian

# --- إعداد الصفحة ---
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

# --- استيراد المكتبات الاختيارية ---
try:
    from prayer_times_calculator import PrayerTimesCalculator
    PRAYER_LIB_AVAILABLE = True
except ImportError:
    PRAYER_LIB_AVAILABLE = False

try:
    from streamlit_js_eval import get_geolocation
    GEO_LIB_AVAILABLE = True
except ImportError:
    GEO_LIB_AVAILABLE = False

# --- إعداد المنطقة الزمنية ---
sa_tz = pytz.timezone('Asia/Riyadh')

# --- دوال مساعدة ---
@st.cache_data(ttl=600) # تخزين الطقس لمدة 10 دقائق
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
    y = today.year
    seasons = [
        ('الربيع / Spring', date(y, 3, 21), "🌸"),
        ('الصيف / Summer', date(y, 6, 21), "☀️"),
        ('الخريف / Autumn', date(y, 9, 23), "🍂"),
        ('الشتاء / Winter', date(y, 12, 21), "❄️")
    ]
    for name, s_date, icon in seasons:
        if s_date > today:
            return name, (s_date - today).days, icon
    # بعد 21 ديسمبر -> ربيع العام القادم
    next_spring = date(y + 1, 3, 21)
    return "الربيع / Spring", (next_spring - today).days, "🌸"

# --- التنسيق البصري (CSS) ---
st.markdown("""
<style>
    /* إخفاء شريط الأدوات الافتراضي */
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

# --- إعدادات الموقع والطقس ---
# إحداثيات افتراضية (بريدة)
lat, lon = 26.32, 43.97

if GEO_LIB_AVAILABLE:
    try:
        location = get_geolocation()
        # التحقق من أن الموقع ليس None ويحتوي على الإحداثيات المتوقعة
        if location and location.get('coords'):
            lat = location['coords']['latitude']
            lon = location['coords']['longitude']
    except Exception:
        pass # في حال حدوث أي خطأ، نستمر بالإحداثيات الافتراضية

# --- حاوية العرض المتجددة ---
placeholder = st.empty()

# --- حلقة التحديث المستمر ---
while True:
    now = datetime.now(sa_tz)
    
    # --- التاريخ الهجري والميلادي ---
    try:
        h = Gregorian.fromdate(now.date()).to_hijri()
        hij_str = f"{h.day}/{h.month}/{h.year} هـ"
    except Exception:
        hij_str = "--/--/---- هـ"
        
    mil_str = f"{now.day}/{now.month}/{now.year} M"
    
    # --- الطقس (يُجلب من الدالة المخزنة مؤقتاً) ---
    weather_data = fetch_weather_cached(lat, lon)

    # --- أوقات الصلاة والصلاة القادمة ---
    # قيم افتراضية في حال عدم توفر المكتبة أو حدوث خطأ
    sunrise, sunset = "--:--", "--:--"
    next_p_ar, next_p_en, t_left = "الفجر", "Fajr", "00:00:00"
    
    if PRAYER_LIB_AVAILABLE:
        try:
            calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
            times = calc.fetch_prayer_times()
            if times:
                sunrise = times.get('Sunrise', "--:--")
                sunset = times.get('Maghrib', "--:--")
                
                # قائمة الصلوات مرتبة
                prayer_list = [
                    ('الفجر', 'Fajr', times.get('Fajr')), 
                    ('الظهر', 'Dhuhr', times.get('Dhuhr')), 
                    ('العصر', 'Asr', times.get('Asr')), 
                    ('المغرب', 'Maghrib', times.get('Maghrib')), 
                    ('العشاء', 'Isha', times.get('Isha'))
                ]
                
                curr_time_str = now.strftime("%H:%M")
                
                for ar_name, en_name, p_time in prayer_list:
                    if p_time and f"{p_time}" > curr_time_str:
                        next_p_ar = ar_name
                        next_p_en = en_name
                        target_dt = sa_tz.localize(datetime.strptime(f"{now.date()} {p_time}", "%Y-%m-%d %H:%M"))
                        diff = target_dt - now
                        h_v, rem = divmod(diff.seconds, 3600)
                        m_v, s_v = divmod(rem, 60)
                        t_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                        break
                else:
                    # إذا لم نجد صلاة قادمة اليوم، نعرض صلاة الفجر لليوم التالي
                    fajr_time_tomorrow = times.get('Fajr')
                    if fajr_time_tomorrow:
                        next_p_ar, next_p_en = "الفجر", "Fajr"
                        target_dt = sa_tz.localize(datetime.strptime(f"{now.date() + timedelta(days=1)} {fajr_time_tomorrow}", "%Y-%m-%d %H:%M"))
                        diff = target_dt - now
                        h_v, rem = divmod(diff.seconds, 3600)
                        m_v, s_v = divmod(rem, 60)
                        t_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
        except Exception:
            pass # في حال حدوث خطأ، نعرض القيم الافتراضية

    # --- حساب الفصل الحالي ---
    season_name, season_days, season_icon = get_season_data()

    # --- تحديث الواجهة ---
    with placeholder.container():
        raw_time = now.strftime('%I:%M:%S').lstrip('0') or "12"
        ampm_ar = "م" if now.strftime('%p') == "PM" else "ص"
        ampm_en = now.strftime('%p')

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
                    {season_icon} متبقي على {season_name.split(' / ')[0]}: {season_days} يوم
                    <span class='eng-sub'>{season_days} days left for {season_name.split(' / ')[1]}</span>
                </div>

                <div class='social-links'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)

    time.sleep(1)
