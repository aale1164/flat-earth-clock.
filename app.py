import streamlit as st
import time
from datetime import datetime
import pytz
from hijri_converter import Gregorian

st.set_page_config(page_title="حساب الرواتب - aale1164", layout="centered")

# التنسيق الجديد المعالج للمحاذاة العربية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    .main { background-color: #0e1117; direction: rtl; }
    .stApp { direction: rtl; }
    
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        font-family: 'Tajawal', sans-serif;
    }
    
    .time-display { font-size: 55px; font-weight: bold; color: #00FF00; margin-bottom: 0px; }
    .hijri-display { font-size: 24px; color: #FFA500; font-weight: bold; margin-bottom: 20px; }
    
    .salary-card {
        background-color: #1e2130;
        border-radius: 12px;
        padding: 15px 20px;
        margin: 8px 0;
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-right: 6px solid #00FF00;
        direction: rtl; /* ضمان اتجاه البطاقة من اليمين */
    }
    
    .card-text { font-size: 18px; color: #ffffff; font-weight: bold; }
    .card-number { font-size: 22px; color: #00FF00; font-weight: bold; }
    
    .social-links {
        margin-top: 30px;
        padding: 20px;
        background-color: #161925;
        border-radius: 15px;
        width: 100%;
    }
    .twitter-btn { color: #1DA1F2; text-decoration: none; font-size: 18px; font-weight: bold; display: block; margin-bottom: 10px; }
    .snap-btn { color: #FFFC00; text-decoration: none; font-size: 18px; font-weight: bold; display: block; }
    </style>
    """, unsafe_allow_html=True)

# قائمة الأشهر العربية
hijri_months_ar = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

saudi_tz = pytz.timezone('Asia/Riyadh')

def calculate_days(target_day, now):
    if now.day <= target_day:
        return target_day - now.day
    else:
        import calendar
        _, last_day = calendar.monthrange(now.year, now.month)
        return (last_day - now.day) + target_day

placeholder = st.empty()

while True:
    now = datetime.now(saudi_tz)
    
    # حساب الأيام
    d_salary = calculate_days(27, now)
    d_citizen = calculate_days(10, now)
    d_dhaman = calculate_days(1, now)
    
    current_time = now.strftime("%I:%M:%S %p").replace("AM", "صباحاً").replace("PM", "مساءً")
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hijri_date = f"{h.day} {hijri_months_ar[h.month - 1]} {h.year} هـ"

    with placeholder.container():
        st.markdown(f"""
            <div class="container">
                <div class="time-display">{current_time}</div>
                <div class="hijri-display">{hijri_date}</div>
                
                <div class="salary-card" style="border-right-color: #00FF00;">
                    <span class="card-text">رواتب الموظفين (عسكري/مدني)</span>
                    <span class="card-number">{d_salary} يوم</span>
                </div>

                <div class="salary-card" style="border-right-color: #00ACEE;">
                    <span class="card-text">حساب المواطن</span>
                    <span class="card-number" style="color: #00ACEE;">{d_citizen} يوم</span>
                </div>

                <div class="salary-card" style="border-right-color: #FFA500;">
                    <span class="card-text">الضمان الاجتماعي المطور</span>
                    <span class="card-number" style="color: #FFA500;">{d_dhaman} يوم</span>
                </div>

                <div class="social-links">
                    <span style="color: #777; font-size: 14px; display: block; margin-bottom: 10px;">إعداد وتطوير</span>
                    <a href="https://twitter.com/aale1164" class="twitter-btn">𝕏 تويتر: @aale1164</a>
                    <a href="https://www.snapchat.com/add/aale112" class="snap-btn">👻 سناب: aale112</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    time.sleep(1)
