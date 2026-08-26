from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
from utils.question_loader import load_questions
from utils.symptom_predictor import predict_symptoms
from utils.image_predictor import predict_image
from utils.i18n import TRANSLATIONS
from PIL import Image
import io
from datetime import datetime
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent

# =========================
# 1. إعدادات الصفحة
# =========================
st.set_page_config(
    page_title="FMD Detection",
    page_icon="🐄",
    layout="wide"
)

# =========================
# 1b. اللغة الحالية للموقع بالكامل
# =========================
# Single source of truth for language, read once per run and used to build
# every piece of UI text and the `direction` of the layout below. Switching
# language just flips this flag and reruns the script - nothing else in the
# app needs to know or care which language is active.
if "lang" not in st.session_state:
    st.session_state.lang = "en"

LANG = st.session_state.lang
T = TRANSLATIONS[LANG]
DIR = T["dir"]  # "ltr" or "rtl"


def toggle_lang():
    st.session_state.lang = "ar" if st.session_state.lang == "en" else "en"

import base64

@st.cache_data
def get_base64(image_path):
    with open(BASE_DIR / image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


# ================================
# تحميل صور الخلفية (للـ Hero) - بتتحمل مرة واحدة وتتلف تلقائيًا فى العرض
# ================================
HERO_IMAGE_FILES = [
    ("asset/cow.jpeg", "image/jpeg"),
    ("asset/2.png", "image/png"),
    ("asset/3.jpeg", "image/jpeg"),
    ("asset/4.jpeg", "image/jpeg"),
]
hero_images = [
    {"data": get_base64(path), "mime": mime} for path, mime in HERO_IMAGE_FILES
]

TIPS_IMAGE_FILES = [
    ("asset/clean.png", "image/png"),
    ("asset/Wash and Dry.jpeg", "image/jpeg"),
    ("asset/Good Lighting.jpeg", "image/jpeg"),
]

tips_images = [
    {"data": get_base64(path), "mime": mime} for path, mime in TIPS_IMAGE_FILES
]

tips_1 = tips_images[0]
tips_2 = tips_images[1]
tips_3 = tips_images[2]

# ================================
# شعار النافبار (Logo)
# ================================
LOGO_IMAGE_FILE = ("asset/logo.jpeg", "image/jpeg")
logo_image = {"data": get_base64(LOGO_IMAGE_FILE[0]), "mime": LOGO_IMAGE_FILE[1]}

if "hero_index" not in st.session_state:
    st.session_state.hero_index = 0

hero_background = hero_images[st.session_state.hero_index]["data"]
# =========================
# 2. تحميل CSS الخارجي + التصميم الجديد
# =========================
@st.cache_data
def get_css(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def load_css(file_path):
    css = get_css(file_path)
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css(BASE_DIR / "styles" / "main.css")
# =========================
# 2b. Layout primitive: centered_section
# =========================
# Streamlit widgets (st.file_uploader, st.button, st.form, ...) are never
# rendered as DOM children of a <div> written via st.markdown() - each
# st.markdown() call produces its own sibling element, so raw HTML wrapper
# tags never actually enclose the widgets that follow them.
#
# st.container(key=...) is different: everything called inside its `with`
# block is rendered as a genuine child of that container in the real DOM,
# and Streamlit automatically attaches a stable, documented CSS hook to it:
# `.st-key-<key>`. That gives us a real, reusable "centered card" building
# block without touching any undocumented internal Streamlit classes.
@contextmanager
def centered_section(key: str):
    """A real Streamlit container, targetable in CSS via `.st-key-<key>`."""
    with st.container(key=key):
        yield

# إضافة CSS مخصص (بما في ذلك تصميم منطقة الرفع الجديد)
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

/* ===== DESIGN TOKENS =====
   One consistent scale for type + spacing, used everywhere instead of
   ad-hoc values, so the whole site reads as one coherent system. */
:root {{
    --fs-2xs: 0.85rem;
    --fs-xs: 0.95rem;
    --fs-sm: 1.05rem;
    --fs-base: 1.15rem;
    --fs-md: 1.3rem;
    --fs-lg: 1.6rem;
    --fs-xl: 2rem;
    --fs-2xl: 2.6rem;
    --lh-tight: 1.25;
    --lh-normal: 1.6;
    --lh-relaxed: 1.8;

    --space-xs: 0.5rem;
    --space-sm: 1rem;
    --space-md: 1.5rem;
    --space-lg: 2.5rem;
    --space-xl: 4rem;

    --brand-dark: #1E4D2B;
    --brand: #2E7D32;
}}

* {{
    font-family: 'Poppins', sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

/* إزالة الهوامش والحشوات من Streamlit */
html, body, .stApp {{
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
    overflow-x: hidden;
    overflow-y: auto;
    font-size: 17px; /* modest base bump: everything below scales from this */
}}

.stAppViewContainer, .stAppViewBlockContainer, .stMainBlockContainer {{
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
}}

.black-container {{
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    max-width: 100% !important;
    width: 100% !important;
}}

header[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
#MainMenu {{ visibility: hidden !important; }}
footer {{ visibility: hidden !important; }}
.stAppViewContainer {{
    padding-top: 0 !important;
    margin-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}}
section.main {{ padding-top: 0 !important; margin-top: 0 !important; }}
div.block-container {{
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}}
[data-testid="stAppViewBlockContainer"] {{ padding: 0 !important; margin: 0 !important; }}

/* Bring Streamlit's own widget text (buttons, radios, inputs, selects)
   up to the same scale, using documented data-testid hooks rather than
   generated internal class names. */
[data-testid="stButton"] button p,
[data-testid="stFormSubmitButton"] button p {{
    font-size: var(--fs-base) !important;
    font-weight: 600 !important;
}}
[data-testid="stRadio"] label p {{
    font-size: var(--fs-base) !important;
}}
[data-testid="stTextInput"] input {{
    font-size: var(--fs-base) !important;
}}
[data-testid="stSelectbox"] div[data-baseweb="select"] * {{
    font-size: var(--fs-base) !important;
}}
[data-testid="stFileUploader"] section button p {{
    font-size: var(--fs-base) !important;
}}

/* ===== NAVIGATION BAR =====
   Real Streamlit container (see centered_section) holding a genuine
   st.button for language switching, plus plain anchor links for
   smooth in-page scrolling. Fixed + translucent, sits above everything. */
.st-key-site-nav {{
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 1000;
    background: rgba(10, 22, 13, 0.6);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
}}
.st-key-site-nav [data-testid="stHorizontalBlock"] {{
    align-items: center;
    max-width: 1300px;
    margin: 0 auto;
    padding: 0.65rem 2rem;
    gap: 1rem;
    flex-wrap: nowrap !important;
}}
.nav-logo {{
    font-weight: 800;
    font-size: var(--fs-md);
    color: #FFFFFF;
    white-space: nowrap;
}}
.nav-logo .light {{ font-weight: 300; opacity: 0.7; }}
.nav-logo-img {{
    height: 44px;
    width: auto;
    display: block;
}}
.nav-links {{
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1.6rem;
}}
.nav-links a {{
    color: #FFFFFF;
    text-decoration: none;
    font-weight: 600;
    font-size: var(--fs-sm);
    opacity: 0.85;
    transition: opacity 0.2s ease;
    white-space: nowrap;
}}
.nav-links a:hover {{ opacity: 1; }}
.st-key-site-nav [data-testid="stButton"] {{ display: flex; justify-content: flex-end; }}
.st-key-site-nav [data-testid="stButton"] button {{
    background: rgba(255,255,255,0.14) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    color: #FFFFFF !important;
    border-radius: 30px !important;
    padding: 0.4rem 1.3rem !important;
    font-weight: 600 !important;
}}
.st-key-site-nav [data-testid="stButton"] button:hover {{
    background: rgba(255,255,255,0.24) !important;
}}
@media (max-width: 860px) {{
    .nav-links {{ display: none; }}
    .st-key-site-nav [data-testid="stHorizontalBlock"] {{
        flex-direction: row !important;
        justify-content: space-between !important;
    }}
    .st-key-site-nav [data-testid="column"]:nth-child(2) {{
        display: none !important;
    }}
}}

/* ===== HERO SECTION ===== */
.hero-section {{
    width: 100vw;
    min-height: 100vh;
    margin: 0;
    padding: 0;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    overflow: hidden;
    background: #0A160D; /* fallback shown for an instant before the first slide fades in */
}}

/* طبقة الشرائح: نفس الصور الأربعة الموجودة، بتتحرك أفقيًا بأسلوب الكاروسيل -
   الصورة الحالية تخرج لليسار فى نفس لحظة دخول اللى بعدها من اليمين - CSS بحت،
   بدون أى تأثير على حجم أو تخطيط قسم الـ Hero */
.hero-bg-slideshow {{
    position: absolute;
    inset: 0;
    z-index: 0;
    overflow: hidden;
}}
.hero-bg-slide {{
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    transform: translateX(100%);
    animation: heroSlide 12s cubic-bezier(0.65, 0, 0.35, 1) infinite;
    animation-fill-mode: both;
    will-change: transform;
}}
.hero-bg-slide:nth-child(1) {{ animation-delay: 0s; }}
.hero-bg-slide:nth-child(2) {{ animation-delay: 3s; }}
.hero-bg-slide:nth-child(3) {{ animation-delay: 6s; }}
.hero-bg-slide:nth-child(4) {{ animation-delay: 9s; }}

@keyframes heroSlide {{
    0%      {{ transform: translateX(100%); }}   /* off-screen right, about to enter */
    6.7%    {{ transform: translateX(0%); }}      /* slid fully into view */
    25%     {{ transform: translateX(0%); }}      /* holds in place, fully visible */
    31.7%   {{ transform: translateX(-100%); }}   /* pushed out to the left, in sync with the next slide entering */
    100%    {{ transform: translateX(-100%); }}   /* stays off-screen left for the rest of the loop */
}}

/* نفس التعتيم الداكن اللى كان متضمن جوه background-image قبل كده، دلوقتي
   طبقة مستقلة فوق الشرائح عشان يفضل شغال مع كل صورة بيتم تبديلها */
.hero-overlay {{
    position: absolute;
    inset: 0;
    background: linear-gradient(rgba(0,0,0,.45), rgba(0,0,0,.45));
    z-index: 1;
}}

.hero-content {{
    position: relative;
    z-index: 2;
    padding-top: 70px; /* breathing room under the fixed nav bar */
}}
.hero-title {{
    font-size: clamp(2.5rem, 8vw, 5.5rem);
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: 2px;
    text-shadow: 0 4px 20px rgba(0,0,0,0.2);
    margin-bottom: 0.2rem;
}}
.hero-slogan {{
    font-size: clamp(1.2rem, 4vw, 2.2rem);
    font-weight: 700;
    color: #E8F5E9;
    margin-bottom: 0.5rem;
    letter-spacing: 1px;
}}
.hero-sub {{
    font-size: clamp(1rem, 3vw, var(--fs-lg));
    color: #C8E6C9;
    font-weight: 400;
    margin-bottom: 2rem;
}}
.hero-btn {{
    background: rgba(40, 43, 27, 1);
    color: #F7FBF7;
    padding: 0.8rem 3rem;
    border-radius: 50px;
    font-weight: 700;
    font-size: var(--fs-base);
    border: none;
    box-shadow: 0 6px 20px rgba(40, 43, 27, 0.4);
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
}}
.hero-btn:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(40, 43, 27, 0.5);
    color: #F7FBF7;
}}

/* ===== ABOUT SECTION ===== */
.about-section {{
    background: #FFFFFF;
    padding: var(--space-xl) 2rem;
    text-align: center;
}}
.about-title {{
    font-size: clamp(1.8rem, 5vw, var(--fs-2xl));
    color: var(--brand-dark);
    font-weight: 800;
    margin-bottom: var(--space-sm);
}}
.about-text {{
    max-width: 820px;
    margin: 0 auto;
    font-size: var(--fs-base);
    line-height: var(--lh-relaxed);
    color: #4A5A4A;
}}

/* ===== TIPS SECTION (Quick Tips — premium infographic redesign) ===== */
.tips-section {{
    position: relative;
    background: linear-gradient(180deg, #FFFFFF 0%, #FBFDFB 55%, #FFFFFF 100%);
    padding: 3rem 2rem 5.5rem;
    overflow: visible;
}}

/* -- background layer: one continuous organic green wave band + decorations -- */
.tips-bg {{
    position: absolute;
    inset: 0;
    overflow: hidden;
    z-index: 0;
    pointer-events: none;
    border-radius: inherit;
}}
.tips-bg-wave {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
}}
.tips-cow-silhouette {{
    position: absolute;
    right: -4%;
    top: 12%;
    height: 78%;
    width: auto;
    opacity: 0.08;
    z-index: 1;
}}
.tips-dotted-curve {{
    position: absolute;
    left: 0;
    top: 4%;
    width: 42%;
    height: 40%;
    opacity: 0.35;
    z-index: 1;
}}
.tips-paw {{
    position: absolute;
    opacity: 0.16;
    z-index: 1;
}}
.tips-paw svg {{ width: 100%; height: 100%; }}
.tips-paw-1 {{ width: 46px; height: 46px; left: 4%; bottom: 10%; }}
.tips-paw-2 {{ width: 34px; height: 34px; left: 7.5%; bottom: 17%; transform: rotate(-18deg); }}
.tips-paw-3 {{ width: 40px; height: 40px; right: 6%; top: 30%; opacity: 0.20; }}

/* -- floating glass header panel: straddles the white/green boundary -- */
.tips-header-panel {{
    position: relative;
    z-index: 3;
    max-width: 620px;
    margin: -60px auto 3.75rem;
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 32px;
    padding: 2.2rem 2.5rem 2rem;
    text-align: center;
    box-shadow: 0 24px 60px rgba(23, 77, 44, 0.16), 0 4px 16px rgba(23, 77, 44, 0.08);
}}
.tips-title {{
    color: #174D2C;
    font-size: clamp(1.8rem, 5vw, var(--fs-2xl));
    font-weight: 800;
    text-align: center;
    letter-spacing: 3px;
}}
.tips-sub {{
    color: #2E7D32;
    text-align: center;
    font-size: var(--fs-md);
    font-weight: 500;
    margin-top: 0.4rem;
}}

/* -- workflow grid: 3 illustrated cards connected by circular arrow links -- */
.tips-grid {{
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    align-items: center;
    gap: 0.5rem;
    max-width: 1220px;
    width: 100%;
    margin: 0 auto;
    margin-top: -30px;
}}

.tip-arrow {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);
    border: 1.5px solid rgba(255, 255, 255, 0.55);
    color: #FFFFFF;
    justify-self: center;
}}

.tip-arrow svg {{
    width: 20px;
    height: 20px;
}}

.tip-card {{
    position: relative;
    background: #FFFFFF;
    border-radius: 30px;
    padding: 2.4rem 1.8rem 2.1rem;
    text-align: center;
    box-shadow: 0 22px 48px rgba(10, 30, 15, 0.20);
    transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1),
                box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    min-height: 430px;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
}}

