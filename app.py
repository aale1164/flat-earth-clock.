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

# تصميم الواجهة CSS للجوال مع تنسيق المنبه الجديد
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }
    .main-container { text-align: center; color: white; width: 100%; padding-top: 10px; }
    .time-text { font-size: 16vw; font-weight: bold; display: inline-block; margin: 0; }
    .ampm-text { font-size: 6vw; color: #00FF00; vertical-align: super; margin-right: 2px; }
    .date-row { font-size: 5vw; color: #FFA500; font-weight: bold; margin-top: 5px; }
    
    /* مربع العداد التنازلي */
    .prayer-card {
        background: rgba(0,255,0,0.1); padding: 15px; border-radius: 20px;
        border: 2px solid #00FF00; margin: 20px auto 10px auto; width: 90%; max-width: 350px;
    }
    .countdown { font-size: 10vw; color: #00FF00; font-weight: bold; font-family: 'Courier New', monospace; }
    
    /* تنسيق المنبه الجديد تحت المربع */
    .alarm-status {
        background: rgba(255, 255, 255, 0.07);
        padding: 8px 15px;
        border-radius: 30px;
        display: inline-block;
        font-size: 14px;
        color: #ddd;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
    }
    .alarm-icon { color: #00FF00; margin-left: 5px; font-weight: bold; }
    
    .footer { margin-top: 20px; opacity: 0.8; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# خيارات الأذان في الجانب (للتغيير)
with st.sidebar:
    st.header("⚙️ إعدادات المنبه")
    enable_adhan = st.checkbox("تفعيل صوت الأذان", value=True)
    voice = st.radio("صوت المؤذن", ["مكي", "مدني"])

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
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
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
                    h_val, rem = divmod(diff.seconds, 3600)
                    m_val, s_val = divmod(rem, 60)
                    time_left = f"{h_val:02d}:{m_val:02d}:{s_val:02d}"
                    break
                if curr_full == p_full: play_now = True
            if not next_p_name: next_p_name, time_left = "الفجر", "صلاة الغد"
    except: pass

    with placeholder.container():
        raw_time = now.strftime('%I:%M:%S'); ampm = now.strftime('%p')
        if raw_time.startswith('0'): raw_time = raw_time[1:]
        
        # تشغيل الأذان
        if play_now and enable_adhan:
            st.markdown(f'<audio src="{audio_links[voice]}" autoplay></audio>', unsafe_allow_html=True)

        # الحالة النصية للمنبه
        alarm_text = f"🔔 المنبه: أذان {voice}" if enable_adhan else "🔕 المنبه: متوقف"

        st.markdown(f"""
            <div class='main-container'>
                <div><span class='time-text'>{raw_time}</span><span class='ampm-text'>{ampm}</span></div>
                <div class='date-row'>{hij_str} | {mil_str}</div>
                
                <div class='prayer-card'>
                    <p style='font-size:18px; margin-bottom:5px;'>متبقي على صلاة {next_p_name}</p>
                    <div class='countdown'>{time_left}</div>
                </div>
                
                <div class='alarm-status'>
                    <span class='alarm-icon'>{'●' if enable_adhan else '○'}</span> {alarm_text}
                </div>

                <div class='footer'>
                    <a href="https://twitter.com/aale1164" target="_blank" style="color:#1DA1F2; text-decoration:none; font-weight:bold;">𝕏 @aale1164</a> | 
                    <a href="https://www.snapchat.com/add/aale112" target="_blank" style="color:#FFFC00; text-decoration:none; font-weight:bold;">👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    time.sleep(1)
