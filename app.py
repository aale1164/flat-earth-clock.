import streamlit as st
import pytz
from datetime import datetime
from hijri_converter import Gregorian

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="مواعيد الرواتب - aale1164", layout="centered")

# 2. توقيت السعودية والحسابات
saudi_tz = pytz.timezone('Asia/Riyadh')
hijri_months_ar = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

def calculate_days(target_day, now_date):
    if now_date.day <= target_day:
        return target_day - now_date.day
    else:
        import calendar
        _, last_day = calendar.monthrange(now_date.year, now_date.month)
        return (last_day - now_date.day) + target_day

now = datetime.now(saudi_tz)
d_salary = calculate_days(27, now)
d_citizen = calculate_days(10, now)
d_dhaman_retirement = calculate_days(1, now)

current_time = now.strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
h = Gregorian(now.year, now.month, now.day).to_hijri()
hijri_date = f"{h.day} {hijri_months_ar[h.month - 1]} {h.year} هـ"

# 3. التصميم (CSS) - المحاذاة والخلفية
# ملاحظة: استخدمت رابط الصورة المباشر لضمان العمل 100%
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    .stApp {{
        background-image: url("https://raw.githubusercontent.com/{st.query_params.get('user', 'aale1164')}/{st.query_params.get('repo', 'aale1164')}/main/background.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        direction: rtl;
    }}
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.6); /* تعتيم الخلفية */
        z-index: -1;
    }}
    * {{
        font-family: 'Tajawal', sans-serif;
        text-align: right;
        color: white !important;
    }}
    .main-title {{
        text-align: center;
        color: #00FF00 !important;
        font-size: 55px;
        font-weight: bold;
        margin-bottom: 0;
    }}
    .hijri-title {{
        text-align: center;
        color: #FFA500 !important;
        font-size: 24px;
        margin-top: 0;
    }}
    .salary-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        margin: 10px 0;
        border-right: 5px solid #00FF00;
    }}
    .days-count {{
        font-size: 28px;
        font-weight: bold;
        color: #00FF00 !important;
    }}
    .social-box {{
        text-align: center;
        background: rgba(0, 0, 0, 0.5);
        padding: 20px;
        border-radius: 15px;
        margin-top: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. عرض المحتوى
st.markdown(f"<p class='main-title'>{current_time}</p>", unsafe_allow_html=True)
st.markdown(f"<p class='hijri-title'>{hijri_date}</p>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #bbb !important;'>{now.strftime('%A, %d %B %Y')}</p>", unsafe_allow_html=True)

st.write("---")

# صفوف البيانات
def create_card(name, subtitle, days):
    st.markdown(f"""
    <div class="salary-row">
        <div>
            <span style="font-size: 20px; font-weight: bold;">{name}</span><br>
            <span style="font-size: 14px; color: #ccc !important;">{subtitle if subtitle else ''}</span>
        </div>
        <div class="days-count">{days} يوم</div>
    </div>
    """, unsafe_allow_html=True)

create_card("💰 رواتب الموظفين", "المدنيين والعسكريين", d_salary)
create_card("💳 حساب المواطن", None, d_citizen)
create_card("🏠 الضمان والتقاعد", "الضمان المطور والتأمينات", d_dhaman_retirement)

st.write("---")

# التواصل الاجتماعي
st.markdown(f"""
    <div class="social-box">
        <p style="font-size: 14px; color: #8
