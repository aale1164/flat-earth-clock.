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

st.set_page_config(page_title="Clock", layout="centered")

sa_tz = pytz.timezone('Asia/Riyadh')
URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# تصميم شفاف وواضح
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }
    .glass {
        background: rgba(0, 0, 0, 0.4); 
        border-radius: 35px;
        padding: 20px;
        text-align: center;
        margin: 10px auto;
        backdrop-filter: blur(5px);
    }
    .t-txt { 
        font-size: 18vw; font-weight: 900; 
        color: rgba(255, 255, 255, 0.85); 
        line-height: 1; margin: 0; 
    }
    .p-card {
        background: #FFFFFF; padding: 20px; 
        border-radius: 25px; margin: 20px auto; 
        width: 100%; max-width: 380px;
        border-bottom: 8px solid #008800;
    }
    .p-time { 
        font-size: 12vw; color: #008800; 
        font-weight: 900; font-family: 'Courier New'; 
    }
</style>
""", unsafe_allow_html=True)

# الموقع
loc = get_geolocation()
lat, lon = 26.32, 43.97
if loc and 'coords' in loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    h_str = f"{h.day}/{h.month}/{h.year} هـ"
    m_str = f"{now.day}/{now.month}/{now.year} م"
    
    p_name, t_rem, play = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(lat, lon, 'makkah', now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            plist = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr = now.strftime("%H:%M:%S")
            for name, pt in plist:
                target_s = f"{pt}:00"
                if target_s > curr:
                    p_name = name
                    # فك الأسطر الطويلة لأسطر قصيرة جداً
                    y, m, d = now.year, now.month, now.day
                    obj = datetime.strptime(target_s, "%H:%M:%S")
                    obj = obj.replace(year=y, month=m, day=d)
                    t_obj = sa_tz.localize(obj)
                    diff = t_obj - now
                    sec = diff.seconds
                    hh, rem = divmod(sec, 3600)
                    mm, ss = divmod(rem, 60)
                    t_rem = f"{hh:02d}:{mm:02d}:{ss:02d}"
                    break
                if curr == target_s:
                    play = True
    except:
        pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S').lstrip('0')
        ampm = now.strftime('%p')

        st.markdown(f"""
            <div class='glass'>
                <div class='t-txt'>{raw_t}<span style='color:#0f0;font-size:7vw;'>{ampm}</span></div>
                <div style='color:#ffa500;font-size:5vw;font-weight:700;'>{h_str} | {m_str}</div>
                <div class='prayer-card'>
                    <div style='color:#333;font-size:22px;font-weight:bold;'>متبقي على صلاة {p_name}</div>
                    <div class='p-time'>{t_rem}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 10, 1])
        with col2:
            on = st.toggle("🔔 أذان الحرم المكي الشريف", value=True, key="v6")

        if play and on:
            st.markdown(f'<audio src="{URL}" autoplay></audio>', unsafe_allow_html=True)

    time.sleep(1)
