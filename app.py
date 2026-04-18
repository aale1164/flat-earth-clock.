import streamlit as st
import time
from datetime import datetime
import pytz
from hijri_converter import Gregorian

# إعدادات الصفحة
st.set_page_config(page_title="مواعيد الرواتب - aale1164", layout="centered")

# توقيت السعودية والقائمة العربية
saudi_tz = pytz.timezone('Asia/Riyadh')
hijri_months_ar = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

def calculate_days(target_day, now):
    if now.day <= target_day:
        return target_day - now.day
    else:
        import calendar
        _, last_day = calendar.monthrange(now.year, now.month)
        return (last_day - now.day) + target_day

# عرض المحتوى
placeholder = st.empty()

while True:
    now = datetime.now(saudi_tz)
    
    # حساب الأيام
    d_salary = calculate_days(27, now)
    d_citizen = calculate_days(10, now)
    d_dhaman_retirement = calculate_days(1, now) # الضمان والتقاعد يوم 1
    
    # تحويل التوقيت
    current_time = now.strftime("%I:%M:%S %p").replace("AM", "صباحاً").replace("PM", "مساءً")
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hijri_date = f"{h.day} {hijri_months_ar[h.month - 1]} {h.year} هـ"

    with placeholder.container():
        # العنوان والتوقيت
        st.markdown(f"<h1 style='text-align: center; color: #00FF00;'>{current_time}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #FFA500;'>{hijri_date}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #888;'>{now.strftime('%A, %d %B %Y')}</p>", unsafe_allow_html=True)
        
        st.write("---")
        
        # استخدام الأعمدة لضمان الترتيب الصحيح
        # رواتب الموظفين
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 💰 رواتب الموظفين")
            st.caption("المدنيين والعسكريين")
        with col2:
            st.markdown(f"### {d_salary} يوم")
            
        st.write("") # مسافة بسيطة
        
        # حساب الموا
