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

# إعدادات الوقت والرابط
sa_tz = pytz.timezone('Asia/Riyadh')
ADHAN_URL = "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3"

# تصميم CSS: إضاءة عالية، ألوان واضحة، وزر بارز
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@800&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; background-attachment: fixed;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }

    .main-container { text-align: center; color: white; width: 100%; }

    /* الساعة باللون الأبيض الناصع مع ظل لإبرازها */
    .time-text { 
        font-size: 17vw; font-weight: 800; color: #FFFFFF; 
        text-shadow: 3px 3px 12px rgba(0,0,0,0.8); margin: 0; 
    }
    
    .ampm-text { font-size: 6vw; color: #00FF00; vertical-align: super; font-weight: bold; }

    /* التاريخ باللون البرتقالي المشع */
    .date-row { font-size: 5.5vw; color: #FFA500; font-weight: 800; margin-top: -5px; }

    /* بطاقة الصلاة: خلفية بيضاء صلبة (غير شفافة) لضمان الوضوح */
    .prayer-card {
        background: #FFFFFF; padding: 18px; border-radius: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); margin: 25px auto; 
        width: 92%; max-width: 360px; border-bottom: 6px solid #008800;
    }

    .prayer-label { font-size: 22px; color: #222222; font-weight: bold; margin: 0; }
    
    /* العداد بلون أخضر زمردي غامق */
    .countdown { 
        font-size: 11vw; color: #008800; font-weight: bold; 
        font-family: 'Courier New', monospace; letter-spacing: -1px;
    }

    .footer { margin-top: 30px; font-size: 16px; font-weight: bold; }
    .footer a { color: #FFFFFF !important; text-decoration: none; border-bottom: 2px solid #00FF00; }
</style>
""", unsafe_allow_html=True)

# الحصول على الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# زر أذان الحرم المكي - بارز جداً وغير شفاف
st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 10, 1])
with col2:
    adhan_on = st.toggle("🔔 أذان الحرم المكي الشريف", value=True, key="mecca_adhan_toggle")

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
                    h_v, rem = divmod(diff.seconds, 3600)
                    m_v, s_v = divmod(rem, 60)
                    time_left = f"{h_v:02d}:{m_v:02d}:{s_v:02d}"
                    break
                if curr_f == p_f:
                    play_now = True
    except:
        pass

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = now.strftime('%p')
        
        # تشغيل الصوت
        if play_now and adhan_on:
            st.markdown(f'<audio src="{ADHAN_URL}" autoplay></audio>', unsafe_allow_html=True)

        # الواجهة
        st.markdown(f"""
            <div class='main-container'>
                <div class='time-text'>{raw_t}<span class='ampm-text'>{ampm}</span></div>
                <div class='date-row'>{hij_str} | {mil_str}</div>
                <div class='prayer-card'>
                    <p class='prayer-label'>متبقي على صلاة {next_p_name}</p>
                    <div class='countdown'>{time_left}</div>
                </div>
                <div class='footer'>
                    <a href="https://twitter.com/aale1164" target="_blank">𝕏 @aale1164</a> | 
                    <a href="https://www.snapchat.com/add/aale112" target="_blank">👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    time.sleep(1)
