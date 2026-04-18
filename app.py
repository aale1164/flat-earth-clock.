import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد مكتبة الصلاة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")

# توقيت السعودية
sa_tz = pytz.timezone('Asia/Riyadh')

# طلب الموقع الجغرافي
location = get_geolocation()
# إحداثيات افتراضية (القصيم) في حال لم يتوفر الموقع بعد
lat, lon = 26.32, 43.97 
location_name = "القصيم"

if location and 'coords' in location:
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    location_name = "موقعك الحالي"

# تصميم الواجهة CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; background-attachment: fixed;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }}
    .prayer-card {{
        text-align: center; background: rgba(0,255,0,0.1); padding: 20px;
        border-radius: 15px; border: 2px solid #00FF00; margin-top: 20px;
    }}
    .countdown {{ font-size: 45px; color: #00FF00; font-weight: bold; font-family: 'Courier New', monospace; }}
    .date-text {{ font-size: 22px; color: #FFA500; font-weight: bold; text-align: center; margin-top: 10px; }}
</style>
""", unsafe_allow_html=True)

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    # تنسيق التاريخ أرقام فقط
    hijri_date = f"{h.day}/{h.month}/{h.year} هـ"
    miladi_date = f"{now.day}/{now.month}/{now.year} م"
    
    # حساب مواقيت الصلاة
    next_prayer_name = ""
    time_diff_str = ""
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        prayers = calc.fetch_prayer_times()
        
        if prayers:
            p_times = [
                ('الفجر', prayers['Fajr']),
                ('الظهر', prayers['Dhuhr']),
                ('العصر', prayers['Asr']),
                ('المغرب', prayers['Maghrib']),
                ('العشاء', prayers['Isha'])
            ]
            
            current_time_str = now.strftime("%H:%M:%S")
            found = False
            for name, p_time in p_times:
                # إضافة الثواني للتوقيت للمقارنة الدقيقة
                full_p_time = f"{p_time}:00"
                if full_p_time > current_time_str:
                    next_prayer_name = name
                    target = datetime.strptime(full_p_time, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
                    target = sa_tz.localize(target)
                    diff = target - now
                    
                    hours, remainder = divmod(diff.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time_diff_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    found = True
                    break
            
            if not found:
                next_prayer_name = "الفجر"
                time_diff_str = "صلاة الغد"
    except Exception as e:
        time_diff_str = "جاري الحساب..."

    with placeholder.container():
        # الساعة
        time_str = now.strftime('%I:%M:%S %p').replace('AM','صباحاً').replace('PM','مساءً')
        if time_str.startswith('0'): time_str = time_str[1:]

        st.markdown(f"<h1 style='text-align:center; color:#fff; font-size:80px; margin-bottom:0;'>{time_str}</h1>", unsafe_allow_html=True)
