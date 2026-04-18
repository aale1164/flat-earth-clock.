import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")

# توقيت السعودية ورابط الأذان
sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- تصميم CSS متكامل (واضح وفخم للجوال) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@800&family=Poppins:wght@600&display=swap');
    
    /* إعدادات الخلفية: إضاءة أكثر ووضوح للحرم */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; 
        background-position: center;
        background-attachment: fixed;
        direction: rtl; 
        font-family: 'Tajawal', sans-serif;
    }

    .main-container { text-align: center; color: white; width: 100%; padding-top: 5px; }

    /* الساعة: بيضاء، واضحة، ضخمة */
    .time-text { 
        font-size: 17vw; 
        font-weight: 800; 
        color: #FFFFFF; 
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5); /* لإبراز النص */
        margin: 0; 
    }
    
    .ampm-text { 
        font-size: 6vw; 
        color: #00FF00; /* أخضر نيون للـ AM/PM */
        vertical-align: super; 
        font-weight: bold;
    }

    /* التاريخ: برتقالي، واضح، عريض */
    .date-row { 
        font-size: 5.5vw; 
        color: #FFA500; 
        font-weight: 800; 
        margin-top: -5px;
        letter-spacing: 1px;
    }

    /* بطاقة الصلاة القادمة: خضراء، غير شفافة، بارزة */
    .prayer-card {
        background: #FFFFFF; /* خلفية بيضاء نقية للوضوح */
        padding: 15px; 
        border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3); /* ظل فخم */
        margin: 25px auto 15px auto; 
        width: 92%; 
        max-width: 360px;
        border-bottom: 5px solid #00AA00; /* خط أخضر بالأسفل */
    }

    .prayer-label { font-size: 20px; color: #333333; font-weight: bold; margin-bottom: 0px; }
    
    /* العداد: أخضر زمردي، واضح جداً */
    .countdown { 
        font-size: 11vw; 
        color: #00AA00; 
        font-weight: bold; 
        font-family: 'Courier New', monospace; 
        letter-spacing: -2px;
    }

    /* الفوتر */
    .footer { margin-top: 25px; opacity: 1; font-size: 15px; color: #FFFFFF; font-weight: bold; }
    .footer a { color: #FFFFFF !important; text-decoration: none; }
    
    /* تحسين شكل الزر (طراز عصري، واضح جداً) */
    .stCheckbox label {
        color: #FFFFFF !important; 
        font-weight: bold !important; 
        font-size: 18px !important;
        background: #00AA00; /* أخضر زمردي ثابت */
        padding: 10px 25px;
        border-radius: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .stCheckbox label:hover { background: #00CC00; }
</style>
""", unsafe_allow_html=True)

# الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# --- هذا الجزء خارج الحلقة لضمان ثبات الزر ---
# وضع الزر في منتصف الواجهة
col1, col2, col3 = st.columns([1, 8, 1])
with col2:
    adhan_on = st.toggle("🔔 أذان الحرم المكي", value=True, key="fixed_mecca_toggle")
# ---------------------------------------------

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    next_p_name, time_left, play_now = "الفجر", "00:00:00", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr_f = now.strftime("%H:%M:%S")
            for name, p_t in p_list:
                p_f = f"{p_t}:00"
                if p_f > curr_f:
                    next_p_name = name
                    target = sa_tz.localize(datetime.strptime(p_f, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day))
                    diff = target - now
                    h_v, rem = divmod(diff.seconds, 3600); m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    break
                if curr_f == p_f: play_now = True
    except: pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')
        
        if play_now and adhan_on:
            st.markdown(f'<audio src="{ADHAN_URL}" autoplay></audio>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class='main-container'>
                <div><span class='time-text'>{raw_t}</span><span class='ampm-text'>{ampm}</span></div>
