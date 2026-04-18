import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# محاولة استيراد مكتبة الصلاة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الرواتب والصلاة - aale1164", layout="centered")

# توقيت السعودية
sa_tz = pytz.timezone('Asia/Riyadh')
months = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

# طلب الموقع الجغرافي من المتصفح
location = get_geolocation()

# إحداثيات افتراضية (القصيم) في حال لم يتوفر الموقع
lat, lon = 26.32, 43.97 
location_name = "القصيم (افتراضي)"

if location:
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    location_name = "موقعك الحالي"

# تصميم الواجهة CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; background-attachment: fixed;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }}
    .card {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 20px; background: rgba(255,255,255,0.08); border-radius: 12px;
        margin: 8px 0; border-right: 5px solid #00FF00;
    }}
    .val {{ font-size: 22px; color: #00FF00; font-weight: bold; }}
    .social {{ text-align: center; background: rgba(0,0,0,0.6); padding: 15px; border-radius: 15px; margin-top: 20px; }}
</style>
""", unsafe_allow_html=True)

def get_days(day, now):
    if now.day <= day: return day - now.day
    import calendar
    return (calendar.monthrange(now.year, now.month)[1] - now.day) + day

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    # حساب مواقيت الصلاة بناءً على الموقع
    prayers = None
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        prayers = calc.fetch_prayer_times()
    except:
        pass

    with placeholder.container():
        # عرض الساعة بنظام 12 ساعة مع الثواني (I تعني 12 ساعة)
        time_str = now.strftime('%I:%M:%S %p').replace('AM','صباحاً').replace('PM','مساءً')
        if time_str.startswith('0'): time_str = time_str[1:] # إزالة الصفر في البداية لتجميل الشكل

        st.markdown(f"<h1 style='text-align:center; color:#00FF00; font-size:65px; margin-bottom:0;'>{time_str}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:#FFA500; margin-top:0;'>{h.day} {months[h.month-1]} {h.year} هـ</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#aaa;'>📍 {location_name}</p>", unsafe_allow_html=True)

        st.divider()

        # الرواتب
        st.markdown("### 💰 المتبقي على الرواتب")
        st.markdown(f'<div class="card"><span>رواتب الموظفين</span><span class="val">{get_days(27, now)} يوم</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card" style="border-right-color:#00ACEE;"><span>حساب المواطن</span><span class="val" style="color:#00ACEE;">{get_days(10, now)} يوم</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card" style="border-right-color:#FFA500;"><span>الضمان والتقاعد</span><span class="val" style="color:#FFA500;">{get_days(1, now)} يوم</span></div>', unsafe_allow_html=True)

        # الصلاة
        if prayers:
            st.divider()
            st.markdown(f"### 🕋 مواقيت الصلاة")
            p_list = [('الفجر', 'Fajr'), ('الظهر', 'Dhuhr'), ('العصر', 'Asr'), ('المغرب', 'Maghrib'), ('العشاء', 'Isha')]
            for p_ar, p_en in p_list:
                st.markdown(f'<div class="card" style="border-right-color:#eee;"><span>صلاة {p_ar}</span><span class="val" style="color:#eee;">{prayers[p_en]}</span></div>', unsafe_allow_html=True)

        # التواصل
        st.markdown(f"""
        <div class="social">
            <a href="https://twitter.com/aale1164" style="color:#1DA1F2; text-decoration:none; font-weight:bold; font-size:18px;">𝕏 @aale1164</a>
            <div style="margin:8px;"></div>
            <a href="https://www.snapchat.com/add/aale112" style="color:#FFFC00; text-decoration:none; font-weight:bold; font-size:18px;">👻 aale112</a>
        </div>
        """, unsafe_allow_html=True)
    
    time.sleep(1)
