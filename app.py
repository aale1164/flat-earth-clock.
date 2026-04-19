import streamlit as st
import streamlit.components.v1 as components
import pytz
from datetime import datetime, date
import requests
from hijri_converter import Gregorian
import json

# 1. إعداد الصفحة الأساسي
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

# محاولة استيراد المكتبات مع معالجة الأخطاء بصمت
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

# --- وظائف معالجة البيانات ---

@st.cache_data(ttl=3600)  # تحديث الطقس كل ساعة لتوفير البيانات
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
    return 'الربيع', 'Spring', (date(y + 1, 3, 21) - today).days, '🌸'

def get_prayer_times(lat, lon, now):
    sunrise = sunset = "--:--"
    prayer_dict = {}
    if PRAYER_LIB_AVAILABLE:
        try:
            calc = PrayerTimesCalculator(lat, lon, 'makkah', now.strftime("%Y-%m-%d"))
            times = calc.fetch_prayer_times()
            if times:
                sunrise = times.get('Sunrise', '--:--')
                sunset = times.get('Maghrib', '--:--')
                prayer_dict = {k: v for k, v in times.items() if k in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']}
        except: pass
    return sunrise, sunset, prayer_dict

# --- الحصول على الموقع والبيانات ---
lat, lon = 26.32, 43.97  # افتراضي القصيم
if GEO_LIB_AVAILABLE:
    try:
        loc = get_geolocation()
        if loc and 'coords' in loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    except: pass

now = datetime.now(sa_tz)
try:
    h = Gregorian.fromdate(now.date()).to_hijri()
    hij_str = f"{h.day}/{h.month}/{h.year} هـ"
except:
    hij_str = "--/--/---- هـ"

mil_str = f"{now.day}/{now.month}/{now.year} M"
temp_val = fetch_weather_cached(lat, lon)
weather_str = f"{temp_val}°C" if temp_val is not None else "--°C"
sunrise, sunset, prayer_dict = get_prayer_times(lat, lon, now)
season_ar, season_en, days_left, season_icon = get_season_data()
prayer_json = json.dumps(prayer_dict)

# --- الواجهة البرمجية (HTML/JS/CSS) ---
html_code = f"""
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0; padding: 0; font-family: 'Tajawal', sans-serif;
            background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
            background-size: cover; background-position: center;
            height: 100vh; display: flex; flex-direction: column; align-items: center;
            color: white; overflow: hidden;
        }}
        .container {{
            width: 100%; height: 100%; display: flex; flex-direction: column;
            align-items: center; justify-content: flex-start; padding-top: 5vh;
        }}
        .unified-text {{ text-shadow: 2px 2px 15px rgba(0,0,0,0.9); text-align: center; margin: 0; }}
        .time-val {{ font-size: 15vw; font-weight: 900; line-height: 1; }}
        .ampm-val {{ font-size: 4vw; color: #FFA500; margin-right: 15px; }}
        .info-line {{ font-size: 4.5vw; font-weight: 700; margin-top: 10px; }}
        .eng-sub {{ font-size: 2.2vw; opacity: 0.85; font-weight: 400; display: block; }}
        
        .data-bar {{
            display: flex; gap: 20px; margin-top: 25px;
            background: rgba(255, 255, 255, 0.12); padding: 15px 35px;
            border-radius: 60px; backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .data-item {{ font-size: 3vw; font-weight: bold; text-align: center; line-height: 1.3; }}
        .small-label {{ font-size: 1.5vw; font-weight: normal; opacity: 0.9; }}

        .social-links {{ margin-top: auto; padding-bottom: 5vh; display: flex; gap: 20px; }}
        .social-links a {{
            color: white; text-decoration: none; font-size: 1.5vw;
            padding: 12px 30px; background: rgba(0,0,0,0.6); border-radius: 50px;
            border: 1px solid rgba(255,255,255,0.3); transition: 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="unified-text time-val">
            <span id="live-time">--:--:--</span>
            <span id="live-ampm" class="ampm-val"></span>
        </div>

        <div class="unified-text info-line">{hij_str} | {mil_str}</div>

        <div class="unified-text info-line" style="color:#00FF00; margin-top:15px;">
            <span id="next-prayer-text">--:--:--</span>
            <span class="eng-sub" id="next-prayer-eng">--:--:--</span>
        </div>

        <div class="data-bar">
            <div class="data-item">🌡️ {weather_str}<br><span class="small-label">Temp</span></div>
            <div class="data-item">☀️ الشروق: {sunrise}<br><span class="small-label">Sunrise</span></div>
            <div class="data-item">🌅 الغروب: {sunset}<br><span class="small-label">Sunset</span></div>
        </div>

        <div class="unified-text info-line" style="margin-top:30px;">
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
        
        function updateClock() {{
            const now = new Date();
            // استخدام توقيت الرياض
            const riyadhTime = new Intl.DateTimeFormat('en-US', {{
                timeZone: 'Asia/Riyadh', hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: false
            }}).formatToParts(now);
            
            const t = {{}}; riyadhTime.forEach(p => t[p.type] = p.value);
            let h = parseInt(t.hour);
            const m = parseInt(t.minute);
            const s = parseInt(t.second);

            // عرض الوقت 12 ساعة
            const h12 = h % 12 || 12;
            const ampmAr = h >= 12 ? 'م' : 'ص';
            const ampmEn = h >= 12 ? 'PM' : 'AM';
            
            document.getElementById('live-time').textContent = `${{h12}}:${{m.toString().padStart(2,'0')}}:${{s.toString().padStart(2,'0')}}`;
            document.getElementById('live-ampm').textContent = `${{ampmAr}} / ${{ampmEn}}`;

            // منطق الصلاة القادمة
            const prayers = [
                {{ar: 'الفجر', en: 'Fajr', t: prayerTimes.Fajr}},
                {{ar: 'الظهر', en: 'Dhuhr', t: prayerTimes.Dhuhr}},
                {{ar: 'العصر', en: 'Asr', t: prayerTimes.Asr}},
                {{ar: 'المغرب', en: 'Maghrib', t: prayerTimes.Maghrib}},
                {{ar: 'العشاء', en: 'Isha', t: prayerTimes.Isha}}
            ];

            const currentStr = `${{h.toString().padStart(2,'0')}}:${{m.toString().padStart(2,'0')}}`;
            let next = prayers.find(p => p.t > currentStr) || prayers[0];
            
            if (next.t) {{
                const [ph, pm] = next.t.split(':').map(Number);
                let pDate = new Date(now);
                pDate.setHours(ph, pm, 0);
                if (next === prayers[0] && currentStr > prayers[4].t) pDate.setDate(pDate.getDate() + 1);
                
                const diff = Math.floor((pDate - now) / 1000);
                if (diff > 0) {{
                    const dh = Math.floor(diff / 3600);
                    const dm = Math.floor((diff % 3600) / 60);
                    const ds = diff % 60;
                    const res = `${{dh.toString().padStart(2,'0')}}:${{dm.toString().padStart(2,'0')}}:${{ds.toString().padStart(2,'0')}}`;
                    document.getElementById('next-prayer-text').textContent = `متبقي على ${{next.ar}}: ${{res}}`;
                    document.getElementById('next-prayer-eng').textContent = `Time to ${{next.en}}: ${{res}}`;
                }}
            }}
        }}
        setInterval(updateClock, 1000);
        updateClock();
    </script>
</body>
</html>
"""

# عرض المكون مع ضبط الارتفاع ليتناسب مع الشاشة
components.html(html_code, height=800)
