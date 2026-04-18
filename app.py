import streamlit as st
import pytz
from datetime import datetime, date
import time
import requests
from hijri_converter import Gregorian
from streamlit_js_eval import get_geolocation

# إعداد الصفحة لإخفاء العناصر غير الضرورية
st.set_page_config(page_title="ساعة الأرض - aale1164", layout="wide")

sa_tz = pytz.timezone('Asia/Riyadh')

# --- وظيفة جلب الطقس ---
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url).json()
        temp = response['current_weather']['temperature']
        return f"{temp}°C"
    except:
        return "25°C"

# --- وظيفة حساب الفصول ---
def get_season_info():
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
    return "الربيع / Spring", (date(year + 1, 3, 21) - today).days, "🌸"

# --- التصميم الجديد (عربي وانجليزي) ---
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
        padding-top: 4vh;
    }

    .unified-text {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 12px rgba(0,0,0,0.8); 
        margin: 0;
        line-height: 1.1;
        text-align: center;
    }

    .time-val { font-size: 14vw; font-weight: 900; }
    .ampm-val { font-size: 4vw; margin-right: 10px; color: #FFA500; }
    .info-line { font-size: 4vw; font-weight: 700; margin-top: 5px; }
    .eng-sub { font-size: 2vw; opacity: 0.8; font-weight: 400; display: block; }

    /* شريط البيانات الزجاجي */
    .data-bar {
        display: flex;
        gap: 15px;
        margin-top: 15px;
        background: rgba(255, 2
