# داخل html_code، استبدل الوسم <style> الحالي بما يلي:
<style>
    * {
        box-sizing: border-box;
    }
    body {
        margin: 0;
        padding: 0;
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
    }
    .container {
        width: 100%;
        max-width: 1200px;  /* تحديد عرض أقصى للشاشات الكبيرة */
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding: 5vh 20px 0 20px;  /* هامش جانبي للجوال */
    }
    .unified-text {
        text-shadow: 2px 2px 15px rgba(0,0,0,0.9);
        text-align: center;
        margin: 0;
    }
    .time-val {
        font-size: 15vw;
        font-weight: 900;
        line-height: 1;
    }
    /* جعل حجم الخط يتكيف مع الشاشات العريضة */
    @media (min-width: 768px) {
        .time-val { font-size: 10vw; }
        .info-line { font-size: 3.5vw; }
        .eng-sub { font-size: 1.8vw; }
        .data-item { font-size: 2.5vw; }
        .small-label { font-size: 1.2vw; }
        .social-links a { font-size: 1.2vw; padding: 10px 25px; }
    }
    @media (min-width: 1200px) {
        .time-val { font-size: 8vw; }
        .info-line { font-size: 2.8vw; }
    }

    .ampm-val {
        font-size: 4vw;
        color: #FFA500;
        margin-right: 15px;
    }
    .info-line {
        font-size: 4.5vw;
        font-weight: 700;
        margin-top: 10px;
    }
    .eng-sub {
        font-size: 2.2vw;
        opacity: 0.85;
        font-weight: 400;
        display: block;
    }
    .data-bar {
        display: flex;
        flex-wrap: wrap;        /* يسمح بالتفاف العناصر على الشاشات الصغيرة */
        justify-content: center;
        gap: 20px 30px;          /* مسافة أفقية وعمودية */
        margin-top: 25px;
        background: rgba(255, 255, 255, 0.12);
        padding: 15px 35px;
        border-radius: 60px;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 90%;          /* لا يلامس الحواف */
    }
    .data-item {
        font-size: 3vw;
        font-weight: bold;
        text-align: center;
        line-height: 1.3;
        min-width: 120px;        /* عرض أدنى لكل عنصر */
    }
    .small-label {
        font-size: 1.5vw;
        font-weight: normal;
        opacity: 0.9;
    }
    .social-links {
        margin-top: auto;
        padding-bottom: 5vh;
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        justify-content: center;
    }
    .social-links a {
        color: white;
        text-decoration: none;
        font-size: 1.5vw;
        padding: 12px 30px;
        background: rgba(0,0,0,0.6);
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }
    .social-links a:hover {
        background: rgba(255, 165, 0, 0.7);
        border-color: #FFA500;
        transform: scale(1.05);
    }
</style>
