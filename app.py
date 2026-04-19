import streamlit as st
import streamlit.components.v1 as components
import pytz
from datetime import datetime, date, timedelta
import requests
from hijri_converter import Gregorian
import json

# --- إعداد الصفحة ---
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

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

@st.cache_data(ttl=3600)
def fetch_prayer_times_cached(lat, lon, date_str):
    """جلب مواقيت الصلاة من AlAdhan API باستخدام requests"""
    try:
        url = f"https://api.aladhan.com/v1/timings/{date_str}"
        params = {
            'latitude': lat,
            'longitude': lon,
            'method': 4,  # مكة المكرمة (Umm al-Qura)
            'school': 0,   # شافعي (الافتراضي)
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data['code'] == 200:
            timings = data['data']['timings']
            return {
                'Fajr': timings['Fajr'],
                'Sunrise': timings['Sunrise'],
                'Dhuhr': timings['Dhuhr'],
                'Asr': timings['Asr'],
                'Maghrib': timings['Maghrib'],
                'Isha': timings['Isha'],
            }
    except:
        pass
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

# --- إدارة حالة الموقع الجغرافي ---
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 26.32, 43.97  # افتراضي: بريدة
    st.session_state.location_checked = False

# --- صفحة طلب إذن الموقع (تظهر مرة واحدة) ---
if not st.session_state.location_checked and GEO_LIB_AVAILABLE:
    st.markdown("""
    <style>
        .stApp { background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png") center/cover fixed; }
        .permission-box {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100vh; color: white; text-shadow: 2px 2px 5px black; text-align: center;
            background: rgba(0,0,0,0.3); backdrop-filter: blur(5px); padding: 20px;
        }
        .permission-box button {
            padding: 15px 30px; font-size: 20px; background: #FFA500; color: black;
            border: none; border-radius: 50px; cursor: pointer; font-weight: bold;
            margin-top: 20px; transition: 0.3s;
        }
        .permission-box button:hover { background: #FFD700; transform: scale(1.05); }
    </style>
    <div class="permission-box">
        <h1>🌍 أهلاً بك في ساعة الأرض</h1>
        <p style="font-size: 18px;">للحصول على مواقيت الصلاة والطقس بدقة، نرجو الموافقة على مشاركة موقعك.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("📍 مشاركة الموقع", type="primary", use_container_width=True):
            try:
                loc = get_geolocation()
                if loc and 'coords' in loc:
                    st.session_state.lat = loc['coords']['latitude']
                    st.session_state.lon = loc['coords']['longitude']
                else:
                    st.warning("تعذر الحصول على الموقع. سيتم استخدام الموقع الافتراضي.")
                st.session_state.location_checked = True
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
                st.session_state.location_checked = True
                st.rerun()
    st.stop()

# --- إذا لم تصلنا الإحداثيات بعد، استخدم الافتراضي ---
if not st.session_state.location_checked:
    st.session_state.location_checked = True

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
temp = fetch_weather_cached(st.session_state.lat, st.session_state.lon)
weather_str = f"{temp}°C" if temp is not None else "--°C"

# جلب مواقيت الصلاة من AlAdhan API
prayer_times_data = fetch_prayer_times_cached(st.session_state.lat, st.session_state.lon, today.strftime("%d-%m-%Y"))
sunrise = sunset = "--:--"
prayer_dict = {}
if prayer_times_data:
    sunrise = prayer_times_data.get('Sunrise', '--:--')
    sunset = prayer_times_data.get('Maghrib', '--:--')
    prayer_dict = {
        'الفجر': prayer_times_data.get('Fajr', '--:--'),
        'الظهر': prayer_times_data.get('Dhuhr', '--:--'),
        'العصر': prayer_times_data.get('Asr', '--:--'),
        'المغرب': prayer_times_data.get('Maghrib', '--:--'),
        'العشاء': prayer_times_data.get('Isha', '--:--')
    }

# الفصل
season_ar, season_en, days_left, season_icon = get_season_data()

# تمرير بيانات الصلاة إلى JavaScript بصيغة JSON
prayer_json = json.dumps(prayer_dict, ensure_ascii=False)

# --- كود HTML + CSS + JavaScript (محسَّن للهواتف) ---
html_code = f"""
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Tajawal', sans-serif;
            background: url("https://raw.githubusercontent.com/aale1164/flat-earth-clock./main/background.png");
            background-size: cover; background-position: center; background-attachment: fixed;
            min-height: 100dvh; display: flex; flex-direction: column; align-items: center;
            color: white; overflow: hidden; padding: 5vh 16px 0 16px;
        }}
        .main-container {{
            width: 100%; max-width: 600px; height: 100%; display: flex;
            flex-direction: column; align-items: center; justify-content: flex-start;
        }}
        .unified-text {{
            text-shadow: 2px 2px 12px rgba(0,0,0,0.7); text-align: center; margin: 0; line-height: 1.3;
        }}
        .time-display {{ font-size: clamp(4rem, 18vw, 8rem); font-weight: 900; line-height: 1; }}
        .ampm-display {{ font-size: clamp(1.2rem, 6vw, 2.5rem); margin-right: 8px; color: #FFD966; }}
        .info-line {{ font-size: clamp(1.2rem, 5.5vw, 2.2rem); font-weight: 700; margin-top: 6px; opacity: 0.9; }}
        .prayer-line {{
            font-size: clamp(1.2rem, 5.5vw, 2.2rem); font-weight: 700; margin-top: 12px; color: #B5FFB5;
        }}
        .eng-sub {{
            font-size: clamp(0.9rem, 3.5vw, 1.3rem); opacity: 0.8; font-weight: 400;
            display: block; margin-top: 2px;
        }}
        /* صندوق البيانات - محسّن */
        .data-bar {{
            display: flex; flex-wrap: wrap; justify-content: center; align-items: center;
            gap: 12px 20px; margin-top: 25px; background: rgba(20, 20, 20, 0.25);
            padding: 12px 20px; border-radius: 50px; backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2); width: fit-content; max-width: 100%;
        }}
        .data-item {{
            font-size: clamp(1rem, 4.5vw, 1.8rem); font-weight: bold; color: #FFFFFF;
            text-align: center; line-height: 1.4; opacity: 0.95; white-space: nowrap;
        }}
        .data-label {{
            font-size: clamp(0.7rem, 3vw, 1.1rem); font-weight: normal; opacity: 0.7;
            display: block; margin-top: 2px;
        }}
        /* سطر الفصل */
        .season-line {{
            font-size: clamp(1.2rem, 5.5vw, 2.2rem); font-weight: 700; margin-top: 30px; opacity: 0.9;
        }}
        .season-sub {{
            font-size: clamp(0.9rem, 3.8vw, 1.4rem); opacity: 0.75; font-weight: normal; display: block;
        }}
        /* روابط التواصل */
        .social-footer {{
            margin-top: auto; padding-bottom: 20px; display: flex; gap: 12px;
            flex-wrap: wrap; justify-content: center;
        }}
        .social-footer a {{
            color: white; text-decoration: none; font-size: clamp(0.9rem, 3.5vw, 1.2rem);
            font-weight: bold; padding: 12px 24px; background: rgba(0,0,0,0.5);
            border-radius: 50px; border: 1px solid rgba(255,255,255,0.25);
            backdrop-filter: blur(5px); transition: all 0.2s ease; opacity: 0.95;
            display: inline-block;
        }}
        .social-footer a:hover {{ background: rgba(255, 165, 0, 0.6); border-color: #FFA500; }}

        /* تحسينات خاصة بالهواتف الصغيرة */
        @media (max-width: 480px) {{
            body {{ padding: 4vh 12px 0 12px; }}
            .data-bar {{
                flex-direction: column; gap: 10px; padding: 14px 18px; width: 90%;
                border-radius: 40px;
            }}
            .data-item {{ white-space: normal; }}
            .social-footer {{ padding-bottom: 15px; }}
            .social-footer a {{ padding: 10px 18px; }}
            .time-display {{ font-size: clamp(3.5rem, 20vw, 6rem); }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="unified-text time-display">
            <span id="live-time">--:--:--</span>
            <span id="live-ampm" class="ampm-display"></span>
        </div>

        <div class="unified-text info-line">{hij_str} | {mil_str}</div>

        <div class="unified-text prayer-line">
            <span id="next-prayer-text">متبقي على --: --:--:--</span>
            <span class="eng-sub" id="next-prayer-eng">Time to --: --:--:--</span>
        </div>

        <div class="data-bar">
            <div class="data-item">🌡️ {weather_str}<span class="data-label">Temp</span></div>
            <div class="data-item">☀️ الشروق: {sunrise}<span class="data-label">Sunrise</span></div>
            <div class="data-item">🌅 الغروب: {sunset}<span class="data-label">Sunset</span></div>
        </div>

        <div class="unified-text season-line">
            {season_icon} متبقي على {season_ar}: {days_left} يوم
            <span class="season-sub">{days_left} days left for {season_en}</span>
        </div>

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

            const formatter = new Intl.DateTimeFormat('en-US', {{
                timeZone: TIMEZONE, hour: 'numeric', minute: 'numeric',
                second: 'numeric', hour12: false
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

            const hour12 = hour % 12 || 12;
            const ampmAr = hour >= 12 ? 'م' : 'ص';
            const ampmEn = hour >= 12 ? 'PM' : 'AM';

            document.getElementById('live-time').textContent = 
                `${{hour12}}:${{minute.toString().padStart(2, '0')}}:${{second.toString().padStart(2, '0')}}`;
            document.getElementById('live-ampm').textContent = `${{ampmAr}} / ${{ampmEn}}`;

            const prayers = [
                {{ ar: 'الفجر', en: 'Fajr', time: prayerTimes['الفجر'] }},
                {{ ar: 'الظهر', en: 'Dhuhr', time: prayerTimes['الظهر'] }},
                {{ ar: 'العصر', en: 'Asr', time: prayerTimes['العصر'] }},
                {{ ar: 'المغرب', en: 'Maghrib', time: prayerTimes['المغرب'] }},
                {{ ar: 'العشاء', en: 'Isha', time: prayerTimes['العشاء'] }}
            ];

            const currentTimeStr = `${{hour.toString().padStart(2, '0')}}:${{minute.toString().padStart(2, '0')}}`;
            let nextPrayer = prayers.find(p => p.time && p.time > currentTimeStr) || prayers[0];

            if (nextPrayer && nextPrayer.time) {{
                const [pHour, pMinute] = nextPrayer.time.split(':').map(Number);
                let prayerDate = new Date(year, month, day, pHour, pMinute, 0);

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

        updateClock();
        setInterval(updateClock, 1000);
    </script>
</body>
</html>
"""

components.html(html_code, height=950, scrolling=False)
