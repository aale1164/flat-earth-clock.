import streamlit as st
import streamlit.components.v1 as components
import pytz
from datetime import datetime, date, timedelta
import requests
from hijri_converter import Gregorian
import json

# --- إعداد الصفحة ---
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

# محاولة استيراد مكتبة أوقات الصلاة
try:
    from prayer_times_calculator import PrayerTimesCalculator
    PRAYER_LIB_AVAILABLE = True
except ImportError:
    PRAYER_LIB_AVAILABLE = False

# محاولة استيراد مكتبة الموقع الجغرافي
try:
    from streamlit_js_eval import get_geolocation
    GEO_LIB_AVAILABLE = True
except ImportError:
    GEO_LIB_AVAILABLE = False

sa_tz = pytz.timezone('Asia/Riyadh')

# --- دوال جلب البيانات (مع تخزين مؤقت) ---
@st.cache_data(ttl=600)
def fetch_weather_cached(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        resp = requests.get(url, timeout=5).json()
        return resp['current_weather']['temperature']
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

# --- البيانات الأساسية (تحسب مرة واحدة عند التحميل) ---
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

# تمرير بيانات الصلاة إلى JavaScript بصيغة JSON
prayer_json = json.dumps(prayer_dict, ensure_ascii=False)

# --- كود HTML + CSS + JavaScript (واجهة كاملة ومستقرة) ---
html_code = f"""
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Tajawal', sans-serif;
            background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            color: white;
            overflow: hidden;
            padding: 5vh 20px 0 20px;
        }}
        .main-container {{
            width: 100%;
            max-width: 1200px;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
        }}
        .unified-text {{
            text-shadow: 2px 2px 15px rgba(0,0,0,0.8);
            text-align: center;
            margin: 0;
            line-height: 1.3;
        }}
        .time-display {{
            font-size: 15vw;
            font-weight: 900;
            line-height: 1;
        }}
        .ampm-display {{
            font-size: 5vw;
            margin-right: 10px;
            color: #FFD966;
        }}
        .info-line {{
            font-size: 4.5vw;
            font-weight: 700;
            margin-top: 8px;
            opacity: 0.9;
        }}
        .prayer-line {{
            font-size: 4.5vw;
            font-weight: 700;
            margin-top: 12px;
            color: #B5FFB5;
        }}
        /* صندوق البيانات (طقس، شروق، غروب) */
        .data-bar {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px 30px;
            margin-top: 35px;
            background: rgba(20, 20, 20, 0.25);
            padding: 15px 35px;
            border-radius: 60px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            opacity: 0.95;
        }}
        .data-item {{
            font-size: 3.5vw;
            font-weight: bold;
            color: #FFFFFF;
            text-align: center;
            line-height: 1.4;
            opacity: 0.9;
            min-width: 120px;
        }}
        .data-label {{
            font-size: 1.8vw;
            font-weight: normal;
            opacity: 0.7;
            display: block;
            margin-top: 4px;
        }}
        /* سطر الفصل */
        .season-line {{
            font-size: 4.2vw;
            font-weight: 700;
            margin-top: 35px;
            opacity: 0.9;
        }}
        .season-sub {{
            font-size: 2.2vw;
            opacity: 0.75;
            font-weight: normal;
            display: block;
        }}
        /* روابط التواصل */
        .social-footer {{
            margin-top: auto;
            padding-bottom: 30px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .social-footer a {{
            color: white;
            text-decoration: none;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 28px;
            background: rgba(0,0,0,0.5);
            border-radius: 50px;
            border: 1px solid rgba(255,255,255,0.25);
            backdrop-filter: blur(5px);
            transition: all 0.3s ease;
            opacity: 0.9;
        }}
        .social-footer a:hover {{
            background: rgba(255, 165, 0, 0.6);
            border-color: #FFA500;
        }}
        /* استجابة للشاشات الصغيرة */
        @media (max-width: 600px) {{
            .time-display {{ font-size: 18vw; }}
            .info-line {{ font-size: 6vw; }}
            .data-item {{ font-size: 5vw; }}
            .data-label {{ font-size: 3vw; }}
            .season-line {{ font-size: 5.5vw; }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <!-- الوقت المباشر -->
        <div class="unified-text time-display">
            <span id="live-time">--:--:--</span>
            <span id="live-ampm" class="ampm-display"></span>
        </div>

        <!-- التاريخ -->
        <div class="unified-text info-line">{hij_str} | {mil_str}</div>

        <!-- متبقي على الصلاة -->
        <div class="unified-text prayer-line">
            <span id="next-prayer-text">متبقي على --: --:--:--</span>
            <span class="data-label" id="next-prayer-eng" style="font-size:2.2vw; margin-top:2px;">Time to --: --:--:--</span>
        </div>

        <!-- صندوق الطقس والشروق والغروب -->
        <div class="data-bar">
            <div class="data-item">🌡️ {weather_str}<span class="data-label">Temp</span></div>
            <div class="data-item">☀️ الشروق: {sunrise}<span class="data-label">Sunrise</span></div>
            <div class="data-item">🌅 الغروب: {sunset}<span class="data-label">Sunset</span></div>
        </div>

        <!-- سطر الفصل -->
        <div class="unified-text season-line">
            {season_icon} متبقي على {season_ar}: {days_left} يوم
            <span class="season-sub">{days_left} days left for {season_en}</span>
        </div>

        <!-- روابط التواصل -->
        <div class="social-footer">
            <a href="https://twitter.com/aale1164" target="_blank">𝕏 @aale1164</a>
            <a href="https://www.snapchat.com/add/aale112" target="_blank">👻 aale112</a>
        </div>
    </div>

    <script>
        const prayerTimes = {prayer_json};
        const TIMEZONE = 'Asia/Riyadh';

        function updateClock() {{
            const now = new Date();

            // تحويل الوقت إلى توقيت الرياض
            const formatter = new Intl.DateTimeFormat('en-US', {{
                timeZone: TIMEZONE,
                hour: 'numeric',
                minute: 'numeric',
                second: 'numeric',
                hour12: false
            }});
            const parts = formatter.formatToParts(now);
            const timeObj = {{}};
            parts.forEach(p => {{ timeObj[p.type] = p.value; }});

            let hour = parseInt(timeObj.hour);
            const minute = parseInt(timeObj.minute);
            const second = parseInt(timeObj.second);
            const year = parseInt(timeObj.year);
            const month = parseInt(timeObj.month) - 1;
            const day = parseInt(timeObj.day);

            // تنسيق الوقت 12 ساعة
            const hour12 = hour % 12 || 12;
            const ampmAr = hour >= 12 ? 'م' : 'ص';
            const ampmEn = hour >= 12 ? 'PM' : 'AM';

            document.getElementById('live-time').textContent = 
                `${{hour12}}:${{minute.toString().padStart(2, '0')}}:${{second.toString().padStart(2, '0')}}`;
            document.getElementById('live-ampm').textContent = `${{ampmAr}} / ${{ampmEn}}`;

            // حساب الصلاة القادمة
            const prayers = [
                {{ ar: 'الفجر', en: 'Fajr', time: prayerTimes.Fajr }},
                {{ ar: 'الظهر', en: 'Dhuhr', time: prayerTimes.Dhuhr }},
                {{ ar: 'العصر', en: 'Asr', time: prayerTimes.Asr }},
                {{ ar: 'المغرب', en: 'Maghrib', time: prayerTimes.Maghrib }},
                {{ ar: 'العشاء', en: 'Isha', time: prayerTimes.Isha }}
            ];

            const currentTimeStr = `${{hour.toString().padStart(2, '0')}}:${{minute.toString().padStart(2, '0')}}`;
            let nextPrayer = prayers.find(p => p.time && p.time > currentTimeStr) || prayers[0];

            if (nextPrayer && nextPrayer.time) {{
                const [pHour, pMinute] = nextPrayer.time.split(':').map(Number);
                let prayerDate = new Date(year, month, day, pHour, pMinute, 0);

                // إذا كانت الصلاة القادمة هي الفجر ونحن بعد العشاء -> نضيف يوم
                if (nextPrayer === prayers[0] && currentTimeStr > (prayers[4].time || "23:59")) {{
                    prayerDate.setDate(prayerDate.getDate() + 1);
                }}

                const diffSeconds = Math.floor((prayerDate - now) / 1000);
                if (diffSeconds > 0) {{
                    const hLeft = Math.floor(diffSeconds / 3600);
                    const mLeft = Math.floor((diffSeconds % 3600) / 60);
                    const sLeft = diffSeconds % 60;
                    const timeLeft = `${{hLeft.toString().padStart(2, '0')}}:${{mLeft.toString().padStart(2, '0')}}:${{sLeft.toString().padStart(2, '0')}}`;

                    document.getElementById('next-prayer-text').textContent = `متبقي على ${{nextPrayer.ar}}: ${{timeLeft}}`;
                    document.getElementById('next-prayer-eng').textContent = `Time to ${{nextPrayer.en}}: ${{timeLeft}}`;
                }} else {{
                    document.getElementById('next-prayer-text').textContent = `حان وقت ${{nextPrayer.ar}}`;
                    document.getElementById('next-prayer-eng').textContent = `Time for ${{nextPrayer.en}}`;
                }}
            }}
        }}

        // تحديث فوري ثم كل ثانية
        updateClock();
        setInterval(updateClock, 1000);
    </script>
</body>
</html>
"""

# عرض المكون (height كبير لتغطية الشاشة بدون شريط تمرير)
components.html(html_code, height=900, scrolling=False)
