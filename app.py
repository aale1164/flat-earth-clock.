import streamlit as st
import time
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Flat Earth Clock", page_icon="🌍")

# تصميم واجهة المستخدم باستخدام CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        text-align: center;
    }
    .clock-text {
        font-family: 'Courier New', Courier, monospace;
        color: #00ff00;
        font-size: 80px;
        font-weight: bold;
        border: 2px solid #333;
        padding: 20px;
        border-radius: 15px;
        background: black;
        box-shadow: 0 0 20px #00ff00;
    }
    .theory-text {
        color: white;
        font-size: 20px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🕒 ساعة الأرض المسطحة الرقمية")
st.write("استعراض الوقت بناءً على التوقيت المحلي بنمط رقمي")

# مكان عرض الساعة
clock_placeholder = st.empty()

# تشغيل الساعة بشكل مستمر
while True:
    now = datetime.now().strftime("%H:%M:%S")
    clock_placeholder.markdown(f'<p class="clock-text">{now}</p>', unsafe_allow_index=True)
    
    st.markdown('<p class="theory-text">"الزمن ثابت.. والمركز هو القطب الشمالي"</p>', unsafe_allow_index=True)
    
    time.sleep(1)
