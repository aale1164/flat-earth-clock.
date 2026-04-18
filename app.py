import streamlit as st
import pytz
from datetime import datetime
try:
    from hijri_converter import Gregorian
except:
    st.error("جاري تحميل المكتبات البرمجية.. يرجى تحديث الصفحة بعد ثوانٍ")

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="مواعيد الرواتب - aale1164", layout="centered")

# توقيت السعودية
saudi_tz = pytz.timezone('Asia/Riyadh')
hijri_months_ar = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

def calculate_days(target_day, now_date):
    if now_date.day <= target_day:
        return target_day - now_date.day
    else:
        import calendar
        _, last_day = calendar.monthrange(now_date.year, now_date.month)
        return (last_day - now_date.day) + target_day

# محاولة الحصول على البيانات
try:
    now = datetime.now(saudi_tz)
    d_salary = calculate_days(27, now)
    d_citizen = calculate_days(10, now)
    d_dhaman_retirement = calculate_days(1, now)

    current_time = now.strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hijri_date = f"{h.day} {hijri_months_ar[h.month - 1]} {h.year} هـ"

    # عرض الواجهة
    st.markdown(f"<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color: #00FF00; margin-bottom: 0;'>{current_time}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #FFA500; margin-top: 0;'>{hijri_date}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #888;'>{now.strftime('%A, %d %B %Y')}</p>", unsafe_allow_html=True)
    st.markdown(f"</div>", unsafe_allow_html=True)

    st.divider()

    # صفوف الرواتب
    c1, c2 = st.columns([3, 1])
    c1.subheader("💰 رواتب الموظفين")
    c2.subheader(f"{d_salary} يوم")
    
    c3, c4 = st.columns([3, 1])
    c3.subheader("💳 حساب المواطن")
    c4.subheader(f"{d_citizen} يوم")
    
    c5, c6 = st.columns([3, 1])
    c5.subheader("🏠 الضمان والتقاعد")
    c6.subheader(f"{d_dhaman_retirement} يوم")

    st.divider()

    # حسابات التواصل
    st.markdown(f"""
        <div style="text-align: center; background-color: #1e2130; padding: 15px; border-radius: 10px;">
            <p style="color: #888; margin-bottom: 5px;">إعداد وتطوير</p>
            <a href="https://twitter.com/aale1164" style="color: #1DA1F2; text-decoration: none; font-weight: bold;">𝕏 @aale1164</a>
            <span style="color: #444; margin: 0 10px;">|</span>
            <a href="https://www.snapchat.com/add/aale112" style="color: #FFFC00; text-decoration: none; font-weight: bold;">👻 aale112</a>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.warning("يرجى الانتظار قليلاً حتى يتم تفعيل السيرفر...")

if st.button('تحديث البيانات'):
    st.rerun()
