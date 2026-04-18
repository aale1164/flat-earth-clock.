import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد المكتبة بأمان
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="centered")

# إعدادات الوقت
sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- تصميم "الاندماج الكامل": لا واجهة، فقط خلفية ونصوص ---
st.markdown("""
<style>
    /* حذف كل زوائد ستريمليت */
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.block-container {padding-top: 0rem;}
    
    .stApp {
        /* إضاءة الخلفية كاملة (100%) لبروز الصورة */
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; 
        background-position: center;
        background-attachment: fixed;
        direction: rtl; 
        font-family: 'Tajawal', sans-serif;
    }

    /* الحاوية للنصوص فقط */
    .content-wrapper {
        text-align: center;
        background: transparent;
        margin-top: 10vh;
    }

    /* الساعة: مدمجة مع الخلفية بتوهج بسيط */
    .time-val { 
        font-size: 25vw; 
        font-weight: 900; 
        color: #FFFFFF; 
        line-height: 0.8; 
        text-shadow: 0 0 20px rgba(0,0,0,1), 0 0 10px rgba(255,255,255,0.3);
        margin: 0; 
    }
    .ampm-val { font-size: 8vw; color: #00FF00; font-weight: bold; }

    /* التاريخ: لون مشع بسيط */
    .date-val { 
        font-size: 7vw; 
        color: #FFA500; 
        font-weight: 800; 
        margin: 15px 0; 
        text-shadow: 2px 2px 10px rgba(0,0,0,1);
    }

    /* العداد التنازلي: عائم فوق الأرض */
    .prayer-label-val { 
        font-size: 30px; 
        color: #FFFFFF; 
        font-weight: 900; 
        text-shadow: 2px 2px 10px rgba(0,0,0,1);
        margin-top: 40px;
    }
    .timer-val { 
        font-size: 18vw; 
        color: #00FF00; 
        font-weight: 900; 
        font-family: 'Courier New', monospace; 
        text-shadow: 0 0 20px rgba(0,0,0,1), 0 0 15px rgba(0,255,0,0.2);
    }

    /* روابط التواصل */
    .social-btns { margin-top: 60px; }
    .social-btns a { 
        color: white !important; 
        text-decoration: none; 
        font-weight: bold; 
        padding: 10px 20px; 
        background: rgba(0,0,0,0.3); /* شفافية عالية جداً للزر */
        border-radius: 50px;
        margin: 5px; 
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* تنسيق زر الأذان ليكون أقل حدة */
    .stToggle {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. جلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# 2. زر التنبيه (شفاف)
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 8, 1])
with c2:
    adhan_on = st.toggle("🔔 أذان الحرم المكي الشريف", value=True, key="pure_bg_toggle")

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

        # عرض النصوص مباشرة فوق الخلفية
        st.markdown(f"""
            <div class='content-wrapper'>
                <div class='time-val'>{raw_t}<span
