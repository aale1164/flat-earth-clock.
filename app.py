import streamlit as st
import time
from datetime import datetime
import pytz
from hijri_converter import Gregorian

st.set_page_config(page_title="Flat Earth Pro Clock", layout="centered")

# تنسيق الواجهة (CSS) المطور للعرض المزدوج
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .clock-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 95vh;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 0 0 15px #00FF00;
        text-align: center;
    }
    .map-img {
        width: 220px;
        filter: drop-shadow(0 0 10px #00FF00);
        margin-bottom: 10px;
    }
    .time-sa { font-size: 80px; font-weight: bold; margin-bottom: -10px; }
    .label-sa { font-size: 18px; color: #00FF00; margin-bottom: 15px; }
    .time-gmt { font-size: 40px; color: #00AAAA; font-weight: bold; }
    .label-gmt { font-size: 14px; color: #00AAAA; margin-bottom: 20px; }
    .date { font-size: 20px; color: #ccc; }
    .hijri { font-size: 24px; color: #FFA500; margin-top: 5px; }
    .icon { font-size: 40px; margin: 10px 0; }
    .footer { font-size: 14px; margin-top: 20px; color: #444; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

placeholder = st.empty()
map_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flat_earth.png/600px-Flat_earth.png"

# المناطق الزمنية
saudi_tz = pytz.timezone('Asia/Riyadh')
gmt_tz = pytz.timezone('GMT')

while True:
    # الحصول على الأوقات
    now_saudi = datetime.now(saudi_tz)
    now_gmt = datetime.now(gmt_tz)
    
    hour = now_saudi.hour
    icon = "☀️" if 6 <= hour < 18 else "🌙"

    # التنسيقات
    time_sa_str = now_saudi.strftime("%I:%M:%S %p")
    time_gmt_str = now_gmt.strftime("%H:%M:%S") + " GMT"
    greg_date = now_saudi.strftime("%A, %d %B %Y")
    
    # التاريخ الهجري
    h = Gregorian(now_saudi.year, now_saudi.month, now_saudi.day).to_hijri()
    hijri_date = f"{h.day} {h.month_name()} {h.year} هـ"
    
    with placeholder.container():
        st.markdown(f"""
            <div class="clock-container">
                <img src="{map_url}" class="map-img">
                <div class="icon">{icon}</div>
                
                <div class="time-sa">{time_sa_str}</div>
                <div class="label-sa">توقيت مكة المكرمة</div>
                
                <div class="time-gmt">{time_gmt_str}</div>
                <div class="label-gmt">التوقيت العالمي المعياري</div>
                
                <div class="date">{greg_date}</div>
                <div class="hijri">{hijri_date}</div>
                <div class="footer">تطبيق خاص - الأرض ثابتة والمركز هو القطب الشمالي</div>
            </div>
            """, unsafe_allow_html=True)
    
    time.sleep(1)
