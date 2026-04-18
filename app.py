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

# إعداد الصفحة لإزالة أي خطوط بيضاء علوية
st.set_page_config(page_title="ساعة الصلاة - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# --- التصميم النهائي: معالجة نصوص الـ HTML وتوحيد الألوان ---
st.markdown("""
<style>
    /* إخفاء تام للعناصر العلوية والخطوط البيضاء */
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
        padding-top: 3vh;
    }

    /* ستايل النصوص الموحد (أبيض بظل شفاف) */
    .unified-style {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.6); 
        margin: 0;
        line-height: 1.2;
        text-align: center;
    }

    .time-main { font-size: 16vw; font-weight: 900; }
    .ampm-mini { font-size: 5vw; margin-right: 10px; color: #FFFFFF !important; }
    .date-mini { font-size: 5vw; font-weight: 700; margin-top: 5px; }

    /* حاوية الأذان في المنتصف */
    .adhan-container {
        margin: 12vh 0 5vh 0;
        padding: 10px 25px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* متبقي على الصلاة (نصوص موحدة) */
    .label-mini { font-size: 6.5vw; font-weight: 800; margin-top: 20px; }
    .timer-mini { font-size: 15vw; font-weight: 900; font-family: 'Courier New', monospace; }

    .social-footer { margin-top: auto; padding-bottom: 20px; }
    .social-footer a {
        color: white !important; text-decoration: none; font-size: 14px;
        padding: 8px 18px; background: rgba(0,0,0,0.3); border-radius: 20px;
        margin: 5px; border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# جلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# استخدام الـ Placeholder لتجنب أخطاء تكرار العناصر (Duplicate Key)
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

        # بناء الواجهة بدون تداخل نصوص الـ HTML
        st.markdown(f"""
            <div class='main-layout'>
                <div class='unified-style time-main'>{raw_t}<span class='ampm-mini'>{ampm}</span></div>
                <div class='unified-style date-mini'>{hij_str} | {mil_str}</div>
                
                <div class='adhan-container'>
                    <div style='color:white; font-size:18px; font-weight:bold;'>🔔 أذان الحرم المكي الشريف</div>
                </div>

                <div class='unified-style label-mini'>متبقي على صلاة {next_p_name}</div>
                <div class='unified-style timer-mini'>{time_left}</div>

                <div class='social-footer'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # زر التفعيل في الأسفل لتجنب الخطأ البرمجي
        adhan_on = st.toggle("تفعيل صوت الأذان", value=True, key="unique_adhan_key")
        
        if play_now and adhan_on:
            st.markdown(f'<audio src="{ADHAN_URL}" autoplay></audio>', unsafe_allow_html=True)

    time.sleep(1)