.tip-card:hover {{
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 30px 60px rgba(10, 30, 15, 0.26);
}}

.tip-badge {{
    position: absolute;
    top: -20px;
    inset-inline-start: 26px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #174D2C;
    color: #EAF6E8;
    font-size: var(--fs-xs);
    font-weight: 800;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 18px rgba(23, 77, 44, 0.45);
}}

.tip-illustration {{
    width: 100%;
    max-width: 240px;
    aspect-ratio: 4 / 3;
    margin: 0.6rem auto 1.3rem;
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.tip-illustration img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}

.tip-card h3 {{
    color: #174D2C;
    font-weight: 700;
    font-size: var(--fs-lg);
    margin-bottom: 0.6rem;
}}

.tip-card p {{
    color: #55655A;
    font-size: var(--fs-base);
    line-height: var(--lh-normal);
    font-weight: 400;
    max-width: 320px;
    margin: 0 auto;
    flex-grow: 1;
}}


/* -- responsive: tablet spacing, mobile vertical stack -- */
@media (max-width: 980px) {{
    .tips-cow-silhouette {{ opacity: 0.05; }}
    .tips-grid {{
        grid-template-columns: 1fr;
        max-width: 480px;
        gap: 0;
    }}
    .tip-arrow {{
        margin: 0.6rem auto;
    }}
    .tip-arrow svg {{ transform: rotate(90deg); }}
}}
@media (max-width: 640px) {{
    .tips-section {{ padding: 3.5rem 1.2rem 4rem; }}
    .tips-header-panel {{ padding: 1.7rem 1.6rem 1.5rem; border-radius: 24px; margin-bottom: 2.5rem; }}
    .tip-card {{ padding: 2.1rem 1.4rem 1.8rem; }}
    .tips-paw-1, .tips-paw-2 {{ display: none; }}
}}

/* ===== DIAGNOSIS SECTION (رفع الصورة + الأسئلة + النتيجة) ===== */
.st-key-diagnosis-section{{
    background:#F4F8F5;
    direction:{DIR};
    padding:60px 0;
}}
.st-key-diagnosis-wrap{{
    width:min(1100px,92%);
    margin:auto;
}}
/* st.container() adds its own flex-gap block around children; remove the
   extra vertical gap so spacing still matches the original design */
.st-key-diagnosis-section, .st-key-diagnosis-wrap {{
    gap: 0;
}}
.step-badge {{
    display: inline-block;
    background: #1E4D2B;
    color: #FFFFFF;
    padding: 5px 16px;
    border-radius: 20px;
    font-size: var(--fs-xs);
    font-weight: 600;
    margin-bottom: 0.8rem;
}}

/* بطاقة عامة بيضاء تستخدم لكل الخطوات */
.upload-card, .questions-card, .result-card {{
    background: #FFFFFF;
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}}
.upload-card h2, .questions-card h2, .result-card h2 {{
    color: #1E4D2B;
    font-size: var(--fs-lg);
    font-weight: 700;
    margin-bottom: 0.3rem;
    text-align: start;
}}
.upload-card p.card-sub, .questions-card p.card-sub {{
    color: #6B7B6B;
    font-size: var(--fs-base);
    line-height: var(--lh-normal);
    margin-bottom: 1.2rem;
    text-align: start;
}}

/* منطقة السحب والإسقاط */
.dropzone-visual {{
    border: 2px dashed #A5D6A7;
    border-radius: 20px;
    background: #F6FBF6;
    padding: 2.2rem 1rem 1.6rem 1rem;
    text-align: center;
    margin-bottom: var(--space-md); /* clear separation from the upload button below */
}}
.dropzone-cloud {{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: #E8F5E9;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 auto 0.8rem auto;
}}
.dropzone-title {{
    color: #1E4D2B;
    font-weight: 700;
    font-size: var(--fs-md);
    margin-bottom: 0.3rem;
}}
.dropzone-caption {{
    color: #8A9A8A;
    font-size: var(--fs-sm);
    margin-bottom: 0.8rem;
}}

/* إخفاء نص الـ Drag&Drop الأصلى بتاع Streamlit عشان نستخدم تصميمنا بس */
[data-testid="stFileUploaderDropzoneInstructions"] {{
    display: none !important;
}}
[data-testid="stFileUploader"] section {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    display: flex;
    justify-content: center; /* centers the native "Browse files" button */
}}
[data-testid="stFileUploader"] button {{
    background: #2E7D32 !important;
    color: white !important;
    border-radius: 30px !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
}}
/* Balanced spacer between the upload button and whatever comes next
   (thumbnails or the Continue button) - replaces ad-hoc st.write("") gaps. */
