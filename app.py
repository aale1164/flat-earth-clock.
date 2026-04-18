import streamlit as st
import time
from datetime import datetime, timedelta
import pytz
from hijri_converter import Gregorian

st.set_page_config(page_title="حساب الرواتب - aale1164", layout="centered")

# تنسيق الواجهة (CSS) - تم إصلاح المحاذاة والخطوط
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
    }
    .main { background-color: #0e1117; }
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        color: #ffffff;
    }
    .time { font-size: 60px; font-weight: bold; color: #00FF00; text-shadow: 0 0 10px #00FF0044; }
    .salary-card {
        background: linear-gradient(145deg, #1e2130, #161925);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        width: 100%;
        border-right: 8px solid #00FF00;
        text-align: right;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-title { font-size: 18px; font-weight: bold; color: #ffffff; }
    .card-days { font-size: 24px; font-weight: bold; color: #00FF00; }
    .social-links { 
        margin-top: 40px; 
        padding: 20px; 
        border-radius: 15px;
        background: #161925;
        width: 100%;
    }
    .twitter { color: #1DA1F2; text-decoration: none; font-size: 20px; font-weight: bold; }
    .snap { color: #FFFC00; text-decoration: none; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# قائمة أسماء الأشهر الهجرية
hijri_months_ar = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

saudi_tz = pytz.timezone('Asia/Riyadh')

def get_days_until(target_day, current_now):
    if current_now.day <= target_day:
        return target_day - current_now.day
    else:
        # حساب الأيام المتبقية لنهاية الشهر الحالي + يوم الهدف في الشهر القادم
        import calendar
        _, last_day = calendar.monthrange(current_now.year, current_now.month)
        return (last_day - current_now.day) + target_day

placeholder = st.empty()

while True:
    now = datetime.now(saudi_tz)
    
    # حسابات الأيام (الرواتب غالباً يوم 27، حساب المواطن يوم 10، الضمان يوم 1)
    days_to_salary = get_days_until(27, now)
    days_to_citizen = get_days_until(10, now)
    days_to_dhaman = get_days_until(1, now)
    
    current_time = now.strftime("%I:%M:%S %p").replace("AM", "صباحاً").replace("PM", "مساءً")
    greg_date = now.strftime("%A, %d %B %Y")
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hijri_date = f"{h.day} {hijri_months_ar[h.month - 1]} {h.year} هـ"

    with placeholder.container():
        st.markdown(f"""
            <div class="container">
                <div class="time">{current_time}</div>
                <div style="font-size: 22px; color: #FFA500; font-weight: bold;">{hijri_date}</div>
                <div style="font-size: 16px; color: #888; margin-bottom: 20px;">{greg_date}</div>
                
                <div class="salary-card">
                    <div class="card-title">رواتب الموظفين (عسكري/مدني)</div>
                    <div class="card-days">{days_to_salary} يوم</div>
                </div>

                <div class="salary-card" style="border-right-color: #00ACEE;">
                    <div class="card-title">حساب المواطن</div>
                    <div class="card-days" style="color: #00ACEE;">{days_to_citizen} يوم</div>
                </div>

                <div class="salary-card" style="border-right-color: #FFA500;">
                    <div class="card-title">الضمان الاجتماعي المطور</div>
                    <div class="card-days" style="color: #FFA500;">{days_to_dhaman} يوم</div>
                </div>

                <div class="social-links">
                    <p style="color: #666; margin-bottom: 10px;">إعداد وتطوير</p>
                    <a href="https://twitter.com/aale1164" class="twitter">𝕏 @aale1164</a>
                    <div style="margin: 10px 0;"></div>
                    <a href="https://www.snapchat.com/add/aale112" class="snap">👻 aale112</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    time.sleep(1)
