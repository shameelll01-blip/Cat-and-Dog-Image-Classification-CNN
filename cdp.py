import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import time
import base64
from io import BytesIO
 
st.set_page_config(
    page_title="PetVision AI",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)
 
# ── Glassmorphism CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');
 
/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 30%, #24243e 60%, #0f0c29 100%) !important;
    min-height: 100vh;
    font-family: 'Inter', sans-serif;
}
 
/* animated background orbs */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: -20%;
    left: -20%;
    width: 60vw;
    height: 60vw;
    background: radial-gradient(circle, rgba(120,80,255,0.18) 0%, transparent 70%);
    border-radius: 50%;
    animation: orb1 12s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}
 
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    bottom: -20%;
    right: -10%;
    width: 50vw;
    height: 50vw;
    background: radial-gradient(circle, rgba(0,200,200,0.14) 0%, transparent 70%);
    border-radius: 50%;
    animation: orb2 15s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}
 
@keyframes orb1 {
    0%   { transform: translate(0, 0) scale(1); }
    100% { transform: translate(6vw, 8vh) scale(1.15); }
}
@keyframes orb2 {
    0%   { transform: translate(0, 0) scale(1); }
    100% { transform: translate(-5vw, -6vh) scale(1.1); }
}
 
/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stSidebar"] { display: none; }
.block-container {
    padding: 2.5rem 2rem 3rem !important;
    max-width: 820px !important;
    margin: 0 auto !important;
    position: relative;
    z-index: 1;
}
 
/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    animation: fadeDown 0.8s cubic-bezier(.16,1,.3,1) both;
}
.hero-badge {
    display: inline-block;
    background: rgba(140,100,255,0.18);
    border: 1px solid rgba(140,100,255,0.35);
    color: #c4a8ff;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.35rem 1.1rem;
    border-radius: 999px;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(8px);
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.4rem, 6vw, 3.8rem);
    font-weight: 700;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 30%, #c4a8ff 70%, #7af4f4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.9rem;
}
.hero p {
    color: rgba(200,190,255,0.65);
    font-size: 1.05rem;
    font-weight: 400;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}
 
/* ── Glass card ── */
.glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 24px;
    padding: 2.2rem;
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    box-shadow:
        0 8px 40px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.12);
    animation: fadeUp 0.7s cubic-bezier(.16,1,.3,1) 0.15s both;
    margin-bottom: 1.5rem;
}
 
/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04) !important;
    border: 2px dashed rgba(140,100,255,0.4) !important;
    border-radius: 18px !important;
    padding: 1.5rem !important;
    transition: border-color 0.25s, background 0.25s;
    backdrop-filter: blur(10px);
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(140,100,255,0.75) !important;
    background: rgba(140,100,255,0.07) !important;
}
[data-testid="stFileUploader"] label {
    color: rgba(200,190,255,0.8) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] div span,
[data-testid="stFileUploaderDropzoneInstructions"] div small {
    color: rgba(180,170,230,0.6) !important;
}
[data-testid="stBaseButton-secondary"] {
    background: rgba(140,100,255,0.2) !important;
    border: 1px solid rgba(140,100,255,0.4) !important;
    color: #c4a8ff !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s;
}
[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(140,100,255,0.35) !important;
    border-color: rgba(140,100,255,0.7) !important;
}
 
/* ── Uploaded image ── */
[data-testid="stImage"] img {
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
}
 
/* ── Spinner ── */
[data-testid="stSpinner"] > div {
    color: #c4a8ff !important;
}
 
