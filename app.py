import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")

# توقيت السعودية ورابط الأذان
sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- تصميم النصوص العائمة (بدون أي مربعات أو خلفيات) ---
st.markdown("""
<style>
    /* إخفاء واجهة ستريمليت والخطوط تماماً */
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.block-container {padding-top: 0rem; background: transparent;}
    
    .stApp {
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; 
        background-position: center;
        background-attachment: fixed;
        direction: rtl; 
        font-family: 'Tajawal', sans-serif;
    }

    /* حاوية النصوص الشفافة */
    .pure-content {
        text-align: center;
        background: transparent;
        margin-top: 10vh;
    }

    /* الساعة */
    .time-val { 
        font-size: 24vw; font-weight: 900; color: #FFFFFF; 
        line-height: 0.85; 
        text-shadow: 0 0 30px rgba(0,0,0,1);
        margin: 0; 
    }
    .ampm-val { font-size: 8vw; color: #00FF00; font-weight: bold; }

    /* التاريخ */
    .date-val { 
        font-size: 7vw; color: #FFA500; font-weight: 800; 
        margin: 15px 0; 
        text-shadow: 2px 2px 15px rgba(0,0,0,1);
    }

    /* العداد التنازلي */
    .prayer-label { 
        font-size: 28px; color: #FFFFFF; font-weight: 900; 
        text-shadow: 2px 2px 10px rgba(0,0,0,1);
        margin-top: 30px;
    }
    .timer-val { 
        font-size: 18vw; color: #00FF00; font-weight: 900; 
        font-family: 'Courier New', monospace; 
        text-shadow: 0 0 25px rgba(0,0,0,1);
    }

    /* الروابط السفلية */
    .links-wrapper { margin-top: 50px; }
    .links-wrapper a { 
        color: white !important; text-decoration: none; 
        font-weight: bold; padding: 10px 20px; 
        background: rgba(255,255,255,0.1); border-radius: 50px;
        margin: 5px; border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# 1. الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# 2. التبديل (الأذان)
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 8, 1])
with col2:
    adhan_on = st.toggle("🔔 أذان الحرم المكي", value=True, key="fixed_pure_toggle")

placeholder = st.empty()

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
    except:
        pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')

        # النص العائم مباشرة على الخلفية
        st.markdown(f"""
            <div class='pure-content'>
                <div class='time-val'>{raw_t}<span class='ampm-val'>{ampm}</span></div>
                <div class='date-val'>{hij_str} | {mil_str}</div>
                <div class='prayer-label'>متبقي على صلاة {next_p_name}</div>
                <div class='timer-val'>{time_left}</div>
                <div class='links-wrapper'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if play_now and adhan_on:
            st.markdown(f'<audio src="{ADHAN_URL}" autoplay></audio>', unsafe_allow_html=True)

    time.sleep(1)
