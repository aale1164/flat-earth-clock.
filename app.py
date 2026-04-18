import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from prayer_times_calculator import PrayerTimesCalculator

# إعداد الصفحة
st.set_page_config(page_title="ساعة الرواتب والصلاة - aale1164", layout="centered")

# توقيت السعودية والقوائم
sa_tz = pytz.timezone('Asia/Riyadh')
months = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

# تصميم الواجهة
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; direction: rtl; font-family: 'Tajawal', sans-serif;
    }}
    .card {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 20px; background: rgba(255,255,255,0.1); border-radius: 10px;
        margin: 8px 0; border-right: 5px solid #00FF00;
    }}
    .val {{ font-size: 22px; color: #00FF00; font-weight: bold; }}
    .social {{ text-align: center; background: rgba(0,0,0,0.5); padding: 15px; border-radius: 15px; margin-top: 20px; }}
</style>
""", unsafe_allow_html=True)

# شريط جانبي لاختيار الموقع
st.sidebar.header("📍 إعدادات الموقع")
city = st.sidebar.text_input("المدينة", "Buraydah")
country = st.sidebar.text_input("الدولة", "Saudi Arabia")

def get_days(day, now):
    if now.day <= day: return day - now.day
    import calendar
    return (calendar.monthrange(now.year, now.month)[1] - now.day) + day

placeholder = st.empty()

# حلقة التحديث الحي
while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    # حساب مواقيت الصلاة
    try:
        calc = PrayerTimesCalculator(latitude=26.32, longitude=43.97, registration_method='makkah', date=now.strftime("%Y-%m-%d"))
        prayers = calc.fetch_prayer_times()
    except:
        prayers = None

    with placeholder.container():
        # عرض الساعة (حية بالثواني)
        st.markdown(f"<h1 style='text-align:center; color:#00FF00; font-size:60px; margin-bottom:0;'>{now.strftime('%I:%M:%S %p').replace('AM','صباحاً').replace('PM','مساءً')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:#FFA500; margin-top:0;'>{h.day} {months[h.month-1]} {h.year} هـ</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📅 {now.strftime('%d-%m-%Y')}")
        with col2:
            st.write(f"📍 {city}")

        st.divider()

        # عرض الرواتب
        st.markdown("### 💰 المتبقي على الرواتب")
        st.markdown(f'<div class="card"><span>رواتب الموظفين</span><span class="val">{get_days(27, now)} يوم</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><span>حساب المواطن</span><span class="val">{get_days(10, now)} يوم</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><span>الضمان والتقاعد</span><span class="val">{get_days(1, now)} يوم</span></div>', unsafe_allow_html=True)

        # عرض مواقيت الصلاة
        if prayers:
            st.divider()
            st.markdown("### 🕋 مواقيت الصلاة")
            for p_name, p_time in [('الفجر', 'Fajr'), ('الظهر', 'Dhuhr'), ('العصر', 'Asr'), ('المغرب', 'Maghrib'), ('العشاء', 'Isha')]:
                st.markdown(f'<div class="card" style="border-right-color:#FFA500;"><span>صلاة {p_name}</span><span class="val" style="color:#FFA500;">{prayers[p_time]}</span></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="social">
            <p style="color:#888; font-size:12px;">إعداد وتطوير</p>
            <a href="https://twitter.com/aale1164" style="color:#1DA1F2; text-decoration:none; font-weight:bold;">𝕏 @aale1164</a> | 
            <a href="https://www.snapchat.com/add/aale112" style="color:#FFFC00; text-decoration:none; font-weight:bold;">👻 aale112</a>
        </div>
        """, unsafe_allow_html=True)
    
    time.sleep(1) # التحديث كل ثانية
