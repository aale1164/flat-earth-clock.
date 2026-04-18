import streamlit as st
import time
from datetime import datetime
import pytz
from hijri_converter import Gregorian

st.set_page_config(page_title="مواعيد الرواتب - السعودية", layout="centered")

# تنسيق الواجهة (CSS) لتصميم احترافي وخدمي
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        color: #ffffff;
        font-family: 'Arial';
    }
    .salary-card {
        background-color: #1e2130;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        width: 90%;
        border-right: 5px solid #00FF00;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .time { font-size: 50px; font-weight: bold; color: #00FF00; }
    .label-sa { font-size: 18px; color: #aaa; }
    .hijri { font-size: 22px; color: #FFA500; margin-top: 5px; }
    .social-links { margin-top: 30px; padding: 20px; border-top: 1px solid #333; width: 100%; }
    .twitter { color: #1DA1F2; font-weight: bold; text-decoration: none; font-size: 18px; }
    .snap { color: #FFFC00; font-weight: bold; text-decoration: none; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# قائمة أسماء الأشهر الهجرية بالعربي
hijri_months_ar = [
    "المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة",
    "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
]

saudi_tz = pytz.timezone('Asia/Riyadh')

placeholder = st.empty()

while True:
    now = datetime.now(saudi_tz)
    
    # حساب الأيام المتبقية للرواتب (غالباً يوم 27 من كل شهر ميلادي)
    salary_day = 27
    if now.day <= salary_day:
        days_left = salary_day - now.day
    else:
        # إذا فات يوم 27، يحسب للشهر القادم (تبسيط)
        days_left = (30 - now.day) + salary_day
    
    # التوقيت
    current_time = now.strftime("%I:%M:%S %p")
    greg_date = now.strftime("%A, %d %B %Y")
    
    # التاريخ الهجري
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    month_name_ar = hijri_months_ar[h.month - 1]
    hijri_date = f"{h.day} {month_name_ar} {h.year} هـ"

    with placeholder.container():
        st.markdown(f"""
            <div class="container">
                <div class="time">{current_time}</div>
                <div class="label-sa">توقيت مكة المكرمة</div>
                <div class="hijri">{hijri_date}</div>
                <div style="font-size: 18px; color: #ccc;">{greg_date}</div>
                
                <div style="margin-top: 30px; width: 100%;">
                    <div class="salary-card">
                        <h3 style="margin:0; color:#00FF00;">الرواتب الموحدة</h3>
                        <p style="margin:5px 0;">متبقي <b>{days_left}</b> يوم على راتب القطاع العام والخاص</p>
                    </div>
                    
                    <div class="salary-card" style="border-right-color: #FFA500;">
                        <h3 style="margin:0; color:#FFA500;">الضمان الاجتماعي</h3>
                        <p style="margin:5px 0;">يصرف في بداية كل شهر ميلادي</p>
                    </div>
                </div>

                <div class="social-links">
                    <p style="margin-bottom:10px; font-size: 14px; color: #888;">برمجة وتطوير</p>
                    <a href="https://twitter.com/aale1164" class="twitter">Twitter: @aale1164</a><br>
                    <a href="https://www.snapchat.com/add/aale112" class="snap">Snapchat: aale112</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    time.sleep(1)
