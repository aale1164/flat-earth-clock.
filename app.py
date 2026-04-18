import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبة
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة الشفافة", layout="centered")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- تصميم زجاجي شفاف (Glassmorphism) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.2)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }

    .glass-box {
        text-align: center;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 25px 10px;
        border-radius: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 10px auto;
    }

    .time-text { 
        font-size: 20vw; font-weight: 900; color: #FFFFFF; 
        text-shadow: 0 4px 15px rgba(0,0,0,1); line-height: 1; margin: 0; 
    }
    
    .ampm-text { font-size: 7vw; color: #00FF00; font-weight: bold; }
    
    .date-text { font-size: 5.5vw; color: #FFA500; font-weight: 700; margin: 10px 0; }

    .prayer-card-glass {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px 10px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 15px auto;
        width: 100%; max-width: 380px;
    }

    .prayer-label { font-size: 22px; color: #FFFFFF; font-weight: 700; margin-bottom: 5px; }
    
    .countdown { 
        font-size: 13vw; color: #00FF00; font-weight: 900; 
        font-family: 'Courier New', monospace; 
        text-shadow: 0 0 15px rgba(0,255,0,0.4);
    }

    .footer-btn {
        display: inline-block; padding: 8px 15px;
        background: rgba(0,0,0,0.3); border-radius: 12px;
        color: white !important; text-decoration: none;
        font-size: 14px; margin: 5px; border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 1. الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# 2. زر التنبيه المكي (خارج الحلقة لمنع أخطاء التكرار)
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 10, 1])
with col2:
    adhan_on = st.toggle("🔔 أذان الحرم المكي الشريف", value=True, key="final_glass_toggle")

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    # إصلاح السطر الذي سبب المشكلة:
    current_date_str = now.strftime("%Y-%m-%d")
    
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=current_date_str)
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
                    h_v, rem = divmod(diff.seconds, 3600); m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    break
                if curr_f == p_f: play_now = True
    except:
        pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')

        st.markdown(f"""
            <div class='glass-box'>
                <div class='time-text'>{raw_t}<span class='ampm-text'>{ampm}</span></div>
                <div class='date-text'>{hij_str} | {mil_str}</div>
                <div class='prayer-card-glass'>
                    <div class='prayer-label'>متبقي على صلاة {next_p_name}</div>
                    <div class='countdown'>{time_left}</div>
                </div>
                <div style='margin-top:15px;'>
                    <a href='https://twitter.com/aale1164' class='footer-btn' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' class='footer-btn' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if play_now and adhan_on:
            st.markdown(f'<audio src="{ADHAN_URL}" autoplay></audio>', unsafe_allow_html=True)

    time.sleep(1)
