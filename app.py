import streamlit as st
import pytz
from datetime import datetime
from hijri_converter import Gregorian

# إعدادات الصفحة - وضعناها في البداية لضمان الاستقرار
st.set_page_config(page_title="مواعيد الرواتب - aale1164", layout="centered")

# توقيت السعودية
saudi_tz = pytz.timezone('Asia/Riyadh')
hijri_months_ar = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

def calculate_days(target_day, now):
    if now.day <= target_day:
        return target_day - now.day
    else:
        import calendar
        _, last_day = calendar.monthrange(now.year, now.month)
        return (last_day - now.day) + target_day

# الحصول على الوقت الحالي مرة واحدة عند التحميل
now = datetime.now(saudi_tz)
d_salary = calculate_days(27, now)
d_citizen = calculate_days(10, now)
d_dhaman_retirement = calculate_days(1, now)

current_time = now.strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
h = Gregorian(now.year, now.month, now.day).to_hijri()
hijri_date = f"{h.day} {hijri_months_ar[h.month - 1]} {h.year} هـ"

# العرض الثابت (أكثر استقراراً للمتصفح)
st.markdown(f"<h1 style='text-align: center; color: #00FF00;'>{current_time}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #FFA500;'>{hijri_date}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #888;'>{now.strftime('%A, %d %B %Y')}</p>", unsafe_allow_html=True)

st.write("---")

# استخدام نظام الأعمدة المستقر
def draw_row(title, subtitle, days):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {title}")
        if subtitle: st.caption(subtitle)
    with col2:
        st.markdown(f"### {days} يوم")
    st.write("")

draw_row("💰 رواتب الموظفين", "المدنيين والعسكريين", d_salary)
draw_row("💳 حساب المواطن", None, d_citizen)
draw_row("🏠 الضمان والتقاعد", "الضمان المطور والتأمينات الاجتماعية", d_dhaman_retirement)

st.write("---")

# الروابط الشخصية
st.markdown(f"""
    <div style="text-align: center; background-color: #1e2130; padding: 20px; border-radius: 15px; border: 1px solid #333;">
        <p style="color: #888; margin-bottom: 10px; font-size: 14px;">إعداد وتطوير</p>
        <a href="https://twitter.com/aale1164" style="color: #1DA1F2; text-decoration: none; font-weight: bold; font-size: 18px;">𝕏 تويتر: @aale1164</a><br>
        <div style="margin: 10px 0;"></div>
        <a href="https://www.snapchat.com/add/aale112" style="color: #FFFC00; text-decoration: none; font-weight: bold; font-size: 18px;">👻 سناب: aale112</a>
    </div>
""", unsafe_allow_html=True)

# زر تحديث يدوي بسيط بدلاً من التحديث التلقائي المزعج للمتصفح
if st.button('تحديث الوقت'):
    st.rerun()
