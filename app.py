import streamlit as st
import time
from datetime import datetime
import pytz
from hijri_converter import Gregorian

st.set_page_config(page_title="Flat Earth Pro", layout="centered")

# تنسيق الواجهة (CSS)
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .clock-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 90vh;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 0 0 15px #00FF00;
        text-align: center;
    }
    .map-img {
        width: 250px;
        filter: drop-shadow(0 0 10px #00FF00);
        margin-bottom: 20px;
    }
    .time { font-size: 85px; font-weight: bold; margin-bottom: 10px; }
    .label-sa { font-size: 20px; color: #00FF00; margin-bottom: 20px; letter-spacing: 2px; }
    .date { font-size: 22px; color: #ccc; }
    .hijri { font-size: 26px; color: #FFA500; margin-top: 8px; font-weight: bold; }
    .icon { font-size: 50px; margin: 15px 0; }
    .footer { font-size: 16px; margin-top: 30px; color: #444; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

placeholder = st.empty()
map_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flat_earth.png/600px-Flat_earth.png"

# تحديد المنطقة الزمنية للسعودية
saudi_tz = pytz.timezone('Asia/Riyadh')

while True:
    # الحصول على الوقت الحالي بتوقيت السعودية
    now_saudi = datetime.now(saudi_tz)
    hour = now_saudi.hour
    
    # تحديد التأثير البصري (شمس أو قمر)
    icon = "☀️" if 6 <= hour < 18 else "🌙"

    # التوقيت بنظام 12 ساعة
    current_time = now_saudi.strftime("%I:%M:%S %p")
    # التاريخ الميلادي
    greg_date = now_saudi.strftime("%A, %d %B %Y")
    
    # التاريخ الهجري
    h = Gregorian(now_saudi.year, now_saudi.month, now_saudi.day).to_hijri()
    hijri_date = f"{h.day} {h.month_name()} {h.year} هـ"
    
    with placeholder.container():
        st.markdown(f"""
            <div class="clock-container">
                <img src="{map_url}" class="map-img">
                <div class="icon">{icon}</div>
                <div class="time">{current_time}</div>
                <div class="label-sa">توقيت مكة المكرمة</div>
                <div class="date">{greg_date}</div>
                <div class="hijri">{hijri_date}</div>
                <div class="footer">تطبيق خاص - الأرض ثابتة والمركز هو القطب الشمالي</div>
            </div>
            """, unsafe_allow_html=True)
    
    time.sleep(1)
