import streamlit as st
import pytz
from datetime import datetime
from hijri_converter import Gregorian

# 1. إعداد الصفحة والمنطقة الزمنية
st.set_page_config(page_title="رواتب السعودية - aale1164", layout="centered")
sa_tz = pytz.timezone('Asia/Riyadh')
months = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

# 2. وظائف الحساب
def get_days(day, now):
    if now.day <= day: return day - now.day
    import calendar
    return (calendar.monthrange(now.year, now.month)[1] - now.day) + day

now = datetime.now(sa_tz)
h = Gregorian(now.year, now.month, now.day).to_hijri()

# 3. التصميم (CSS) - المحاذاة والخلفية
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; direction: rtl; font-family: 'Tajawal', sans-serif;
    }}
    .card {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 15px; background: rgba(255,255,255,0.1); border-radius: 12px;
        margin: 10px 0; border-right: 6px solid #00FF00; text-align: right;
    }}
    .days {{ font-size: 24px; color: #00FF00; font-weight: bold; }}
    .social {{ text-align: center; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 15px; margin-top: 20px; }}
</style>
""", unsafe_allow_html=True)

# 4. عرض الوقت والتاريخ
st.markdown(f"<h1 style='text-align:center; color:#00FF00;'>{now.strftime('%I:%M %p').replace('AM','صباحاً').replace('PM','مساءً')}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align:center; color:#FFA500;'>{h.day} {months[h.month-1]} {h.year} هـ</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ccc;'>"+now.strftime('%A, %d %B %Y')+"</p>", unsafe_allow_html=True)

st.divider()

# 5. عرض الرواتب
def row(name, days):
    st.markdown(f'<div class="card"><span>{name}</span><span class="days">{days} يوم</span></div>', unsafe_allow_html=True)

row("💰 رواتب الموظفين (عسكري/مدني)", get_days(27, now))
row("💳 حساب المواطن", get_days(10, now))
row("🏠 الضمان والتقاعد", get_days(1, now))

# 6. التواصل
st.markdown(f"""
<div class="social">
    <p style="color:#888; font-size:12px;">إعداد وتطوير</p>
    <a href="https://twitter.com/aale1164" style="color:#1DA1F2; text-decoration:none;">𝕏 @aale1164</a> | 
    <a href="https://www.snapchat.com/add/aale112" style="color:#FFFC00; text-decoration:none;">👻 aale112</a>
</div>
""", unsafe_allow_html=True)

if st.button('🔄 تحديث'): st.rerun()
