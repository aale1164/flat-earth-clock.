import streamlit as st
import pytz
from datetime import datetime, date, timedelta
import requests
from hijri_converter import Gregorian
import json

# إعداد الصفحة
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

# محاولة استيراد المكتبات الاختيارية
try:
    from prayer_times_calculator import PrayerTimesCalculator
    PRAYER_LIB_AVAILABLE = True
except ImportError:
    PRAYER_LIB_AVAILABLE = False

try:
    from streamlit_js_eval import get_geolocation
    GEO_LIB_AVAILABLE = True
except ImportError:
    GEO_LIB_AVAILABLE = False

sa_tz = pytz.timezone('Asia/Riyadh')

# --- دوال مساعدة ---
@st.cache_data(ttl=600)
def fetch_weather_cached(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        return response['current_weather']['temperature']
    except:
        return None

def get_season_data():
    today = date.today()
    y = today.year
    seasons = [
        ('الربيع', 'Spring', date(y, 3, 21), '🌸'),
        ('الصيف', 'Summer', date(y, 6, 21), '☀️'),
        ('الخريف', 'Autumn', date(y, 9, 23), '🍂'),
        ('الشتاء', 'Winter', date(y, 12, 21), '❄️')
    ]
    for ar, en, s_date, icon in seasons:
        if s_date > today:
            return ar, en, (s_date - today).days, icon
    # بعد 21 ديسمبر -> ربيع العام القادم
    next_spring = date(y + 1, 3, 21)
    return 'الربيع', 'Spring', (next_spring - today).days, '🌸'

def get_prayer_times(lat, lon, now):
    sunrise = sunset = "--:--"
    prayer_dict = {}
    if PRAYER_LIB_AVAILABLE:
        try:
            calc = PrayerTimesCalculator(
                latitude=lat,
                longitude=lon,
                calculation_method='makkah',
                date=now.strftime("%Y-%m-%d")
            )
            times = calc.fetch_prayer_times()
            if times:
                sunrise = times.get('Sunrise', '--:--')
                sunset = times.get('Maghrib', '--:--')
                prayer_dict = {
                    'Fajr': times.get('Fajr'),
                    'Dhuhr': times.get('Dhuhr'),
                    'Asr': times.get('Asr'),
                    'Maghrib': times.get('Maghrib'),
                    'Isha': times.get('Isha')
                }
        except:
            pass
    return sunrise, sunset, prayer_dict

# --- الحصول على الإحداثيات ---
lat, lon = 26.32, 43.97  # بريدة
if GEO_LIB_AVAILABLE:
    try:
        loc = get_geolocation()
        if loc and 'coords' in loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
    except:
        pass

# --- تجهيز البيانات الثابتة نسبياً ---
now = datetime.now(sa_tz)
today = now.date()

# التاريخ الهجري
try:
    h = Gregorian.fromdate(today).to_hijri()
    hij_str = f"{h.day}/{h.month}/{h.year} هـ"
except:
    hij_str = "--/--/---- هـ"
mil_str = f"{today.day}/{today.month}/{today.year} M"

# الطقس
temp = fetch_weather_cached(lat, lon)
weather_str = f"{temp}°C" if temp is not None else "--°C"

# أوقات الصلاة
sunrise, sunset, prayer_dict = get_prayer_times(lat, lon, now)

# الفصل
season_ar, season_en, days_left, season_icon = get_season_data()

# --- تمرير البيانات إلى JavaScript عبر JSON ---
prayer_json = json.dumps(prayer_dict, ensure_ascii=False)

# --- التنسيق CSS + JavaScript للتحديث الحي ---
st.markdown(f"""
<style>
    header, footer, .stDeployButton, #MainMenu {{ visibility: hidden !important; height: 0; }}
    .block-container {{ padding: 0 !important; }}
    .stApp {{
        background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
        background-size: 100% 100%;
        background-attachment: fixed;
        direction: rtl;
        font-family: 'Tajawal', sans-serif;
    }}
    .main-layout {{
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100vh;
        justify-content: flex-start;
        padding-top: 4vh;
    }}
    .unified-text {{
        color: #FFFFFF !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
        margin: 0;
        line-height: 1.2;
        text-align: center;
    }}
    .time-val {{ font-size: 14vw; font-weight: 900; }}
    .ampm-val {{ font-size: 4vw; margin-right: 10px; color: #FFA500; }}
    .info-line {{ font-size: 4vw; font-weight: 700; margin-top: 5px; }}
    .eng-sub {{ font-size: 2vw; opacity: 0.8; font-weight: normal; display: block; }}
    .data-bar {{
        display: flex;
        gap: 20px;
        margin-top: 20px;
        background: rgba(255, 255, 255, 0.1);
        padding: 10px 25px;
        border-radius: 50px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .data-item {{ font-size: 2.5vw; font-weight: bold; color: #FFFFFF; text-align: center; line-height: 1.4; }}
    .social-links {{ margin-top: auto; padding-bottom: 40px; display: flex; gap: 15px; }}
    .social-links a {{
        color: white !important; text-decoration: none; font-size: 16px;
        padding: 10px 25px; background: rgba(0,0,0,0.5); border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.2); transition: 0.3s;
    }}
</style>

<div class="main-layout">
    <div class="unified-text time-val">
        <span id="live-time">--:--:--</span>
        <span id="live-ampm" class="ampm-val"></span>
    </div>

    <div class="unified-text info-line">{hij_str} | {mil_str}</div>

    <div class="unified-text info-line" style="color:#00FF00; margin-top:10px;">
        <span id="next-prayer-text">متبقي على --: --:--:--</span>
        <span class="eng-sub" id="next-prayer-eng">Time to --: --:--:--</span>
    </div>

    <div class="data-bar">
        <div class="data-item">🌡️ {weather_str}<br><span style="font-size:1.5vw; font-weight:normal;">Temp</span></div>
        <div class="data-item">☀️ الشروق: {sunrise}<br><span style="font-size:1.5vw; font-weight:normal;">Sunrise</span></div>
        <div class="data-item">🌅 الغروب: {sunset}<br><span style="font-size:1.5vw; font-weight:normal;">Sunset</span></div>
    </div>

    <div class="unified-text info-line" style="margin-top:25px;">
        {season_icon} متبقي على {season_ar}: {days_left} يوم
        <span class="eng-sub">{days_left} days left for {season_en}</span>
    </div>

    <div class="social-links">
        <a href="https://twitter.com/aale1164" target="_blank">𝕏 @aale1164</a>
        <a href="https://www.snapchat.com/add/aale112" target="_blank">👻 aale112</a>
    </div>
</div>

<script>
const prayerTimes = {prayer_json};
const timezone = "Asia/Riyadh";

function updateClock() {{
    const now = new Date();
    // تحويل إلى توقيت الرياض يدوياً (لأن new Date() بتوقيت المتصفح المحلي)
    const options = {{ timeZone: timezone, hour12: false }};
    const formatter = new Intl.DateTimeFormat('en-US', options);
    const parts = formatter.formatToParts(now);
    const dateParts = {{}};
    parts.forEach(p => {{ dateParts[p.type] = p.value; }});
    
    const year = parseInt(dateParts.year);
    const month = parseInt(dateParts.month) - 1;
    const day = parseInt(dateParts.day);
    const hour = parseInt(dateParts.hour);
    const minute = parseInt(dateParts.minute);
    const second = parseInt(dateParts.second);
    
    // عرض الوقت بصيغة 12 ساعة
    let hour12 = hour % 12;
    hour12 = hour12 === 0 ? 12 : hour12;
    const ampmAr = hour >= 12 ? 'م' : 'ص';
    const ampmEn = hour >= 12 ? 'PM' : 'AM';
    const timeStr = `${{hour12}}:${{minute.toString().padStart(2,'0')}}:${{second.toString().padStart(2,'0')}}`;
    document.getElementById('live-time').textContent = timeStr;
    document.getElementById('live-ampm').textContent = `${{ampmAr}} / ${{ampmEn}}`;
    
    // حساب الصلاة القادمة
    const prayers = [
        {{ nameAr: 'الفجر', nameEn: 'Fajr', time: prayerTimes.Fajr }},
        {{ nameAr: 'الظهر', nameEn: 'Dhuhr', time: prayerTimes.Dhuhr }},
        {{ nameAr: 'العصر', nameEn: 'Asr', time: prayerTimes.Asr }},
        {{ nameAr: 'المغرب', nameEn: 'Maghrib', time: prayerTimes.Maghrib }},
        {{ nameAr: 'العشاء', nameEn: 'Isha', time: prayerTimes.Isha }}
    ];
    
    const currentTimeStr = `${{hour.toString().padStart(2,'0')}}:${{minute.toString().padStart(2,'0')}}`;
    let nextPrayer = null;
    for (let p of prayers) {{
        if (p.time && p.time > currentTimeStr) {{
            nextPrayer = p;
            break;
        }}
    }}
    if (!nextPrayer) {{
        // بعد العشاء -> الفجر غداً
        nextPrayer = prayers[0];
    }}
    
    if (nextPrayer && nextPrayer.time) {{
        // حساب الوقت المتبقي
        const [pHour, pMinute] = nextPrayer.time.split(':').map(Number);
        let prayerDate = new Date(year, month, day, pHour, pMinute, 0);
        if (nextPrayer === prayers[0] && currentTimeStr >= prayers[prayers.length-1].time) {{
            // الفجر لليوم التالي
            prayerDate.setDate(prayerDate.getDate() + 1);
        }}
        const diffMs = prayerDate - now;
        const diffSec = Math.floor(diffMs / 1000);
        const hLeft = Math.floor(diffSec / 3600);
        const mLeft = Math.floor((diffSec % 3600) / 60);
        const sLeft = diffSec % 60;
        const timeLeft = `${{hLeft.toString().padStart(2,'0')}}:${{mLeft.toString().padStart(2,'0')}}:${{sLeft.toString().padStart(2,'0')}}`;
        
        document.getElementById('next-prayer-text').textContent = `متبقي على ${{nextPrayer.nameAr}}: ${{timeLeft}}`;
        document.getElementById('next-prayer-eng').textContent = `Time to ${{nextPrayer.nameEn}}: ${{timeLeft}}`;
    }} else {{
        document.getElementById('next-prayer-text').textContent = `متبقي على --: --:--:--`;
        document.getElementById('next-prayer-eng').textContent = `Time to --: --:--:--`;
    }}
}}

// التحديث كل ثانية
updateClock();
setInterval(updateClock, 1000);
</script>
""", unsafe_allow_html=True)
