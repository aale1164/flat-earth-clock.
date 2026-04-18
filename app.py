import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبات بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")
sa_tz = pytz.timezone('Asia/Riyadh')

# تصميم CSS متوافق مع الجوال
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }
    .main-container { text-align: center; color: white; width: 100%; }
    .time-text { font-size: 16vw; font-weight: bold; display: inline-block; margin: 0; }
    .ampm-text { font-size: 6vw; color: #00FF00; vertical-align: super; margin-right: 2px; }
    .date-row { font-size: 5vw; color: #FFA500; font-weight: bold; margin-top: 5px; }
    .prayer-card {
        background: rgba(0,255,0,0.1); padding: 15px; border-radius: 20px;
        border: 2px solid #00FF00; margin: 20px auto 10px auto; width: 90%; max-width: 350px;
    }
    .countdown { font-size: 10vw; color: #00FF00; font-weight: bold; font-family: 'Courier New', monospace; }
    .footer { margin-top: 25px; opacity: 0.8; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# الموقع الافتراضي (القصيم)
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# عرض الساعة والبيانات
placeholder = st.empty()

# حالة المنبه (خارج الحلقة لضمان الثبات)
if 'adhan_on' not in st.session_state:
    st.session_state.adhan_on = True

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "جاري الحساب", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr_f = now.strftime("%H:%M:%S")
            for name, p_t in p_list:
                p_f = f"{p_t}:00"
                if p_f > curr_f:
                    next_p_name = name
                    target = sa_tz.localize(datetime.strptime(p_f, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    h_v, rem = divmod(diff.seconds, 3600)
                    m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    break
                if curr_f == p_f: play_now = True
            if not next_p_name or next_p_name == "جاري الحساب": next_p_name, time_left = "الفجر", "صلاة الغد"
    except: pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')
        
        # تشغيل الأذان
        if play_now and st.session_state.adhan_on:
            st.markdown('<audio src="