/* ── Result cards ── */
.result-card {
    border-radius: 18px;
    padding: 1.8rem 2rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid;
    animation: popIn 0.55s cubic-bezier(.16,1,.3,1) both;
    margin-top: 1rem;
}
.result-dog {
    background: linear-gradient(135deg, rgba(255,170,50,0.12) 0%, rgba(255,120,30,0.08) 100%);
    border-color: rgba(255,170,50,0.35);
    box-shadow: 0 0 40px rgba(255,150,30,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
}
.result-cat {
    background: linear-gradient(135deg, rgba(100,200,255,0.12) 0%, rgba(140,100,255,0.08) 100%);
    border-color: rgba(100,200,255,0.35);
    box-shadow: 0 0 40px rgba(100,200,255,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
}
.result-emoji {
    font-size: 3.5rem;
    line-height: 1;
    margin-bottom: 0.6rem;
    display: block;
    animation: bounce 0.6s cubic-bezier(.36,.07,.19,.97) 0.3s both;
}
.result-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}
.result-sub {
    color: rgba(200,190,255,0.6);
    font-size: 0.9rem;
    font-weight: 400;
    margin-bottom: 1.2rem;
}
 
/* confidence bar */
.conf-bar-wrap {
    background: rgba(255,255,255,0.07);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 1s cubic-bezier(.16,1,.3,1);
    animation: barGrow 1.1s cubic-bezier(.16,1,.3,1) 0.4s both;
}
.conf-bar-dog { background: linear-gradient(90deg, #ff9d2f, #ffcc70); }
.conf-bar-cat { background: linear-gradient(90deg, #64c8ff, #c4a8ff); }
.conf-pct {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: rgba(200,190,255,0.55);
    text-align: right;
}
 
/* ── Divider label ── */
.section-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(200,190,255,0.45);
    margin-bottom: 0.9rem;
}
 
/* ── Tip strip ── */
.tip-strip {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1rem 1.3rem;
    color: rgba(200,190,255,0.5);
    font-size: 0.82rem;
    line-height: 1.55;
    animation: fadeUp 0.7s cubic-bezier(.16,1,.3,1) 0.3s both;
}
.tip-strip strong { color: rgba(200,190,255,0.75); font-weight: 500; }
 
/* ── Keyframes ── */
@keyframes fadeDown {
    from { opacity:0; transform: translateY(-22px); }
    to   { opacity:1; transform: translateY(0); }
}
@keyframes fadeUp {
    from { opacity:0; transform: translateY(22px); }
    to   { opacity:1; transform: translateY(0); }
}
@keyframes popIn {
    0%   { opacity:0; transform: scale(0.92) translateY(16px); }
    100% { opacity:1; transform: scale(1)    translateY(0); }
}
@keyframes bounce {
    0%,100% { transform: translateY(0); }
    30%      { transform: translateY(-14px); }
    60%      { transform: translateY(-6px); }
}
@keyframes barGrow {
    from { transform: scaleX(0); transform-origin: left; }
    to   { transform: scaleX(1); transform-origin: left; }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
.shimmer-text {
    background: linear-gradient(90deg, #c4a8ff 25%, #7af4f4 50%, #c4a8ff 75%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
}
</style>
""", unsafe_allow_html=True)
 
 
# ── Model loading ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("cat_dog_cnn.h5")
 
model = load_model()
 
 
# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">🐾 Neural Vision · CNN Classifier</div>
    <h1>PetVision <span class="shimmer-text">AI</span></h1>
    <p>Drop in any photo and our convolutional network will tell you — cat or dog — in under a second.</p>
</div>
""", unsafe_allow_html=True)
 
 
# ── Upload card ───────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">📂 Upload Image</div>', unsafe_allow_html=True)
 
uploaded_file = st.file_uploader(
    "Upload a Cat or Dog Image",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)
 
 
# ── Tip strip ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="tip-strip">
    <strong>Tips for best results:</strong> Use a clear, well-lit photo where the pet's face is visible.
    Supported formats: JPG · PNG · WebP. The model was trained on 128 × 128 crops.
</div>
""", unsafe_allow_html=True)
 
 
# ── Prediction flow ───────────────────────────────────────────────────────────
if uploaded_file is not None:
    st.markdown("<br>", unsafe_allow_html=True)
 
    image = Image.open(uploaded_file).convert("RGB")
 
    # Image preview inside a glass card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">🖼 Preview</div>', unsafe_allow_html=True)
    st.image(image, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
 
    # Run inference
    with st.spinner("Analyzing with CNN…"):
        time.sleep(0.8)   # small dramatic pause
 
        img = image.resize((128, 128))
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=0)
        pred = model.predict(img, verbose=0)
        score = float(pred[0][0])
 
    # ── Result ────────────────────────────────────────────────────────────────
    is_dog     = score > 0.5
    confidence = score * 100 if is_dog else (1 - score) * 100
    bar_class  = "conf-bar-dog" if is_dog else "conf-bar-cat"
    card_class = "result-dog"   if is_dog else "result-cat"
    emoji      = "🐶"           if is_dog else "🐱"
    label      = "Dog"          if is_dog else "Cat"
    desc       = "Woof! This one's definitely a pup." if is_dog else "Meow! Our model sees a feline here."
 
    st.markdown(f"""
    <div class="result-card {card_class}">
        <span class="result-emoji">{emoji}</span>
        <div class="result-label">{label} Detected</div>
        <div class="result-sub">{desc}</div>
        <div class="conf-bar-wrap">
            <div class="conf-bar-fill {bar_class}" style="width:{confidence:.1f}%"></div>
        </div>
        <div class="conf-pct">Confidence · {confidence:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)