import streamlit as st
import pytz
from datetime import datetime, date
import time
import requests
from hijri_converter import Gregorian

# إعداد الصفحة (يجب أن يكون في بداية الكود دائماً)
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

# محاولة استيراد مكتبة أوقات الصلاة بشكل آمن
try:
    from prayer_times_calculator import PrayerTimesCalculator
    PRAYER_LIB_AVAILABLE = True
except ImportError:
    PRAYER_LIB_AVAILABLE = False

# محاولة استيراد مكتبة الموقع الجغرافي بشكل آمن
try:
    from streamlit_js_eval import get_geolocation
    GEO_LIB_AVAILABLE = True
except ImportError:
    GEO_LIB_AVAILABLE = False

# إعداد المنطقة الزمنية
sa_tz = pytz.timezone('Asia/Riyadh')

# --- دوال المساعدة للطقس والفصول ---
def fetch_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        temp = response['current_weather']['temperature']
        return f"{temp}°C"
    except Exception:
        return "--°C"

def get_season_data():
    today = date.today()
    year = today.year
    seasons = [
        ('الربيع / Spring', date(year, 3, 21), "🌸"),
        ('الصيف / Summer', date(year, 6, 21), "☀️"),
        ('الخريف / Autumn', date(year, 9, 23), "🍂"),
        ('الشتاء / Winter', date(year, 12, 21), "❄️")
    ]
    for name, s_date, icon in seasons:
        if s_date > today:
            return name, (s_date - today).days, icon
            
    # إذا تجاوزنا 21 ديسمبر، نحسب للربيع القادم
    next_spring = date(year + 1, 3, 21)
    return "الربيع / Spring", (next_spring - today).days, "🌸"

# --- التنسيق البصري (CSS) ---
st.markdown("""
<style>
    /* إخفاء شريط الأدوات الافتراضي */
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
        padding-top: 4vh;
    }

    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8); 
        margin: 0;
        line-height: 1.2;
        text-align: center;
    }

    .time-val { font-size: 14vw; font-weight: 900
