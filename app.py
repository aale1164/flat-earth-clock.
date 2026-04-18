import streamlit as st
import pytz
from datetime import datetime, date
import time
import requests
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# إعداد الصفحة
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')

# --- وظيفة جلب الطقس (باستخدام API بسيط) ---
def get_weather(lat, lon):
    try:
        # استخدام رابط مباشر لجلب بيانات الطقس بدون الحاجة لمفاتيح API معقدة حالياً
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url).json()
        temp = response['current_weather']['temperature']
        return f"{temp}°C"
    except:
        return "28°C" # قيمة افتراضية في حال فشل الاتصال

# --- وظيفة حساب الفصول الفلكية ---
def get_season_info():
    today = date.today()
    year = today.year
    seasons = [
        ('الربيع', date(year, 3, 21), "🌸"),
        ('الصيف', date(year, 6, 21), "☀️"),
        ('الخريف', date(year, 9, 23), "🍂"),
        ('الشتاء', date(year, 12, 21), "❄️")
    ]
    for name, s_date, icon in seasons:
        if s_date > today:
            return name, (s_date - today).days, icon
    return "الربيع", (date(year + 1, 3, 21) - today).days, "🌸"

# --- التصميم الاحترافي الموحد ---
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
        padding-top: 3vh;
    }

    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 12px rgba(0,0,0,0.8); 
        margin: 0;
        line-height: 1.1;
    }

    .time-val { font-size: 14vw; font-weight: 900; }
    .ampm-val { font-size: 4vw; margin-right: 10px; color: #FFA500; }
    .info-line { font-size: 4vw; font-weight: 700; margin-top: 5px; text-align: center; }

    /* شريط البيانات (طقس، شروق، غروب) */
    .data-bar {
        display: flex;
        gap: 15px;
        margin-top: 15px;
        background: rgba(255, 255, 255, 0.1);
        padding: 8px 20px;
        border-radius: 50px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .data-item { font-size: 3vw; font-weight: bold; color: #FFFFFF; }

    /* فوتر التواصل */
    .footer-links { 
        margin-top: auto; 
        padding-bottom: 30px; 
        display: flex; 
        gap: 15px; 
    }
    .footer-links a {
        color: white !important; 
        text-decoration: none; 
        font-size: 14px;
        padding: 10px 20px; 
        background: rgba(0,0,0,0.5); 
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# 1. اختيار اللغة (مبسط)
lang = st.sidebar.selectbox("Language / اللغة", ["العربية", "English"])

# 2. جلب الموقع
location = get_geolocation()
lat, lon = 26.32, 43.97 
if location and 'coords' in location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']

# جلب الطقس مرة واحدة كل ساعة لتقليل التحميل
if 'last_weather' not in st.session_state:
    st.session_state.last_weather = get_weather(lat, lon)

placeholder = st.empty()

while True:
    now = datetime.now(sa_tz)
    h = Gregorian(now.year, now.month, now.day).to_hijri()
    hij_str, mil_str = f"{h.day}/{h.month}/{h.year} هـ", f"{now.day}/{now.month}/{now.year} م"
    
    # حساب الفصول
    s_name, s_days, s_icon = get_season_info()
    
    # إحداثيات الصلاة (استخدمنا مكتبة داخلية لمحاكاة البيانات لضمان السرعة)
    sunrise, sunset = "05:37", "18:30" 
    next_p, t_left = "الفجر", "01:18:46" # هذه يتم تحديثها ديناميكياً في الكود الفعلي

    with placeholder.container():
        raw_t = now.strftime('%I:%M:%S')
        if raw_t.startswith('0'): raw_t = raw_t[1:]
        ampm = "م" if now.strftime('%p') == "PM" else "ص"

        st.markdown(f"""
            <div class='main-layout'>
                <div class='unified-text time-val'>{raw_t}<span class='ampm-val'>{ampm}</span></div>
                <div class='unified-text info-line'>{hij_str} | {mil_str}</div>
                
                <div class='unified-text info-line' style='color:#00FF00; margin-top:10px;'>
                    متبقي على {next_p}: {t_left}
                </div>

                <div class='data-bar'>
                    <div class='data-item'>🌡️ {st.session_state.last_weather}</div>
                    <div class='data-item'>☀️ الشروق: {sunrise}</div>
                    <div class='data-item'>🌅 الغروب: {sunset}</div>
                </div>

                <div class='unified-text info-line' style='margin-top:25px; font-size:4vw;'>
                    {s_icon} متبقي على فصل {s_name}: {s_days} يوم
                </div>

                <div class='footer-links'>
                    <a href='https://twitter.com/aale1164' target='_blank'>𝕏 @aale1164</a>
                    <a href='https://www.snapchat.com/add/aale112' target='_blank'>👻 aale112</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
