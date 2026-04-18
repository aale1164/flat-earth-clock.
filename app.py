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

# تصميم الواجهة CSS للجوال
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }
    .main-container { text-align: center; color: white; width: 100%; }
    .time-text { font-size: 16vw; font-weight: bold; display: inline-block; margin: 0; }
    .ampm-text { font-size: 6vw; color: #00FF00; vertical-align: super; margin-right: 2px; }
    .date-row { font-size: 5vw; color: #FFA500; font-weight: bold; margin-top: 5px; }
    .prayer-card {
        background: rgba(0,255,0,0.1); padding: 15px; border-radius: 20px;
        border: 2px solid #00FF00; margin: 20px auto; width: 90%; max-width: 350px;
    }
    .countdown { font-size: 10vw; color: #00FF00; font-weight: bold; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# خيارات الأذان
with st.sidebar:
    st.header("🔔 منبه الأذان")
    enable_adhan = st.checkbox("تفعيل التنبيه", value=True)
    voice = st.radio("المؤذن", ["مكي", "مدني"])

audio_links = {
    "مكي": "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_1.mp3",
    "مدني": "https://download.tvquran.com/download/Adhan/TVQuran.com_Adhan_7.mp3"
}

# الموقع
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
                    # تم إصلاح السطر المسبب للخطأ هنا
                    h_val, rem = divmod(diff.seconds, 3600)
                    m_val, s_val = divmod(rem, 60)
                    time_left = f"{h_val:02d}:{m_val:02d}:{s_val:02d}"
                    break
                if curr_full == p_full: play_now = True

            if not next_p_name: next_p_name, time_left = "الفجر", "صلاة الغد"
    except: pass

    with placeholder.container():
        raw_time = now.strftime('%I:%M:%S')
        if raw_time.startswith('0'): raw_time = raw_time[1:]
        ampm = now.strftime('%p')
        
        if play_now and enable_adhan:
            st.markdown(f'<audio src="{audio_links[voice]}" autoplay></audio>', unsafe_allow_html=True)

        content = f"""
            <div class='main-container'>
                <div><span class='time-text'>{raw_time}</span><span class='ampm-text'>{ampm}</span></div>
                <div class='date-row'>{hij_str} | {mil_str}</div>
                <div class='prayer-card'>
                    <p style='font-size:18px; margin-bottom:5px;'>متبقي على صلاة {next_p_name}</p>
                    <div class='countdown'>{time_left}</div>
                </div>
                <div style='margin-top:25px; opacity:0.8; font-size:14px;'>
                    <a href="https://twitter.com/aale1164" target="_blank" style="color:#1DA1F2; text-decoration:none;">𝕏 @aale1164</a> | 
                    <a href="https://www.snapchat.com/add/aale112" target="_blank" style="color:#FFFC00; text-decoration:none;">👻 aale112</a>
                </div>
            </div>
        """
        st.markdown(content, unsafe_allow_html=True)
    
    time.sleep(1)
