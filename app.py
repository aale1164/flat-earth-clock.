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

# تصميم الواجهة CSS - ثابت ومضمون
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
        direction: rtl; 
        font-family: 'Tajawal', sans-serif;
    }}
    
    .main-container {{
        text-align: center;
        color: white;
        padding-top: 20px;
    }}

    .time-text {{
        font-size: 75px;
        font-weight: bold;
        display: inline-block;
        margin: 0;
        padding: 0;
    }}

    .ampm-text {{
        font-size: 25px;
        color: #00FF00;
        vertical-align: super;
        margin-right: 5px;
    }}

    .date-row {{
        font-size: 22px;
        color: #FFA500;
        font-weight: bold;
        margin-top: 10px;
    }}

    .prayer-card {{
        background: rgba(0,255,0,0.1);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #00FF00;
        margin: 25px auto;
        max-width: 400px;
    }}

    .countdown {{
        font-size: 45px;
        color: #00FF00;
        font-weight: bold;
        font-family: 'Courier New', monospace;
    }}

    .footer {{
        margin-top: 40px;
        opacity: 0.7;
        font-size: 18px;
    }}
</style>
""", unsafe_allow_html=True)

# طلب الموقع الجغرافي
location = get_geolocation()
lat, lon = 26.32, 43.97 # القصيم افتراضياً
loc_label = "القصيم"

if location and 'coords' in location:
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    loc_label = "موقعك الحالي"

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    # التاريخ
    hij_str = f"{h.day}/{h.month}/{h.year} هـ"
    mil_str = f"{now.day}/{now.month}/{now.year} م"
    
    # حساب الصلاة
    next_p_name = ""
    time_left = "جاري الحساب..."
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr_str = now.strftime("%H:%M:%S")
            found = False
            for name, p_t in p_list:
                if f"{p_t}:00" > curr_str:
                    next_p_name = name
                    target = sa_tz.localize(datetime.strptime(f"{p_t}:00", "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    m, s = divmod(diff.seconds, 60)
                    h_val, m = divmod(m, 60)
                    time_left = f"{h_val:02d}:{m:02d}:{s:02d}"
                    found = True
                    break
            if not found:
                next_p_name = "الفجر"; time_left = "صلاة الغد"
    except:
        pass

    with placeholder.container():
        # عرض الوقت
        raw_time = now.strftime('%I:%M:%S')
        if raw_time.startswith('0'): raw_time = raw_time[1:]
        ampm = now.strftime('%p')
        
        st.markdown(f"""
            <div class='main-container'>
                <div>
                    <span class='time-text'>{raw_time}</span>
                    <span class='ampm-text'>{ampm}</span>
                </div>
                <div class='date-row'>{hij_str} | {mil_str}</div>
                <p style='color:#888; margin-top:5px;'>📍 {loc_label}</p>
                <div class='prayer-card'>
                    <p style='font-size:20px; margin-bottom:5px;'>متبقي على صلاة {next_p_name}</p>
                    <div class='countdown'>{time_left}</div>
                </div>
                <div class='footer'>
                    <a
