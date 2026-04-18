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

# تصميم الواجهة CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: cover; background-position: center; background-attachment: fixed;
        direction: rtl; font-family: 'Tajawal', sans-serif;
    }
    .main-container { text-align: center; color: white; padding-top: 10px; }
    .time-text { font-size: 75px; font-weight: bold; display: inline-block; margin: 0; }
    .ampm-text { font-size: 25px; color: #00FF00; vertical-align: super; margin-right: 5px; }
    .date-row { font-size: 22px; color: #FFA500; font-weight: bold; margin-top: 5px; }
    .prayer-card {
        background: rgba(0,255,0,0.1); padding: 15px; border-radius: 15px;
        border: 2px solid #00FF00; margin: 15px auto; max-width: 400px;
    }
    .countdown { font-size: 40px; color: #00FF00; font-weight: bold; font-family: 'Courier New', monospace; }
    .settings-box { background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; margin-top: 10px; border: 1px solid #444; }
</style>
""", unsafe_allow_html=True)

# شريط جانبي أو خيارات المنبه
with st.sidebar:
    st.header("🔔 إعدادات الأذان")
    enable_adhan = st.checkbox("تفعيل منبه الأذان")
    voice_type = st.selectbox("اختر المؤذن", ["مكي", "مدني"])
    length_type = st.selectbox("نوع التنبيه", ["أذان كامل", "تكبيرات فقط"])

# روابط ملفات الصوت (روابط تجريبية - يمكنك استبدالها بروابط مباشرة لملفات mp3)
# ملاحظة: يجب أن تكون الروابط مباشرة لملف mp3
sounds = {
    "مكي_كامل": "https://www.islamcan.com/common/adhan/makkah.mp3",
    "مدني_كامل": "https://www.islamcan.com/common/adhan/madina.mp3",
    "مكي_تكبيرات": "https://www.islamcan.com/common/adhan/makkah.mp3", # هنا نستخدم نفس الملف كمثال
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
    
    next_p_name, time_left, is_adhan_time = "", "جاري الحساب...", False
    
    try:
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method='makkah', date=now.strftime("%Y-%m-%d"))
        times = calc.fetch_prayer_times()
        if times:
            p_list = [('الفجر', times['Fajr']), ('الظهر', times['Dhuhr']), ('العصر', times['Asr']), ('المغرب', times['Maghrib']), ('العشاء', times['Isha'])]
            curr_str = now.strftime("%H:%M") # للمقارنة بالدقائق
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
                
                # التحقق إذا حان وقت الأذان الآن
                if curr_full == p_full and enable_adhan:
                    is_adhan_time = True
            
            if not next_p_name: next_p_name, time_left = "الفجر", "صلاة الغد"
    except: pass

    with placeholder.container():
        raw_time = now.strftime('%I:%M:%S'); ampm = now.strftime('%p')
        if raw_time.startswith('0'): raw_time = raw_time[1:]
        
        # تشغيل الصوت إذا حان الوقت
        if is_adhan_time:
            sound_url = sounds.get(f"{voice_type}_{'كامل' if length_type == 'أذان كامل' else 'تكبيرات'}", sounds["مكي_كامل"])
            st.markdown(f'<audio src="{sound_url}" autoplay></audio>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class='main-container'>
                <div><span class='time-text'>{raw_time}</span><span class='ampm-text'>{ampm}</span></div>
                <div class='date-row'>{hij_str} | {mil_str}</div>
                <div class='prayer-card'>
                    <p style='font-size:18px; margin-bottom:5px;'>متبقي على صلاة {next_p_name}</p>
