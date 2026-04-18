import streamlit as st
import pytz
from datetime import datetime, date
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# محاولة استيراد مكتبة أوقات الصلاة
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')

# --- وظيفة حساب الأيام المتبقية للفصول الفلكية ---
def get_season_countdown():
    today = date.today()
    year = today.year
    # المواعيد التقريبية لبداية الفصول
    seasons_dates = [
        ('الربيع', date(year, 3, 21)),
        ('الصيف', date(year, 6, 21)),
        ('الخريف', date(year, 9, 23)),
        ('الشتاء', date(year, 12, 21))
    ]
    
    # البحث عن الفصل القادم
    for name, s_date in seasons_dates:
        if s_date > today:
            return name, (s_date - today).days
            
    # إذا تجاوزنا 21 ديسمبر، الفصل القادم هو الربيع في العام التالي
    next_spring = date(year + 1, 3, 21)
    return 'الربيع', (next_spring - today).days

# --- التصميم: دمج الفلك والطقس بشكل أنيق ---
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

    .info-line { font-size: 4.2vw; font-weight: 700; margin-top: 5px; opacity: 0.9; }

    /* شبكة البيانات الفلكية (الشروق والغروب) */
    .astro-grid {
        display: flex;
        gap: 20px;
        margin-top: 25px;
        background: rgba(255, 255, 255, 0.1);
        padding: 12px 25px;
        border-radius: 50px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .astro-item { font-size: 3.5vw; font-weight: bold; color: #FFFFFF; }

    /* فوتر التواصل */
    .footer-links { 
        margin-top: auto; 
        padding-bottom: 30px; 
        display: flex; 
        gap: 15px; 
    }
    .footer-links a {
        color: white !important; 
        text-decoration: none; 
        font-size: 16px;
        padding: 10px 20px; 
        background: rgba(0,0,0,0.5); 
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.2);
        transition: 0.3s;
    }
    .footer-links a:hover { background: rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# جلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97 # افتراضي: القصيم
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    # حساب البيانات الفلكية
    sunrise, sunset, next_p_name, time_left = "--:--", "--:--", "الفجر", "00:00:00"
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            sunrise = times['Sunrise']
            sunset = times['Maghrib']
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

    # حساب الفصل
    season_name, days_rem = get_season_countdown()
    # أيقونة الفصل
    season_icon = "🌸" if season_name == "الربيع" else "☀️" if season_name == "الصيف" else "🍂" if season_name == "الخريف" else "❄️"

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')

        st.markdown(f"""
            <div class='main-layout'>
                <div class='unified-text time-val'>{raw_t}<span class='ampm-val'>{ampm}</span></div>
                <div class='unified-text info-line'>{hij_str} | {mil_str}</div>
                
                <div class='unified-text info-line' style='color:#00FF00; margin-top:10px;'>
                    متبقي على {next_p_name}: {time_left}
                </div>

                <div class='astro-grid'>
                    <div class='astro-item'>☀️ الشروق: {sunrise}</div>
                    <div class='astro-item'>🌅 الغروب: {sunset}</div>
                </div>

                <div class='unified-text info-line' style='margin-top:25px; font-size:4vw;'>
                    {season_icon} متبقي على فصل {season_name}: {days_rem} يوم
                </div>

                <div class='footer-links'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
