import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد مكتبة الصلاة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")

# توقيت السعودية
sa_tz = pytz.timezone('Asia/Riyadh')

# تصميم الواجهة CSS المخصص للجوال
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    
    /* إعدادات الشاشة الأساسية */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }

    .main-container { 
        text-align: center; 
        color: white; 
        padding: 5px;
        width: 100%;
    }

    /* حجم الساعة للجوال */
    .time-text { 
        font-size: 16vw; /* حجم متجاوب مع عرض الشاشة */
        font-weight: bold; 
        display: inline-block; 
        margin: 0; 
        color: #fff;
    }
    
    .ampm-text { 
        font-size: 6vw; 
        color: #00FF00; 
        vertical-align: super; 
        margin-right: 2px;
    }

    .date-row { 
        font-size: 5vw; 
        color: #FFA500; 
        font-weight: bold; 
        margin-top: 5px;
        letter-spacing: 1px;
    }

    /* بطاقة الصلاة القادمة */
    .prayer-card {
        background: rgba(0,255,0,0.1); 
        padding: 15px; 
        border-radius: 20px;
        border: 2px solid #00FF00; 
        margin: 20px auto; 
        width: 90%; /* عرض مناسب للجوال */
        max-width: 350px;
    }

    .prayer-label { font-size: 18px; margin-bottom: 5px; color: #eee; }
    
    .countdown { 
        font-size: 10vw; 
        color: #00FF00; 
        font-weight: bold; 
        font-family: 'Courier New', monospace; 
    }

    .footer { margin-top: 25px; opacity: 0.8; font-size: 14px; }
    
    /* إخفاء القائمة الجانبية في الجوال لتوسيع المساحة */
    [data-testid="stSidebar"] { width: 250px; }
</style>
""", unsafe_allow_html=True)

# خيارات الأذان في الجانب
with st.sidebar:
    st.header("🔔 منبه الأذان")
    enable_adhan = st.checkbox("تفعيل التنبيه", value=True)
    voice = st.radio("المؤذن", ["مكي", "مدني"])
    # ملاحظة: يمكنك إضافة ملفات الصوت الخاصة بك لاحقاً

audio_links = {
    "مكي": "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3",
    "مدني": "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_7.mp3"
}

# طلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    
    hij_str = f"{h.day}/{h.month}/{h.year} هـ"
    mil_str = f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr_full = now.strftime("%H:%M:%S")
            
            for name, p_t in p_list:
                p_full = f"{p_t}:00"
                if p_full > curr_full:
                    next_p_name = name
                    target = sa_tz.localize(datetime.strptime(p_full, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    m, s = divmod(diff.seconds, 60); h_val, m = divmod(m, 60)
                    time_left = f"{h_val:02d}:{m:02d}:{s:02d}"
                    break
                if curr_full == p_full: play_now = True

            if not next_p_name: next_p_name, time_left = "الفجر", "صلاة الغد"
    except: pass

    with placeholder.container():
        raw_time =
