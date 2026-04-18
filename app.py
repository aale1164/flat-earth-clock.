import streamlit as st
import pytz
from datetime import datetime
import time
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# استيراد مكتبة أوقات الصلاة
try:
    from prayer_times_calculator import PrayerTimesCalculator
except ImportError:
    pass

# إعداد الصفحة لإزالة الخطوط والزحام
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- التصميم الاحترافي الموحد (أبيض بظلال شفافة) ---
st.markdown("""
<style>
    header, footer, .stDeployButton, #MainMenu { visibility: hidden !important; height: 0; }
    .block-container { padding: 0 !important; }

    .stApp {
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: 100% 100%;
        background-attachment: fixed;
        direction: rtl;
        font-family: 'Tajawal', sans-serif;
    }

    .main-layout {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100vh;
        justify-content: flex-start;
        padding-top: 2vh;
    }

    /* ستايل النصوص الموحد (أبيض بظل مائي شفاف) */
    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 12px rgba(0,0,0,0.4); 
        margin: 0;
        line-height: 1.1;
        text-align: center;
    }

    /* الساعة فوق القمر ومصغرة */
    .time-top { font-size: 14vw; font-weight: 900; }
    .ampm-top { font-size: 4vw; margin-right: 8px; }

    /* التاريخ تحت الساعة مباشرة وأصغر */
    .date-sub { font-size: 4.5vw; font-weight: 700; margin-top: 5px; }

    /* حاوية الأذان (المنبه) في منتصف الشاشة */
    .adhan-center-box {
        margin: 15vh 0 5vh 0;
        background: rgba(255, 255, 255, 0.08);
        padding: 8px 25px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    /* متبقي على الصلاة في الأسفل */
    .prayer-label { font-size: 6vw; font-weight: 800; margin-top: 20px; }
    .prayer-timer { font-size: 12vw; font-weight: 900; font-family: 'Courier New', monospace; }

    /* التحكم في زر التبديل */
    .stToggle { position: fixed; bottom: 80px; left: 20px; z-index: 1000; }
</style>
""", unsafe_allow_html=True)

# 1. حل مشكلة Duplicate Key: تعريف الزر خارج حلقة التحديث
if 'adhan_status' not in st.session_state:
    st.session_state.adhan_status = True

# وضع الزر في مكان جانبي أو ثابت لمنع تكراره برمجياً
with st.sidebar:
    st.session_state.adhan_status = st.toggle("تفعيل الأذان", value=st.session_state.adhan_status)

# 2. جلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# 3. حاوية العرض المتجددة
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

        # بناء الواجهة بتنسيق نظيف لمنع ظهور أكواد الـ HTML
        st.markdown(f"""
            <div class='main-layout'>
                <div class='unified-text time-top'>{raw_t}<span class='ampm-top'>{ampm}</span></div>
                <div class='unified-text date-sub'>{hij_str} | {mil_str}</div>
                
                <div class='adhan-center-box'>
                    <div style='color:white; font-size:18px; font-weight:bold;'>🔔 أذان الحرم المكي الشريف</div>
                </div>

                <div class='unified-text prayer-label'>متبقي على صلاة {next_p_name}</div>
                <div class='unified-text prayer-timer'>{time_left}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if play_now and st.session_state.adhan_status:
            st.markdown(f'<audio src="{ADHAN_URL}" autoplay></audio>', unsafe_allow_html=True)

    time.sleep(1)
