import streamlit as st
import time
from hijri_converter import Gregorian

st.set_page_config(page_title="Flat Earth Pro", layout="centered")

# تنسيق الواجهة (CSS) مع إضافة لمسات بصرية
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
    .time { font-size: 70px; font-weight: bold; }
    .date { font-size: 20px; color: #ccc; }
    .hijri { font-size: 24px; color: #FFA500; margin-top: 5px; }
    .icon { font-size: 50px; margin: 15px 0; }
    .footer { font-size: 16px; margin-top: 20px; color: #444; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

placeholder = st.empty()

# رابط صورة خريطة الأرض المسطحة (رابط موثوق)
map_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flat_earth.png/600px-Flat_earth.png"

while True:
    t = time.localtime()
    hour = t.tm_hour
    
    # تحديد التأثير البصري (شمس أو قمر)
    if 6 <= hour < 18:
        icon = "☀️"  # وقت النهار
        status_text = "حالة النهار فوق الخريطة"
    else:
        icon = "🌙"  # وقت الليل
        status_text = "حالة الليل فوق الخريطة"

    # التوقيت والتاريخ
    current_time = time.strftime("%I:%M:%S %p", t)
    greg_date = time.strftime("%A, %d %B %Y", t)
    
    # التاريخ الهجري
    h = Gregorian(t.tm_year, t.tm_mon, t.tm_mday).to_hijri()
    hijri_date = f"{h.day} {h.month_name()} {h.year} هـ"
    
    with placeholder.container():
        st.markdown(f"""
            <div class="clock-container">
                <img src="{map_url}" class="map-img">
                <div class="icon">{icon}</div>
                <div class="time">{current_time}</div>
                <div class="date">{greg_date}</div>
                <div class="hijri">{hijri_date}</div>
                <div class="footer">تطبيق خاص - الأرض ثابتة والمركز هو القطب الشمالي</div>
            </div>
            """, unsafe_allow_html=True)
    
    time.sleep(1)
