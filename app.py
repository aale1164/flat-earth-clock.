import streamlit as st
import time

st.set_page_config(page_title="Flat Earth Clock", layout="centered")

# تنسيق الواجهة (CSS)
st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .clock-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 0 0 20px #00FF00;
    }
    .time { font-size: 80px; font-weight: bold; }
    .date { font-size: 24px; margin-top: 10px; }
    .footer { font-size: 18px; margin-top: 30px; color: #555; }
    </style>
    """, unsafe_allow_html=True)

# حاوية الساعة
placeholder = st.empty()

while True:
    now = time.localtime()
    current_time = time.strftime("%H:%M:%S", now)
    current_date = time.strftime("%A, %d %B %Y", now)
    
    with placeholder.container():
        st.markdown(f"""
            <div class="clock-container">
                <div class="time">{current_time}</div>
                <div class="date">{current_date}</div>
                <div class="footer">Flat Earth Clock - Stationary & Central</div>
            </div>
            """, unsafe_allow_html=True)
    
    time.sleep(1)
