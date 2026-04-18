import streamlit as st
import pytz
from datetime import datetime
try:
    from hijri_converter import Gregorian
except:
    pass  # جاري معالجة خطأ التحميل، يتم التجاهل مؤقتاً

# إعدادات الصفحة
st.set_page_config(page_title="مواعيد الرواتب - aale1164", layout="centered", page_icon="💰")

# رابط الصورة الخلفية (تم تحميلها إلى GitHub لضمان الأمان)
# تأكد من أنك قمت برفع الصورة باسم background.png إلى مستودعك
BACKGROUND_URL = "background.png" 

# توقيت السعودية والقائمة العربية
saudi_tz = pytz.timezone('Asia/Riyadh')
hijri_months_ar = ["المحرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

def calculate_days(target_day, now_date):
    if now_date.day <= target_day:
        return target_day - now_date.day
    else:
        import calendar
        _, last_day = calendar.monthrange(now_date.year, now_date.month)
        return (last_day - now_date.day) + target_day

# الحصول على البيانات
now = datetime.now(saudi_tz)
d_salary = calculate_days(27, now)
d_citizen = calculate_days(10, now)
d_dhaman_retirement = calculate_days(1, now)

current_time = now.strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
h = Gregorian(now.year, now.month, now.day).to_hijri()
hijri_date = f"{h.day} {hijri_months_ar[h.month - 1]} {h.year} هـ"

# تنسيق الواجهة (CSS) المطور - الخلفية والمحاذاة اليمينية
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
        color: #f1f1f1;
    }}
    
    #stApp {{
        background-image: url("{BACKGROUND_URL}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    
    #stApp:before {{
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.4);
    }}
    
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    #root {{
        background: transparent !important;
    }}
    
    .stMainBlock {{
        background-color: transparent !important;
    }}
    
    .stMarkdown {{
        background: transparent !important;
    }}
    
    div[data-testid="stMarkdownContainer"] p {{
        background: transparent !important;
    }}
    
    #root > div:nth-child(1) > div > div > div > main > div:nth-child(1) > div > div:nth-child(1) {{
        background: transparent !important;
    }}
    
    #root > div:nth-child(1) > div > div > div > main > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) {{
        background: transparent !important;
    }}
    
    .css-1r6slb0, .css-k7v5r2 {{
        background: transparent !important;
    }}
    
    .salary-block {{
        background-color: rgba(30, 33, 48, 0.7);
        border-radius: 12px;
        padding: 15px 20px;
        margin: 10px 0;
        border-right: 6px solid #00FF00;
        text-align: right;
    }}
    
    .salary-days {{
        font-size: 26px;
        color: #00FF00;
        font-weight: bold;
    }}
    
    .time-container {{
        text-align: center;
        margin-bottom: 20px;
        background: transparent !important;
    }}
    
    .social-links {{
        margin-top: 30px;
        padding: 15px;
        background-color: rgba(22, 25, 37, 0.7);
        border-radius: 10px;
        text-align: center;
    }}
    .twitter-btn {{ color: #1DA1F2; text-decoration: none; font-weight: bold; display: block; margin-bottom: 5px; }}
    .snap-btn {{ color: #FFFC00; text-decoration: none; font-weight: bold; display: block; }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: #f1f1f1 !important;
    }}
    
    </style>
    """, unsafe_allow_html=True)

# عرض الواجهة
st.markdown(f"<div class='time-container'>", unsafe_allow_html=True)
st.markdown(f"<h1 style='color: #00FF00; margin-bottom: 0;'>{current_time}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color: #FFA500; margin-top: 0;'>{hijri_date}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #d1d1d1;'>{now.strftime('%A, %d %B %Y')}</p>", unsafe_allow_html=True)
st.markdown(f"</div>", unsafe_allow_html=True)

st.divider()

# صفوف الرواتب بنظام الأعمدة المطور
c1, c2 = st.columns([3, 1])
c1.subheader("💰 رواتب الموظفين")
c2.markdown(f"<div class='salary-days'>{d_salary} يوم</div>", unsafe_allow_html=True)

st.write("")  # مسافة بسيطة

c3, c4 = st.columns([3, 1])
c3.subheader("💳 حساب المواطن")
c4.markdown(f"<div class='salary-days'>{d_citizen} يوم</div>", unsafe_allow_html=True)

st.write("")  # مسافة بسيطة

c5, c6 = st.columns([3, 1])
c5.subheader("🏠 الضمان والتقاعد")
c6.markdown(f"<div class='salary-days'>{d_dhaman_retirement} يوم</div>", unsafe_allow_html=True)

st.divider()

# حسابات التواصل
st.markdown(f"""
    <div class="social-links">
        <p style="color: #b1b1b1; margin-bottom: 5px; font-size: 14px;">إعداد وتطوير</p>
        <a href="https://twitter.com/aale1164" class="twitter-btn">𝕏 @aale1164</a>
        <a href="https://www.snapchat.com/add/aale112" class="snap-btn">👻 aale112</a>
    </div>
""", unsafe_allow_html=True)

# زر تحديث يدوي
if st.button('🔄 تحديث الوقت', key='update_btn'):
    st.rerun()
