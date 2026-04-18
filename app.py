import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# محاولة استيراد المكتبة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")

# توقيت السعودية
sa_tz = pytz.timezone('Asia/Riyadh')

# تصميم الواجهة CSS المطور للالتصاق
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; background-attachment: fixed;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }}
    .time-display {{
        text-align: center; color: #fff; font-size: 85px; font-weight: bold;
        letter-spacing: -2px; line-height: 1; margin-bottom: 0;
    }}
    .ampm-style {{
        font-size: 35px; margin-right: -10px; color: #00FF00;
    }}
    .prayer-card {{
        text-align: center; background: rgba(0,255,0,0.1); padding: 15px;
        border-radius: 15px; border: 2px solid #00FF00; margin-top: 20px;
    }}
    .countdown {{ font-size: 45px; color: #00FF00; font-weight: bold; font-family: 'Courier New', monospace; }}
    .date-text {{ font-size: 24px; color: #FFA500; font-weight: bold; text-align: center; margin-top: 5px; }}
</style>
""", unsafe_allow_html=True)

# طلب الموقع الجغرافي
location = get_geolocation()
lat, lon = 26.32, 43.97  # القصيم افتراضياً
loc_label = "القصيم"

if location and 'coords' in location:
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    loc_label = "موقعك الحالي"

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    # تنسيق التاريخ أرقام
    hij_str = f"{h.day}/{h.month}/{h.year} هـ"
    mil_str = f"{now.day}/{now.month}/{now.year} م"
    
    # حساب الصلاة القادمة
    next_p_name = ""
    time_left = ""
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        
        p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
        curr_str = now.strftime("%H:%M:%S")
        
        for name, p_t in p_list:
            p_full = f"{p_t}:00"
            if p_full > curr_str:
                next_p_name = name
                target = sa_tz.localize(datetime.strptime(p_full, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                diff = target - now
                m, s = divmod(diff.seconds, 60)
                h_val, m = divmod(m, 60)
                time_left = f"{h_val:02d}:{m:02d}:{s:02d}"
                break
        if not next_p_name:
            next_p_name = "الفجر"; time_left = "صلاة الغد"
    except:
        time_left = "جاري الحساب..."

    with placeholder.container():
        # فصل الوقت عن AM/PM للتحكم في الالتصاق
        raw_time = now
