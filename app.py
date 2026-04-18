import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- تصميم احترافي: وضوح تام وتوزيع متناسق ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }

    .main-box {
        text-align: center;
        background: rgba(0, 0, 0, 0.6);
        padding: 20px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 10px auto;
        width: 95%;
    }

    .time-text { 
        font-size: 18vw; font-weight: 900; color: #FFFFFF; 
        line-height: 1; margin: 0;
    }
    
    .ampm-text { font-size: 7vw; color: #00FF00; vertical-align: baseline; }

    .date-text { font-size: 5.5vw; color: #FFA500; font-weight: 700; margin: 10px 0; }

    /* مربع الصلاة: أبيض ناصع وواضح جداً */
    .prayer-card {
        background: #FFFFFF; padding: 20px; border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin: 20px auto; 
        width: 100%; max-width: 360px;
    }

    .prayer-label { font-size: 22px; color: #333; font-weight: bold; }
    .countdown { font-size: 12vw; color: #008800; font-weight: 900; font-family: 'Courier New', monospace; }

    /* تنسيق زر التنبيه أسفل المربع */
    .stToggle {
        background: #008800; padding: 10px 20px; border-radius: 50px;
        display: inline-block; border: 2px solid white; margin-top: 10px;
    }
    
    .footer { margin-top: 30px; font-weight: bold; letter-spacing: 1px; }
    .footer a { color: white !important; text-decoration: none; padding: 5px 10px; border-radius: 10px; background: rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

# الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

placeholder = st.empty()

# تشغيل الساعة والحسابات
while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "الفجر", "00:00:00", False
    
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
                    h_v, rem = divmod(diff.seconds, 3600); m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    break
                if curr_f == p_f: play_now = True
    except: pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')

        # الواجهة المركزية
        st.markdown(f"""
            <div class='main-box'>
                <div class='time-text'>{raw_t}<span class='ampm-text'>{ampm}</span></div>
                <div class='date-text'>{hij_str} | {mil_str}</div>
                <div class='prayer-card'>
                    <div class='prayer-label'>متبقي على صلاة {next_p_name}</div>
                    <div class='countdown'>{time_left}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # زر التنبيه تحت المربع (خارج الـ Markdown لتجنب أخطاء التفاعل)
        c1, c2, c3 = st.columns([1, 8, 1])
        with c2:
            adhan_on = st.toggle("🔔 تفعيل أذان الحرم المكي الشريف", value=True, key="mecca_adhan_fixed")

        # الفوتر
        st.markdown(f"""
            <div class='main-box' style='background:transparent; border:none;'>
                <div class='footer'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a> 
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if play_now and adhan_on:
            st.markdown(f'<audio src="{ADHAN_URL}" autoplay></audio>', unsafe_allow_html=True)

    time.sleep(1)