.upload-gap {{
    height: var(--space-lg);
}}

/* thumbnails preview */
.thumb-card {{
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    margin-bottom: 0.5rem;
}}
.thumb-card img {{
    width: 100%;
    height: 110px;
    object-fit: cover;
    display: block;
}}

/* أسئلة */
.question-block {{
    margin-bottom: 1.4rem;
    text-align: start;
}}
.question-label {{
    color: #1E4D2B;
    font-weight:700;
    font-size:22px;
    margin-bottom:10px;
}}
div[data-testid="stForm"] {{
    border: none;
    padding: 0;
}}
div[role="radiogroup"] label p{{
    font-size:18px !important;
    font-weight:500;
    color: #1E4D2B !important;
}}
div[data-baseweb="select"]{{
    font-size:18px;
}}

/* ===== Question Buttons ===== */
div[data-testid="stForm"] button {{
    border-radius: 12px;
    height: 48px;
    font-weight: 600;
    font-size: 15px;
}}
div[data-testid="stForm"] button[kind="secondary"] {{
    border: 1px solid #1E4D2B;
    color: #1E4D2B;
    background: white;
}}
div[data-testid="stForm"] button[kind="primary"] {{
    border-radius: 12px;
}}

/* "Show Diagnosis Result" / "Back to Upload": use_container_width=True makes
   Streamlit stretch both the column and the button to fill the row's fixed
   1.7/1.3 split. Scoped to this one button group (via the real container key
   below) so nothing else on the page is touched: every layer between the
   row and the button text is forced back to its natural content width, and
   the row is centered with a small gap instead of a hard column split. */
.st-key-result-action-buttons [data-testid="stHorizontalBlock"] {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 12px !important;
    flex-wrap: wrap !important;
    width: auto !important;
}}
.st-key-result-action-buttons [data-testid="stColumn"],
.st-key-result-action-buttons [data-testid="column"] {{
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
}}
.st-key-result-action-buttons div[data-testid="stFormSubmitButton"] {{
    display: inline-flex !important;
    width: auto !important;
}}
.st-key-result-action-buttons button {{
    width: auto !important;
    height: auto !important;
    min-height: 48px !important;
    padding: 10px 16px !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
}}
.st-key-result-action-buttons button p {{
    white-space: nowrap !important;
}}


/* نتيجة التشخيص - بطاقة بأسلوب مرجعى */
.result-verdict {{
    font-size: clamp(2rem, 6vw, 3rem);
    font-weight: 900;
    margin-bottom: 1.5rem;
}}
.result-conf-row {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 0.4rem;
    text-align: start;
}}
.result-conf-label {{ color: #6B7B6B; font-size: var(--fs-sm); }}
.result-conf-value {{ font-size: var(--fs-xl); font-weight: 800; color: #1E4D2B; }}
.result-progress-bg {{
    width: 100%;
    height: 10px;
    background: #E8F0E9;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 1.2rem;
}}
.result-progress-fill {{ height: 100%; border-radius: 10px; }}
.result-meta {{
    display: flex;
    justify-content: space-between;
    border-top: 1px solid #EEF2EE;
    padding-top: 0.9rem;
    font-size: var(--fs-2xs);
    color: #8A9A8A;
    text-align: start;
}}

/* صورة الحيوان أعلى بطاقة النتيجة - بتترندر خارج result-card عشان متبقاش
   جوه صندوق أبيض بمسافات فاضية حواليها؛ الصورة نفسها بس بحواف دائرية. */
.result-image-wrap {{
    position:relative;
    border-radius:22px;
    overflow:hidden;
    margin:0 0 1.5rem;
    width:100%;
    background:transparent;
}}
.result-image-wrap img {{
    width: 100%;
    height: 430px;
    object-fit: cover;
    display: block;
}}
.result-image-tag {{
    position: absolute;
    top: 12px;
    right: 12px;
    background: #1E4D2B;
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 16px;
}}

/* جرس التنبيهات */
.bell-wrap {{ display: flex; justify-content: center; margin-bottom: 0.6rem; }}

/* =====================================================
   VETERINARY RECOMMENDATION
   ===================================================== */

.st-key-vet-panel{{
    position:fixed;
    inset-inline-end:25px;
    bottom:25px;
    width:560px;
    max-width:95vw;
    z-index:99999;
    animation:slideUp .35s ease;
}}
/* close (X) button now lives inside the same fixed panel as the card, sitting
   snugly in its top-right corner instead of appearing elsewhere on the page. */
.st-key-vet-panel [data-testid="stHorizontalBlock"] {{
    margin-bottom:-6px;
}}
.st-key-close_recommendation button {{
    width:32px;
    height:32px;
    min-width:32px;
    padding:0 !important;
    border-radius:50%;
    border:1px solid #E6ECE8;
    background:#fff;
    color:#1E4D2B;
    line-height:1;
}}
.st-key-close_recommendation button p {{
    font-size:14px !important;
}}

@keyframes slideUp{{
    from{{
        transform:translateY(40px);
        opacity:0;
    }}
    to{{
        transform:translateY(0);
        opacity:1;
    }}
}}
.vet-card{{
    width:100%;
    max-height:85vh;
    overflow-y:auto;
    background:#fff;
    border-radius:22px;
    border:1px solid #E6ECE8;
    box-shadow:0 18px 45px rgba(0,0,0,.15);
}}
.vet-header{{
    display:flex;
    align-items:center;
    gap:20px;
    padding:26px;
    background:linear-gradient(135deg,#F7FBF7,#FFFFFF);
    border-bottom:1px solid #E8F0E8;
}}
.vet-icon{{ 
    width:44px;
    height:44px;
    border-radius:14px;
    background:#EDF7EF;
    color:#1E4D2B;
    font-size:20px;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-shrink:0;
    line-height:1;
}}
.vet-title{{
    font-size:28px;
    font-weight:900;
    color:#1E4D2B;
}}
.vet-status{{
    margin-top:6px;
    font-size:24px;
    font-weight:900;
    text-shadow:0 1px 2px rgba(0,0,0,.08);
}}
.vet-box{{
    margin:22px;
    padding:26px;
    border-radius:18px;
    background:#F9FCF9;
    border:1px solid #E6EFE7;
    transition:all .25s ease;
}}
.vet-box:hover{{
    transform:translateY(-2px);
    box-shadow:0 8px 22px rgba(0,0,0,.06);
}}
.vet-summary{{
    background:#FFF9E8;
    border-left:6px solid #F4B400;
}}
.vet-actions{{
    background:#F1FBF3;
    border-left:6px solid #22C55E;
}}
.vet-contact{{
    background:#EEF6FF;
    border-left:6px solid #3B82F6;
}}
.vet-box h4{{
    margin:0 0 16px;
    font-size:22px;
    font-weight:900;
    color:#1E4D2B;
}}
.vet-box p{{
    margin:0;
    font-size:18px;
    line-height:2;
    color:#354635;
    font-weight:500;
}}

/* ===== FOOTER ===== */
.site-footer {{
    background: #12271A;
    color: #E8F5E9;
    padding: var(--space-xl) 2rem var(--space-md);
    direction: {DIR};
}}
.footer-inner {{
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: var(--space-lg);
}}
.footer-col {{ flex: 1; min-width: 240px; }}
.footer-col h4 {{
    font-size: var(--fs-md);
    margin-bottom: 0.6rem;
    color: #FFFFFF;
}}
.footer-col p {{
    font-size: var(--fs-sm);
    line-height: var(--lh-normal);
    color: #B8CCB9;
    margin-bottom: 0.3rem;
}}
.footer-bottom {{
    text-align: center;
    margin-top: var(--space-lg);
    padding-top: 1.4rem;
    border-top: 1px solid rgba(255,255,255,0.1);
    font-size: var(--fs-2xs);
    color: #8AA88C;
}}

@media (max-width: 640px) {{
    .st-key-diagnosis-wrap {{ max-width: 100%; }}
    .upload-card, .questions-card, .result-card {{ padding: 1.3rem; }}
    .st-key-vet-panel {{ left: 12px; right: 12px; inset-inline-end: 12px; width: auto; bottom: 12px; }}
    .footer-inner {{ flex-direction: column; }}
}}


</style>
""", unsafe_allow_html=True)

# =========================
# 3. تحميل البيانات والأسئلة
# =========================
questions = load_questions()

phone_numbers = {
    'Cairo': '23646120 / 23647652', 'Giza': '35851635', 'Qalyubia': '133261186',
    'Monufia': '482175059', 'Sharqia': '552302231', 'Gharbia': '403305747',
    'Kafr El Sheikh': '473234359', 'Dakahlia': '502244346', 'Beheira': '453288126',
    'Alexandria': '34970992', 'Fayoum': '842169102', 'Beni Suef': '822142366',
    'Minya': '862363718', 'Assiut': '882323699', 'Sohag': '932323103',
    'Qena': '963337975', 'Luxor': '9523844339', 'Aswan': '972428061'
}

# =========================
# 4. دوال عرض النتائج والتوصيات
# =========================
IMAGE_THRESHOLD = 0.5
SYMPTOM_THRESHOLD = 0.42

# لون وأيقونة كل تصنيف (مستقلة عن اللغة) - النص المعروض يُترجم من T["result"]["verdicts"]
VERDICT_STYLE = {
    "healthy": {"icon": "✅", "color": "#2E7D32", "bg": "#E8F5E9"},
    "suspected": {"icon": "⚠️", "color": "#F9A825", "bg": "#FFF8E1"},
    "infected": {"icon": "🔴", "color": "#C62828", "bg": "#FFEBEE"},
}

# خريطة أسماء المحافظات بالعربى إلى المفاتيح الإنجليزية فى قاموس أرقام التليفونات
ARABIC_GOV_MAP = {
    "القاهرة": "Cairo", "الجيزة": "Giza", "القليوبية": "Qalyubia",
    "المنوفية": "Monufia", "الشرقية": "Sharqia", "الغربية": "Gharbia",
    "كفر الشيخ": "Kafr El Sheikh", "الدقهلية": "Dakahlia", "البحيرة": "Beheira",
    "الاسكندرية": "Alexandria", "الإسكندرية": "Alexandria", "الفيوم": "Fayoum",
    "بني سويف": "Beni Suef", "المنيا": "Minya", "اسيوط": "Assiut", "أسيوط": "Assiut",
    "سوهاج": "Sohag", "قنا": "Qena", "الاقصر": "Luxor", "الأقصر": "Luxor",
    "اسوان": "Aswan", "أسوان": "Aswan",
}
GOV_EN_TO_AR = {
    "Cairo": "القاهرة", "Giza": "الجيزة", "Qalyubia": "القليوبية", "Monufia": "المنوفية",
    "Sharqia": "الشرقية", "Gharbia": "الغربية", "Kafr El Sheikh": "كفر الشيخ",
    "Dakahlia": "الدقهلية", "Beheira": "البحيرة", "Alexandria": "الإسكندرية",
    "Fayoum": "الفيوم", "Beni Suef": "بني سويف", "Minya": "المنيا", "Assiut": "أسيوط",
    "Sohag": "سوهاج", "Qena": "قنا", "Luxor": "الأقصر", "Aswan": "أسوان",
}


def match_governorate(user_text):
    """يحاول مطابقة النص/الاختيار (عربى أو إنجليزى) مع قاموس أرقام التليفونات.
    يرجّع المفتاح الإنجليزى القياسى للمحافظة (en_key) ورقم التليفون، بغض النظر
    عن اللغة التى اختار بها المستخدم - العرض باللغة الحالية يتم لاحقًا."""
    if not user_text:
        return None, None
    text = user_text.strip()
    for key in phone_numbers:
        if text.lower() == key.lower():
            return key, phone_numbers[key]
    for ar_name, en_key in ARABIC_GOV_MAP.items():
        if ar_name in text or text in ar_name:
            return en_key, phone_numbers.get(en_key)
    return None, None


def get_verdict(image_fmd_prob, symptom_prob):
    """يحدد التصنيف النهائى (سليم / مشتبه به / مصاب) وقيمة الثقة."""
    image_positive = image_fmd_prob >= IMAGE_THRESHOLD
    symptom_positive = symptom_prob >= SYMPTOM_THRESHOLD

    if image_positive and symptom_positive:
        tier = "infected"
        confidence = max(image_fmd_prob, symptom_prob) * 100
    elif (not image_positive) and (not symptom_positive):
        tier = "healthy"
        confidence = (1 - max(image_fmd_prob, symptom_prob)) * 100
    else:
        tier = "suspected"
        confidence = ((image_fmd_prob + symptom_prob) / 2) * 100

    return tier, confidence


def build_recommendation(tier, image_fmd_prob, symptom_prob, governorate_text, lang):
    """يبنى نص التوصية الكامل: السبب + الإجراء المطلوب + رقم تليفون المحافظة،
    باللغة الحالية. يُستدعى وقت العرض (مش وقت التشخيص) عشان لو المستخدم غيّر
    اللغة بعدين، النص يتحدث فورًا من نفس الأرقام المخزنة بدون أى حسابات جديدة."""
    rec = TRANSLATIONS[lang]["recommendation"]

    en_key, phone = match_governorate(governorate_text)
    if en_key:
        gov_display = en_key if lang == "en" else GOV_EN_TO_AR.get(en_key, en_key)
    else:
        gov_display = governorate_text or ""

    reason = rec["reason_template"].format(
        image_pct=image_fmd_prob * 100, symptom_pct=symptom_prob * 100
    )
    action = rec[f"action_{tier}"]

    if phone:
        contact = rec["contact_found"].format(gov=gov_display, phone=phone)
    else:
        contact = rec["contact_not_found"]

    return reason, action, contact

# =========================
# 5. إعدادات اضافية لحالة الجلسة
# =========================
if "stage" not in st.session_state:
    st.session_state.stage = "upload"          # upload -> questions -> result
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []       # list of bytes
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "result" not in st.session_state:
    st.session_state.result = None
if "show_notification" not in st.session_state:
    st.session_state.show_notification = False


def restart_flow():
    st.session_state.stage = "upload"
    st.session_state.uploaded_images = []
    st.session_state.answers = {}
    st.session_state.result = None
    st.session_state.show_notification = False


# =========================
# 6. شريط التنقل (Navigation Bar)
# =========================
# Real Streamlit container + real columns: the logo/links are plain HTML
# (no interactivity needed), the language switch is a genuine st.button so
# it can actually change st.session_state and rerun - unlike the previous
# `onclick="window.location.reload()"` button, which never touched Python.
with centered_section("site-nav"):
    nav_logo_col, nav_links_col, nav_lang_col = st.columns([2, 5, 2])

    with nav_logo_col:
        st.markdown(
            f'<div class="nav-logo"><img class="nav-logo-img" src="data:{logo_image["mime"]};base64,{logo_image["data"]}" alt="BoviScan logo"></div>',
            unsafe_allow_html=True,
        )

    with nav_links_col:
        st.markdown(f"""
            <div class="nav-links">
                <a href="#home">{T['nav']['home']}</a>
                <a href="#about">{T['nav']['about']}</a>
                <a href="#tips">{T['nav']['tips']}</a>
                <a href="#diagnosis">{T['nav']['diagnosis']}</a>
                <a href="#diagnosis">{T['nav']['results']}</a>
                <a href="#contact">{T['nav']['contact']}</a>
            </div>
        """, unsafe_allow_html=True)

    with nav_lang_col:
        if st.button(f"🌐 {T['nav']['lang_switch']}", key="lang_toggle_btn"):
            toggle_lang()
            st.rerun()

# =========================
# 7. الهيرو (الغلاف)
# =========================
hero_slides_html = ""
for _hero_img in hero_images:
    _mime = _hero_img["mime"]
    _data = _hero_img["data"]
    hero_slides_html += f'<div class="hero-bg-slide" style="background-image:url(\'data:{_mime};base64,{_data}\');"></div>'

st.markdown(f"""
<div class="hero-section" id="home">
    <div class="hero-bg-slideshow">
        {hero_slides_html}
    </div>
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-title">{T['hero']['title']}</div>
        <div class="hero-slogan">{T['hero']['slogan']}</div>
        <div class="hero-sub">{T['hero']['sub']}</div>
        <a href="#diagnosis" class="hero-btn">{T['hero']['cta']}</a>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 8. عن المرض (About)
# =========================
st.markdown(f"""
<div class="about-section" id="about">
    <div class="about-title">{T['about']['title']}</div>
    <div class="about-text">{T['about']['text']}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# 9. نصائح سريعة
# =========================
st.markdown(f"""
<div class="tips-section" id="tips">
<div class="tips-bg">
<svg class="tips-bg-wave" viewBox="0 0 1200 700" preserveAspectRatio="none" aria-hidden="true">
<defs>
<linearGradient id="tipsGreenGrad" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#123C22"/>
<stop offset="0.45" stop-color="#174D2C"/>
<stop offset="1" stop-color="#2E7D32"/>
</linearGradient>
</defs>
<path d="M0,90 C200,20 380,180 600,168 C820,156 1000,58 1200,80 L1200,600 C1000,662 820,558 600,720 C380,666 200,556 0,598 Z" fill="url(#tipsGreenGrad)"></path></svg>
<svg class="tips-cow-silhouette" viewBox="0 0 420 500" aria-hidden="true">
<g fill="#FFFFFF">
<ellipse cx="180" cy="260" rx="150" ry="90"></ellipse>
<ellipse cx="330" cy="200" rx="70" ry="60"></ellipse>
<ellipse cx="300" cy="150" rx="18" ry="26" transform="rotate(-20 300 150)"></ellipse>
<ellipse cx="365" cy="150" rx="18" ry="26" transform="rotate(20 365 150)"></ellipse>
<rect x="70" y="330" width="26" height="120" rx="10"></rect>
<rect x="150" y="340" width="26" height="120" rx="10"></rect>
<rect x="230" y="340" width="26" height="120" rx="10"></rect>
<rect x="290" y="330" width="26" height="120" rx="10"></rect>
<path d="M40 250 C10 260 0 300 20 330 C10 340 15 355 30 350" stroke="#FFFFFF" stroke-width="10" fill="none" stroke-linecap="round"></path>
</g>
</svg>
<svg class="tips-dotted-curve" viewBox="0 0 400 300" aria-hidden="true">
<path d="M-20 260 C80 320 160 180 260 220 C320 244 360 160 420 140" fill="none" stroke="#174D2C" stroke-width="2" stroke-dasharray="2 10" stroke-linecap="round"></path>
</svg>
<div class="tips-paw tips-paw-1" style="color:rgba(255,255,255,0.9)">
<svg viewBox="0 0 40 40"><ellipse cx="20" cy="26" rx="11" ry="9" fill="currentColor"></ellipse><ellipse cx="8" cy="14" rx="4.5" ry="5.5" fill="currentColor"></ellipse><ellipse cx="18" cy="8" rx="4.5" ry="5.5" fill="currentColor"></ellipse><ellipse cx="28" cy="9" rx="4.5" ry="5" fill="currentColor"></ellipse><ellipse cx="35" cy="17" rx="4" ry="5" fill="currentColor"></ellipse></svg>
</div>
<div class="tips-paw tips-paw-2" style="color:rgba(255,255,255,0.9)">
<svg viewBox="0 0 40 40"><ellipse cx="20" cy="26" rx="11" ry="9" fill="currentColor"></ellipse><ellipse cx="8" cy="14" rx="4.5" ry="5.5" fill="currentColor"></ellipse><ellipse cx="18" cy="8" rx="4.5" ry="5.5" fill="currentColor"></ellipse><ellipse cx="28" cy="9" rx="4.5" ry="5" fill="currentColor"></ellipse><ellipse cx="35" cy="17" rx="4" ry="5" fill="currentColor"></ellipse></svg>
</div>
<div class="tips-paw tips-paw-3" style="color:rgba(255,255,255,0.9)">
<svg viewBox="0 0 40 40"><ellipse cx="20" cy="26" rx="11" ry="9" fill="currentColor"></ellipse><ellipse cx="8" cy="14" rx="4.5" ry="5.5" fill="currentColor"></ellipse><ellipse cx="18" cy="8" rx="4.5" ry="5.5" fill="currentColor"></ellipse><ellipse cx="28" cy="9" rx="4.5" ry="5" fill="currentColor"></ellipse><ellipse cx="35" cy="17" rx="4" ry="5" fill="currentColor"></ellipse></svg>
</div>
<div class="tips-paw tips-paw-4" style="color:rgba(23,77,44,0.5)">
<svg viewBox="0 0 40 40"><ellipse cx="20" cy="26" rx="11" ry="9" fill="currentColor"></ellipse><ellipse cx="8" cy="14" rx="4.5" ry="5.5" fill="currentColor"></ellipse><ellipse cx="18" cy="8" rx="4.5" ry="5.5" fill="currentColor"></ellipse><ellipse cx="28" cy="9" rx="4.5" ry="5" fill="currentColor"></ellipse><ellipse cx="35" cy="17" rx="4" ry="5" fill="currentColor"></ellipse></svg>
</div>
</div>
<div class="tips-header-panel">
<div class="tips-title">{T['tips']['title']}</div>
<div class="tips-sub">{T['tips']['sub']}</div>
</div>
<div class="tips-grid">
<div class="tip-card">
<span class="tip-badge">01</span>
<div class="tip-illustration">
<!-- <svg viewBox="0 0 240 180" xmlns="http://www.w3.org/2000/svg"> -->
       <img
        src="data:{tips_1['mime']};base64,{tips_1['data']}"
        alt="Clean and Clear"
    >
</div>
<h3>{T['tips']['tip1_title']}</h3>
<p>{T['tips']['tip1_text']}</p>
</div>
<div class="tip-arrow">
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12 H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path><path d="M13 6 L19 12 L13 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
</div>
<div class="tip-card">
<span class="tip-badge">02</span>
<div class="tip-illustration">
   <img
        src="data:{tips_2['mime']};base64,{tips_2['data']}"
        alt="Wash and Dry"
    >
</div>
<h3>{T['tips']['tip2_title']}</h3>
<p>{T['tips']['tip2_text']}</p>

</div>
<div class="tip-arrow">
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12 H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path><path d="M13 6 L19 12 L13 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
</div>
<div class="tip-card">
<span class="tip-badge">03</span>
<div class="tip-illustration">
  <img
        src="data:{tips_3['mime']};base64,{tips_3['data']}"
        alt="Good Lighting"
    >
</div>
<h3>{T['tips']['tip3_title']}</h3>
<p>{T['tips']['tip3_text']}</p>

</div>
</div>
</div>
""", unsafe_allow_html=True)

# =========================
# 10/11. التشخيص: رفع الصورة → الأسئلة → النتيجة → التوصية
# =========================

st.markdown('<div id="diagnosis"></div>', unsafe_allow_html=True)
with centered_section("diagnosis-section"):
    with centered_section("diagnosis-wrap"):

        # =========================================================
        # الخطوة 1: رفع الصور
        # =========================================================
        if st.session_state.stage == "upload":
            st.markdown(f'<span class="step-badge">{T["upload"]["step_badge"]}</span>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="upload-card">
                <h2>{T['upload']['title']}</h2>
                <p class="card-sub">{T['upload']['subtitle']}</p>
                <div class="dropzone-visual">
                    <div class="dropzone-cloud">☁️</div>
                    <div class="dropzone-title">{T['upload']['dropzone_title']}</div>
                    <div class="dropzone-caption">{T['upload']['dropzone_caption']}</div>
                </div>
            """, unsafe_allow_html=True)

            new_files = st.file_uploader(
                T['upload']['dropzone_title'],
                type=["jpg", "jpeg", "png", "heic"],
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="uploader_widget",
            )

            if new_files:
                existing_names = {f["name"] for f in st.session_state.uploaded_images}
                for f in new_files:
                    if f.name not in existing_names:
                        st.session_state.uploaded_images.append({"name": f.name, "bytes": f.getvalue()})

            # مسافة متّزنة بين زر الرفع وأى محتوى بعده (صور مصغّرة أو زر المتابعة)
            st.markdown('<div class="upload-gap"></div>', unsafe_allow_html=True)

            # عرض الصور المرفوعة
            if st.session_state.uploaded_images:
                cols = st.columns([1, 2, 1])
                with cols[1]:
                    for idx, img_item in enumerate(st.session_state.uploaded_images):
                        st.markdown('<div class="thumb-card">', unsafe_allow_html=True)
                        st.image(img_item["bytes"], use_container_width=True)

                        if st.button(
                            T['upload']['remove'],
                            key=f"remove_{idx}",
                            use_container_width=False
                        ):
                            st.session_state.uploaded_images.pop(idx)
                            st.rerun()

                        st.markdown('<div class="upload-gap"></div>', unsafe_allow_html=True)

                    # زر المتابعة
                    if st.session_state.uploaded_images:
                        if st.button(T['upload']['continue'], type="primary", use_container_width=True):
                            st.session_state.stage = "questions"
                            st.rerun()
                        else:
                            st.button(T['upload']['continue'], disabled=True, use_container_width=False,
                                      help=T['upload']['continue_help'])
                    st.markdown('</div>', unsafe_allow_html=True)  # close upload-card

        # =========================================================
        # الخطوة 2: الأسئلة (كلها تظهر مرة واحدة)
        # =========================================================
        elif st.session_state.stage == "questions":
            st.markdown(f'<span class="step-badge">{T["questions"]["step_badge"]}</span>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="questions-card">
                <h2>{T['questions']['title']}</h2>
                <p class="card-sub">{T['questions']['subtitle']}</p>
            """, unsafe_allow_html=True)

            cols = st.columns([1, 2, 1])
            with cols[1]:
                with st.form("questions_form"):
                    form_answers = {}
                    for q in questions:
                        field = q["field"]
                        label = T["questions"]["fields"].get(field, q["question"])

                        st.markdown(f'<div class="question-block"><div class="question-label">{label}</div></div>',
                                    unsafe_allow_html=True)

                        if field == "governorate":
                            # آخر سؤال فى الاستبيان: dropdown بدل الحقل النصى الحر.
                            # الخيارات المعروضة تتبع اللغة الحالية، لكن match_governorate()
                            # تتعرف على الاسمين العربى والإنجليزى بنفس الكفاءة.
                            gov_options = (
                                sorted(phone_numbers.keys()) if LANG == "en"
                                else sorted(GOV_EN_TO_AR.values())
                            )
                            form_answers[field] = st.selectbox(
                                label, options=gov_options, index=None,
                                placeholder=T["questions"]["gov_placeholder"],
                                key=f"q_{field}", label_visibility="collapsed",
                            )
                        elif q["type"] == "text":
                            form_answers[field] = st.text_input(
                                label, key=f"q_{field}", label_visibility="collapsed",
                            )
                        elif field == "animal_type" or q["type"] == "multiple_choice":
                            opts = q["options"] if q["options"] else ["Cattle", "Goat", "Sheep"]
                            choice = st.radio(
                                label, options=opts, index=None,
                                format_func=lambda o: T["questions"]["animal_options"].get(o, o),
                                key=f"q_{field}", label_visibility="collapsed", horizontal=True,
                            )
                            form_answers[field] = choice
                        else:  # yes_no
                            choice = st.radio(
                                label, options=["yes", "no"], index=None,
                                format_func=lambda o: T["questions"]["yes"] if o == "yes" else T["questions"]["no"],
                                key=f"q_{field}", label_visibility="collapsed", horizontal=True,
                            )
                            form_answers[field] = choice

                    st.markdown("<br>", unsafe_allow_html=True)

                    col_space1, col_buttons, col_space2 = st.columns([1, 2.8, 1])

                    st.markdown("<br>", unsafe_allow_html=True)

                    left_space, buttons_col, right_space = st.columns([1, 3, 1])

                    with buttons_col:
                        with st.container(key="result-action-buttons"):
                            submit_col, back_col = st.columns([1.7, 1.3], gap="small")

                            with submit_col:
                                submitted = st.form_submit_button(
                                    T['questions']['submit'],
                                    type="primary",
                                    use_container_width=True
                                )

                            with back_col:
                                back_clicked = st.form_submit_button(
                                    T['questions']['back'],
                                    use_container_width=True
                                )
                    st.markdown('</div>', unsafe_allow_html=True)  # end questions-card

                    if submitted:
                        gov_text = form_answers.get("governorate")
                        if not gov_text:
                            st.error(T['questions']['gov_error'])
                        else:
                            st.session_state.answers = form_answers
                            with st.spinner("..."):
                                first_image_bytes = st.session_state.uploaded_images[0]["bytes"]
                                image_label, image_confidence, image_fmd_prob = predict_image(io.BytesIO(first_image_bytes))
                                symptom_prob = predict_symptoms(form_answers)
                                tier, confidence = get_verdict(float(image_fmd_prob), float(symptom_prob))
                                st.session_state.result = {
                                    "tier": tier,
                                    "confidence": confidence,
                                    "image_fmd_prob": float(image_fmd_prob),
                                    "symptom_prob": float(symptom_prob),
                                    "governorate_text": gov_text,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                }
                            st.session_state.stage = "result"
                            st.session_state.show_notification = True
                            st.rerun()

                    if back_clicked:
                        st.session_state.stage = "upload"
                        st.rerun()

        # =========================================================
        # الخطوة 3: النتيجة + التوصية
        # =========================================================
        elif st.session_state.stage == "result":
            result = st.session_state.result
            style = VERDICT_STYLE[result["tier"]]
            verdict_label = T["result"]["verdicts"][result["tier"]]

            _, result_action, _ = build_recommendation(
                result["tier"],
                result["image_fmd_prob"],
                result["symptom_prob"],
                result["governorate_text"],
                LANG,
            )

            # --- الصورة اللى اتبعتت + بطاقة النتيجة ---
            first_image_bytes = st.session_state.uploaded_images[0]["bytes"]
            img_b64 = base64.b64encode(first_image_bytes).decode()

            st.markdown(f"""
                <div class="result-image-wrap">
                    <img src="data:image/jpeg;base64,{img_b64}" />
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class="result-card">
                <h2 style='text-align:center;'>{T['result']['title']}</h2>
            """, unsafe_allow_html=True)
            st.markdown(
                f'<div class="result-verdict" style="color:{style["color"]};">{style["icon"]} {verdict_label}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"""
                <div class="vet-box vet-actions">
                    <h4>✅ Recommended Actions</h4>
                    <p>
                        {result_action.replace(chr(10), "<br>")}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class="result-meta">
                    <span></span>
                    <span>{T['result']['last_update']} {result['timestamp']}</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)  # end result-card

            # --- جرس التنبيهات (لإظهار/إخفاء التوصية) ---
            # --- أزرار النتيجة ---
            st.markdown('<div class="result-buttons">', unsafe_allow_html=True)

            if st.button(
                T['result']['new_diagnosis'],
                key="new_diag_btn",
                type="primary",
                use_container_width=True,
            ):
                restart_flow()
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # --- توصية الطبيب البيطرى: بطاقة توصية احترافية أسفل الشاشة ---
            if st.session_state.show_notification and st.session_state.result:
                result = st.session_state.result
                style = VERDICT_STYLE[result["tier"]]
                verdict_label = T["result"]["verdicts"][result["tier"]]

                reason, action, contact = build_recommendation(
                    result["tier"],
                    result["image_fmd_prob"],
                    result["symptom_prob"],
                    result["governorate_text"],
                    LANG,
                )

                # real st.container(key=...) so the close button becomes an
                # actual DOM sibling inside the same fixed-position panel as
                # the card, instead of a separate element in the page flow.
                with st.container(key="vet-panel"):
                    close_col1, close_col2 = st.columns([12, 1])

                    with close_col2:
                        if st.button("✕", key="close_recommendation"):
                            st.session_state.show_notification = False
                            st.rerun()

                    st.markdown(f"""
                    <div class="vet-card">
                        <div class="vet-header">
                            <div class="vet-icon">
                                {style["icon"]}
                            </div>
                            <div>
                                <div class="vet-title">
                                    Veterinary Recommendation
                                </div>
                                <div class="vet-status"
                                     style="color:{style['color']};">
                                    {verdict_label}
                                </div>
                            </div>
                        </div>
                        <div class="vet-box vet-contact">
                            <h4>☎ Contact</h4>
                            <p>
                                {contact.replace(chr(10), "<br>")}
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# =========================
# 12. الفوتر (تواصل معنا)
# =========================
st.markdown(f"""
<div class="site-footer" id="contact">
    <div class="footer-inner">
        <div class="footer-col">
            <h4>{T['footer']['about_title']}</h4>
            <p>{T['footer']['about_text']}</p>
        </div>
        <div class="footer-col">
            <h4>{T['footer']['contact_title']}</h4>
            <p>{T['footer']['contact_text']}</p>
            <p>{T['footer']['email_label']}: support@fmd-detect.app</p>
            <p>{T['footer']['hotline_label']}: {phone_numbers['Cairo']}</p>
        </div>
    </div>
    <div class="footer-bottom">{T['footer']['copyright']}</div>
</div>
""", unsafe_allow_html=True)