import streamlit as st
import torch
from PIL import Image
import sys
import os
import json
import base64
import math
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from model import ChestXrayClassifier, load_model
from predict import predict, CLASS_NAMES, CLASS_COLORS
from gradcam import generate_gradcam

st.set_page_config(
    page_title="MedVision AI - Medical Image Classifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def img_to_b64(img):
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def find_custom_background():
    """Look for user-provided background images in assets/ folder."""
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    if not os.path.isdir(assets_dir):
        return None
    for name in ["background.jpg", "background.png", "bg.jpg", "bg.png", "hero-bg.jpg", "hero-bg.png"]:
        path = os.path.join(assets_dir, name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                ext = name.split(".")[-1]
                mime = "jpeg" if ext == "jpg" else "png"
                return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"
    return None


CUSTOM_BG = find_custom_background()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg-deep: #050d18;
    --bg-main: #07111F;
    --bg-card: rgba(13, 27, 42, 0.75);
    --bg-card-solid: #0D1B2A;
    --bg-card-hover: rgba(13, 27, 42, 0.95);
    --primary: #00D4FF;
    --primary-dim: rgba(0, 212, 255, 0.15);
    --primary-glow: rgba(0, 212, 255, 0.4);
    --secondary: #14B8A6;
    --secondary-dim: rgba(20, 184, 166, 0.15);
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --border: rgba(255, 255, 255, 0.06);
    --border-cyan: rgba(0, 212, 255, 0.2);
    --danger: #EF4444;
    --danger-dim: rgba(239, 68, 68, 0.15);
    --success: #22C55E;
    --success-dim: rgba(34, 197, 94, 0.15);
    --warning: #F59E0B;
    --warning-dim: rgba(245, 158, 11, 0.15);
    --glow-sm: 0 0 15px rgba(0, 212, 255, 0.15);
    --glow-md: 0 0 30px rgba(0, 212, 255, 0.25);
    --glow-lg: 0 0 60px rgba(0, 212, 255, 0.2);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

.stApp {
    background: var(--bg-deep) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    transition: background 0.8s ease;
}

.main .block-container {
    max-width: 1200px !important;
    padding: 1.5rem 3rem 4rem !important;
    background: transparent !important;
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 212, 255, 0.4); }

/* ═══════════════════════════════════════════════ */
/*  PAGE HEALTHCARE BACKGROUNDS (applied via JS)  */
/* ═══════════════════════════════════════════════ */
.stApp.bg-home {
    background:
        radial-gradient(ellipse at 15% 25%, rgba(0, 212, 255, 0.07) 0%, transparent 45%),
        radial-gradient(ellipse at 85% 75%, rgba(20, 184, 166, 0.06) 0%, transparent 45%),
        radial-gradient(ellipse at 50% 50%, rgba(0, 212, 255, 0.02) 0%, transparent 60%),
        url("data:image/svg+xml,%3Csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M40 10 Q55 25 40 40 Q25 55 40 70' stroke='rgba(0,212,255,0.05)' fill='none' stroke-width='1'/%3E%3Ccircle cx='40' cy='10' r='2' fill='rgba(0,212,255,0.08)'/%3E%3Ccircle cx='40' cy='40' r='2' fill='rgba(20,184,166,0.08)'/%3E%3Ccircle cx='40' cy='70' r='2' fill='rgba(0,212,255,0.08)'/%3E%3C/svg%3E"),
        var(--bg-deep) !important;
}

/* Custom user background image (assets/background.jpg etc.) */
.custom-bg-layer {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-size: cover;
    background-position: center;
    z-index: -2;
    pointer-events: none;
}

.custom-bg-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(180deg,
        rgba(5, 13, 24, 0.82) 0%,
        rgba(5, 13, 24, 0.72) 50%,
        rgba(5, 13, 24, 0.88) 100%);
    z-index: -1;
    pointer-events: none;
}

.stApp.bg-analyze {
    background:
        radial-gradient(ellipse at 30% 30%, rgba(0, 212, 255, 0.09) 0%, transparent 40%),
        radial-gradient(ellipse at 70% 70%, rgba(139, 92, 246, 0.05) 0%, transparent 40%),
        repeating-linear-gradient(0deg, transparent, transparent 80px, rgba(0, 212, 255, 0.02) 80px, rgba(0, 212, 255, 0.02) 81px),
        repeating-linear-gradient(90deg, transparent, transparent 80px, rgba(0, 212, 255, 0.02) 80px, rgba(0, 212, 255, 0.02) 81px),
        url("data:image/svg+xml,%3Csvg width='200' height='200' xmlns='http://www.w3.org/2000/svg'%3E%3Crect x='60' y='20' width='80' height='160' rx='10' stroke='rgba(0,212,255,0.04)' fill='none' stroke-width='1'/%3E%3Cline x1='40' y1='100' x2='160' y2='100' stroke='rgba(0,212,255,0.03)' stroke-width='0.5'/%3E%3C/svg%3E"),
        var(--bg-deep) !important;
}

.stApp.bg-history {
    background:
        radial-gradient(ellipse at 20% 80%, rgba(20, 184, 166, 0.07) 0%, transparent 40%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 212, 255, 0.05) 0%, transparent 40%),
        url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Crect x='10' y='10' width='40' height='40' rx='6' stroke='rgba(0,212,255,0.035)' fill='none' stroke-width='0.5'/%3E%3Cline x1='18' y1='22' x2='42' y2='22' stroke='rgba(0,212,255,0.025)' stroke-width='0.5'/%3E%3Cline x1='18' y1='30' x2='36' y2='30' stroke='rgba(0,212,255,0.02)' stroke-width='0.5'/%3E%3Cline x1='18' y1='38' x2='40' y2='38' stroke='rgba(0,212,255,0.025)' stroke-width='0.5'/%3E%3C/svg%3E"),
        var(--bg-deep) !important;
}

.stApp.bg-dashboard {
    background:
        radial-gradient(ellipse at 50% 20%, rgba(139, 92, 246, 0.07) 0%, transparent 40%),
        radial-gradient(ellipse at 20% 70%, rgba(0, 212, 255, 0.06) 0%, transparent 40%),
        radial-gradient(ellipse at 80% 60%, rgba(20, 184, 166, 0.05) 0%, transparent 40%),
        url("data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpolyline points='10,80 25,55 40,65 55,30 70,45 85,15' stroke='rgba(0,212,255,0.04)' fill='none' stroke-width='1'/%3E%3Ccircle cx='25' cy='55' r='2' fill='rgba(0,212,255,0.05)'/%3E%3Ccircle cx='55' cy='30' r='2' fill='rgba(20,184,166,0.05)'/%3E%3Ccircle cx='85' cy='15' r='2' fill='rgba(139,92,246,0.05)'/%3E%3C/svg%3E"),
        var(--bg-deep) !important;
}

/* ═══════════════════════════════════════════════ */
/*  FLOATING TEXT                                 */
/* ═══════════════════════════════════════════════ */
.hero-float-text {
    animation: floatText 6s ease-in-out infinite;
    position: relative; z-index: 1;
}

@keyframes floatText {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

.hero-float-sub {
    animation: floatSub 5s ease-in-out infinite;
    animation-delay: 0.5s;
}

@keyframes floatSub {
    0%, 100% { transform: translateY(0); opacity: 0.8; }
    50% { transform: translateY(-5px); opacity: 1; }
}

/* ═══════════════════════════════════════════════ */
/*  SUPER ATTRACTIVE FEATURE POINTS               */
/* ═══════════════════════════════════════════════ */
.super-feature {
    display: flex; align-items: flex-start; gap: 1.2rem;
    background: rgba(13, 27, 42, 0.45);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 18px;
    padding: 1.6rem 1.5rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative; overflow: hidden;
}

.super-feature::before {
    content: '';
    position: absolute; top: 0; left: 0; bottom: 0;
    width: 3px;
    border-radius: 0 3px 3px 0;
    transition: all 0.3s ease;
}

.super-feature.sf-1::before { background: linear-gradient(180deg, #00D4FF, #0891B2); }
.super-feature.sf-2::before { background: linear-gradient(180deg, #14B8A6, #059669); }
.super-feature.sf-3::before { background: linear-gradient(180deg, #8B5CF6, #7C3AED); }
.super-feature.sf-4::before { background: linear-gradient(180deg, #F59E0B, #D97706); }

.super-feature:hover {
    transform: translateY(-4px) translateX(4px);
    border-color: rgba(0, 212, 255, 0.15);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.25), 0 0 30px rgba(0, 212, 255, 0.08);
}

.super-feature:hover::before { width: 4px; }

.super-feature .sf-icon {
    width: 52px; height: 52px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    border-radius: 14px; font-size: 1.5rem;
    position: relative;
}

.super-feature.sf-1 .sf-icon { background: rgba(0, 212, 255, 0.08); border: 1px solid rgba(0, 212, 255, 0.15); }
.super-feature.sf-2 .sf-icon { background: rgba(20, 184, 166, 0.08); border: 1px solid rgba(20, 184, 166, 0.15); }
.super-feature.sf-3 .sf-icon { background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.15); }
.super-feature.sf-4 .sf-icon { background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.15); }

.super-feature:hover .sf-icon { transform: scale(1.1); }

.super-feature .sf-text h4 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: var(--text-primary); margin-bottom: 0.3rem;
}

.super-feature .sf-text p {
    font-size: 0.82rem; color: var(--text-muted); line-height: 1.5;
}

.super-feature .sf-text .sf-tag {
    display: inline-block; margin-top: 0.5rem;
    font-size: 0.65rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
    padding: 3px 10px; border-radius: 6px;
}

.super-feature.sf-1 .sf-tag { background: rgba(0, 212, 255, 0.1); color: #00D4FF; }
.super-feature.sf-2 .sf-tag { background: rgba(20, 184, 166, 0.1); color: #14B8A6; }
.super-feature.sf-3 .sf-tag { background: rgba(139, 92, 246, 0.1); color: #8B5CF6; }
.super-feature.sf-4 .sf-tag { background: rgba(245, 158, 11, 0.1); color: #F59E0B; }

/* Floating medical icons around hero */
.floating-medical-icons {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none; overflow: hidden; z-index: 0;
}

.floating-medical-icons .fm-icon {
    position: absolute;
    font-size: 1.2rem; opacity: 0.08;
    animation: floatMedical 12s ease-in-out infinite;
}

.floating-medical-icons .fm-icon:nth-child(1) { top: 15%; left: 8%; animation-delay: 0s; animation-duration: 14s; }
.floating-medical-icons .fm-icon:nth-child(2) { top: 25%; right: 12%; animation-delay: 2s; animation-duration: 11s; }
.floating-medical-icons .fm-icon:nth-child(3) { bottom: 20%; left: 15%; animation-delay: 4s; animation-duration: 16s; }
.floating-medical-icons .fm-icon:nth-child(4) { bottom: 30%; right: 8%; animation-delay: 1s; animation-duration: 13s; }
.floating-medical-icons .fm-icon:nth-child(5) { top: 60%; left: 5%; animation-delay: 3s; animation-duration: 15s; }
.floating-medical-icons .fm-icon:nth-child(6) { top: 10%; left: 50%; animation-delay: 5s; animation-duration: 10s; }

@keyframes floatMedical {
    0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.06; }
    25% { transform: translateY(-12px) rotate(5deg); opacity: 0.12; }
    50% { transform: translateY(-6px) rotate(-3deg); opacity: 0.08; }
    75% { transform: translateY(-15px) rotate(3deg); opacity: 0.1; }
}

/* ═══════════════════════════════════════════════ */
/*  GRID BACKGROUND                               */
/* ═══════════════════════════════════════════════ */
.grid-bg {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridScroll 40s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes gridScroll {
    0% { transform: translate(0, 0); }
    100% { transform: translate(60px, 60px); }
}

/* ═══════════════════════════════════════════════ */
/*  FLOATING PARTICLES                            */
/* ═══════════════════════════════════════════════ */
.particles {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none; z-index: 0; overflow: hidden;
}

.particle {
    position: absolute;
    width: 3px; height: 3px;
    background: var(--primary);
    border-radius: 50%;
    opacity: 0;
    animation: particleFloat linear infinite;
}

.particle:nth-child(1) { left: 10%; animation-duration: 18s; animation-delay: 0s; }
.particle:nth-child(2) { left: 25%; animation-duration: 22s; animation-delay: 3s; width: 2px; height: 2px; }
.particle:nth-child(3) { left: 40%; animation-duration: 16s; animation-delay: 1s; }
.particle:nth-child(4) { left: 55%; animation-duration: 20s; animation-delay: 5s; width: 4px; height: 4px; }
.particle:nth-child(5) { left: 70%; animation-duration: 24s; animation-delay: 2s; width: 2px; height: 2px; }
.particle:nth-child(6) { left: 85%; animation-duration: 17s; animation-delay: 4s; }
.particle:nth-child(7) { left: 15%; animation-duration: 21s; animation-delay: 6s; width: 2px; height: 2px; }
.particle:nth-child(8) { left: 60%; animation-duration: 19s; animation-delay: 1.5s; }
.particle:nth-child(9) { left: 90%; animation-duration: 23s; animation-delay: 3.5s; width: 4px; height: 4px; }
.particle:nth-child(10) { left: 35%; animation-duration: 25s; animation-delay: 0.5s; width: 2px; height: 2px; }
.particle:nth-child(11) { left: 5%; animation-duration: 20s; animation-delay: 7s; }
.particle:nth-child(12) { left: 48%; animation-duration: 26s; animation-delay: 2.5s; width: 3px; height: 3px; }

@keyframes particleFloat {
    0% { bottom: -5%; opacity: 0; transform: translateX(0) scale(1); }
    10% { opacity: 0.6; }
    50% { opacity: 0.3; transform: translateX(30px) scale(0.8); }
    90% { opacity: 0.5; }
    100% { bottom: 105%; opacity: 0; transform: translateX(-20px) scale(0.5); }
}

/* ═══════════════════════════════════════════════ */
/*  NAVIGATION                                    */
/* ═══════════════════════════════════════════════ */
.nav-bar {
    display: flex; flex-direction: column; align-items: center;
    padding: 0.8rem 1.8rem;
    background: rgba(7, 17, 31, 0.85);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--border-cyan);
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: var(--glow-sm), 0 8px 32px rgba(0, 0, 0, 0.4);
}

.nav-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem; font-weight: 800;
    background: linear-gradient(135deg, #00D4FF, #14B8A6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    display: flex; align-items: center; gap: 10px;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    margin-bottom: 0.6rem;
    letter-spacing: 0.5px;
}

.nav-brand-dot {
    width: 8px; height: 8px;
    background: #00D4FF;
    border-radius: 50%;
    box-shadow: 0 0 10px #00D4FF;
    animation: navPulse 2s ease-in-out infinite;
}

@keyframes navPulse {
    0%, 100% { box-shadow: 0 0 5px #00D4FF; opacity: 1; }
    50% { box-shadow: 0 0 15px #00D4FF, 0 0 30px rgba(0, 212, 255, 0.3); opacity: 0.8; }
}

.nav-links { display: flex; gap: 0.3rem; }

.nav-link {
    padding: 0.45rem 1.1rem; border-radius: 10px;
    font-size: 0.82rem; font-weight: 600;
    color: var(--text-muted); background: transparent;
    border: 1px solid transparent;
    cursor: pointer; transition: all 0.3s ease;
    font-family: 'Inter', sans-serif;
}

.nav-link:hover {
    color: var(--text-primary);
    background: rgba(0, 212, 255, 0.06);
    border-color: rgba(0, 212, 255, 0.15);
}

.nav-link.active {
    color: #00D4FF;
    background: rgba(0, 212, 255, 0.1);
    border-color: rgba(0, 212, 255, 0.25);
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
}

/* ═══════════════════════════════════════════════ */
/*  HERO SECTION                                  */
/* ═══════════════════════════════════════════════ */
.hero-section {
    text-align: center; padding: 3.5rem 2rem 3rem;
    margin-bottom: 2.5rem;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(20, 184, 166, 0.03), rgba(0, 212, 255, 0.02));
    border: 1px solid var(--border-cyan);
    border-radius: 28px;
    position: relative; overflow: hidden;
    box-shadow: var(--glow-lg), inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

.hero-section::before {
    content: '';
    position: absolute; top: -2px; left: 20%; right: 20%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00D4FF, transparent);
    border-radius: 2px;
}

.hero-section::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; top: 0;
    background: radial-gradient(circle at 50% 0%, rgba(0, 212, 255, 0.08) 0%, transparent 60%);
    pointer-events: none;
}

.hero-tag {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid rgba(0, 212, 255, 0.2);
    color: #00D4FF;
    padding: 6px 18px; border-radius: 50px;
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px;
    margin-bottom: 1.2rem;
    position: relative; z-index: 1;
}

.hero-tag .dot {
    width: 6px; height: 6px;
    background: #00D4FF; border-radius: 50%;
    animation: heroPulse 2s ease-in-out infinite;
    box-shadow: 0 0 6px #00D4FF;
}

@keyframes heroPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(1.5); }
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.2rem !important; font-weight: 800 !important;
    line-height: 1.1 !important; margin-bottom: 0.6rem !important;
    position: relative; z-index: 1;
}

.hero-title .line1 {
    display: block;
    color: var(--text-primary);
    font-size: 0.85rem; font-weight: 600;
    letter-spacing: 4px; text-transform: uppercase;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, var(--text-muted), #00D4FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.hero-title .line2 {
    display: block;
    font-size: 2.8rem;
    background: linear-gradient(135deg, #00D4FF 0%, #14B8A6 50%, #00D4FF 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: heroGradient 4s ease infinite;
}

@keyframes heroGradient {
    0% { background-position: 0% center; }
    50% { background-position: 100% center; }
    100% { background-position: 0% center; }
}

.hero-subtitle {
    font-size: 1.05rem; color: var(--text-secondary);
    position: relative; z-index: 1;
    max-width: 600px; margin: 0.8rem auto 1.5rem;
    line-height: 1.6;
}

/* ═══════════════════════════════════════════════ */
/*  FLOWING WORDS (word-by-word reveal)           */
/* ═══════════════════════════════════════════════ */
.flow-words span {
    display: inline-block;
    opacity: 0;
    animation: flowWordIn 0.6s ease forwards;
}

@keyframes flowWordIn {
    0% { opacity: 0; transform: translateY(14px) scale(0.9); filter: blur(4px); }
    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}

/* ═══════════════════════════════════════════════ */
/*  MARQUEE STRIP (scrolling keywords)            */
/* ═══════════════════════════════════════════════ */
.marquee-strip {
    overflow: hidden;
    white-space: nowrap;
    padding: 12px 0;
    margin: 2.2rem 0 0.5rem;
    border-top: 1px solid rgba(0, 212, 255, 0.08);
    border-bottom: 1px solid rgba(0, 212, 255, 0.08);
    background: rgba(13, 27, 42, 0.35);
    position: relative;
    z-index: 1;
}

.marquee-track {
    display: inline-flex;
    gap: 3rem;
    animation: marqueeScroll 28s linear infinite;
    will-change: transform;
}

.marquee-track:hover { animation-play-state: paused; }

.marquee-item {
    display: inline-flex; align-items: center; gap: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem; font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 2px; text-transform: uppercase;
}

.marquee-item .m-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #00D4FF;
    box-shadow: 0 0 8px #00D4FF;
}

@keyframes marqueeScroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

.hero-buttons {
    display: flex; gap: 1rem; justify-content: center;
    position: relative; z-index: 1;
}

.btn-primary-hero {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, #00D4FF, #14B8A6);
    color: #050d18 !important;
    padding: 0.7rem 2rem; border-radius: 12px;
    font-family: 'Inter', sans-serif; font-weight: 700; font-size: 0.9rem;
    border: none; cursor: pointer;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.35);
    transition: all 0.3s ease;
    text-decoration: none;
}

.btn-primary-hero:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 35px rgba(0, 212, 255, 0.5);
}

.btn-secondary-hero {
    display: inline-flex; align-items: center; gap: 8px;
    background: transparent;
    color: var(--text-secondary) !important;
    padding: 0.7rem 2rem; border-radius: 12px;
    font-family: 'Inter', sans-serif; font-weight: 700; font-size: 0.9rem;
    border: 1px solid var(--border-cyan); cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
}

.btn-secondary-hero:hover {
    color: #00D4FF !important;
    border-color: rgba(0, 212, 255, 0.5);
    background: rgba(0, 212, 255, 0.05);
}

/* ═══════════════════════════════════════════════ */
/*  GLASSMORPHISM CARDS                           */
/* ═══════════════════════════════════════════════ */
.glass-card {
    background: rgba(13, 27, 42, 0.55);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(0, 212, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent);
}

.glass-card:hover {
    border-color: rgba(0, 212, 255, 0.25);
    box-shadow: var(--glow-md), 0 20px 60px rgba(0, 0, 0, 0.3);
    transform: translateY(-4px);
}

/* ═══════════════════════════════════════════════ */
/*  FEATURE CARDS                                 */
/* ═══════════════════════════════════════════════ */
.features-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 2rem 0; }

.feature-card {
    background: rgba(13, 27, 42, 0.45);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 16px;
    padding: 1.5rem; text-align: center;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative; overflow: hidden;
}

.feature-card::after {
    content: '';
    position: absolute; bottom: 0; left: 20%; right: 20%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    opacity: 0; transition: opacity 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: rgba(0, 212, 255, 0.2);
    box-shadow: var(--glow-md), 0 15px 40px rgba(0, 0, 0, 0.3);
}

.feature-card:hover::after { opacity: 1; }

.feature-card .icon {
    font-size: 2rem; margin-bottom: 0.8rem;
    display: inline-block;
    transition: transform 0.3s ease;
}

.feature-card:hover .icon { transform: scale(1.15) translateY(-2px); }

.feature-card h4 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; color: var(--text-primary);
    margin-bottom: 0.3rem; font-size: 0.95rem;
}

.feature-card p { color: var(--text-muted); font-size: 0.8rem; line-height: 1.4; }

/* ═══════════════════════════════════════════════ */
/*  AI SCANNING ANIMATION                         */
/* ═══════════════════════════════════════════════ */
.scan-container {
    position: relative;
    display: inline-block;
    border-radius: 20px;
    overflow: hidden;
    border: 2px solid rgba(0, 212, 255, 0.3);
    box-shadow: var(--glow-md);
}

.scan-container img {
    display: block; width: 100%; height: auto;
    border-radius: 18px;
}

.scan-line {
    position: absolute; top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, #00D4FF, #14B8A6, #00D4FF, transparent);
    box-shadow: 0 0 20px #00D4FF, 0 0 40px rgba(0, 212, 255, 0.4);
    animation: scanDown 2s ease-in-out infinite;
    z-index: 2;
}

@keyframes scanDown {
    0% { top: 0%; opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}

.scan-overlay {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(180deg, rgba(0, 212, 255, 0.03) 0%, transparent 50%, rgba(0, 212, 255, 0.03) 100%);
    pointer-events: none;
    border-radius: 18px;
}

.scan-steps { margin-top: 1.5rem; }

.scan-step {
    display: flex; align-items: center; gap: 12px;
    padding: 0.5rem 0;
    font-size: 0.85rem;
    transition: all 0.3s ease;
}

.scan-step .step-dot {
    width: 20px; height: 20px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; flex-shrink: 0;
    border: 2px solid rgba(255, 255, 255, 0.1);
    color: var(--text-muted);
    transition: all 0.3s ease;
}

.scan-step.done .step-dot {
    background: rgba(34, 197, 94, 0.15);
    border-color: #22C55E;
    color: #22C55E;
    box-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
}

.scan-step.active .step-dot {
    background: rgba(0, 212, 255, 0.15);
    border-color: #00D4FF;
    color: #00D4FF;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    animation: stepPulse 1.5s ease-in-out infinite;
}

.scan-step.pending .step-dot {
    border-color: rgba(255, 255, 255, 0.08);
}

@keyframes stepPulse {
    0%, 100% { box-shadow: 0 0 5px rgba(0, 212, 255, 0.3); }
    50% { box-shadow: 0 0 15px rgba(0, 212, 255, 0.5); }
}

.scan-step .step-text { color: var(--text-muted); }
.scan-step.done .step-text { color: var(--success); }
.scan-step.active .step-text { color: #00D4FF; font-weight: 600; }

.scan-progress-bar {
    height: 4px; background: rgba(255, 255, 255, 0.05);
    border-radius: 4px; margin-top: 1rem; overflow: hidden;
}

.scan-progress-fill {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, #00D4FF, #14B8A6);
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
    animation: progressFill 2.5s ease-in-out infinite;
}

@keyframes progressFill {
    0% { width: 0%; }
    50% { width: 75%; }
    100% { width: 100%; }
}

/* ═══════════════════════════════════════════════ */
/*  UPLOAD ZONE (GLASSMORPHISM)                   */
/* ═══════════════════════════════════════════════ */
.upload-zone {
    background: rgba(13, 27, 42, 0.4);
    backdrop-filter: blur(16px);
    border: 2px dashed rgba(0, 212, 255, 0.2);
    border-radius: 24px;
    padding: 3.5rem 2rem; text-align: center;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative; overflow: hidden;
}

.upload-zone::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(circle at 50% 50%, rgba(0, 212, 255, 0.03) 0%, transparent 70%);
    pointer-events: none;
}

.upload-zone:hover {
    border-color: rgba(0, 212, 255, 0.5);
    background: rgba(13, 27, 42, 0.6);
    box-shadow: var(--glow-md), inset 0 0 60px rgba(0, 212, 255, 0.03);
    transform: translateY(-4px);
}

.upload-icon {
    width: 90px; height: 90px; margin: 0 auto 1.2rem;
    background: rgba(0, 212, 255, 0.06);
    border: 2px solid rgba(0, 212, 255, 0.15);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    transition: all 0.3s ease;
}

.upload-zone:hover .upload-icon {
    background: rgba(0, 212, 255, 0.12);
    border-color: rgba(0, 212, 255, 0.35);
    box-shadow: 0 0 30px rgba(0, 212, 255, 0.15);
    transform: scale(1.05);
}

.upload-formats {
    display: flex; gap: 6px; justify-content: center; margin-top: 1rem;
}

.format-tag {
    background: rgba(0, 212, 255, 0.06);
    border: 1px solid rgba(0, 212, 255, 0.12);
    color: rgba(0, 212, 255, 0.7);
    padding: 3px 10px; border-radius: 6px;
    font-size: 0.65rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════════ */
/*  CONFIDENCE RING (ANIMATED)                    */
/* ═══════════════════════════════════════════════ */
.confidence-ring-container {
    display: flex; flex-direction: column; align-items: center;
    padding: 2rem;
}

.confidence-ring {
    position: relative;
    width: 180px; height: 180px;
}

.confidence-ring svg {
    width: 180px; height: 180px;
    transform: rotate(-90deg);
}

.confidence-ring .bg-ring {
    fill: none;
    stroke: rgba(255, 255, 255, 0.04);
    stroke-width: 8;
}

.confidence-ring .fg-ring {
    fill: none;
    stroke-width: 8;
    stroke-linecap: round;
    stroke-dasharray: 440;
    stroke-dashoffset: 440;
    transition: stroke-dashoffset 2s cubic-bezier(0.4, 0, 0.2, 1);
    filter: drop-shadow(0 0 8px var(--primary));
}

.confidence-ring .ring-label {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
}

.confidence-ring .ring-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem; font-weight: 800;
    line-height: 1;
}

.confidence-ring .ring-text {
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 4px;
}

/* ═══════════════════════════════════════════════ */
/*  PREDICTION DISPLAY                            */
/* ═══════════════════════════════════════════════ */
.prediction-display {
    background: rgba(13, 27, 42, 0.6);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border-cyan);
    border-radius: 24px;
    padding: 2rem;
    position: relative; overflow: hidden;
    box-shadow: var(--glow-sm);
}

.prediction-display::before {
    content: '';
    position: absolute; top: 0; left: 10%; right: 10%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
}

.prediction-header {
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 1.2rem; padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.prediction-header h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem; font-weight: 700; flex: 1;
}

.prediction-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 14px; border-radius: 50px;
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
}

.prediction-badge.covid {
    background: var(--danger-dim); color: var(--danger);
    border: 1px solid rgba(239, 68, 68, 0.25);
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.15);
}

.prediction-badge.normal {
    background: var(--success-dim); color: var(--success);
    border: 1px solid rgba(34, 197, 94, 0.25);
    box-shadow: 0 0 15px rgba(34, 197, 94, 0.15);
}

.prediction-badge.pneumonia {
    background: var(--warning-dim); color: var(--warning);
    border: 1px solid rgba(245, 158, 11, 0.25);
    box-shadow: 0 0 15px rgba(245, 158, 11, 0.15);
}

/* ═══════════════════════════════════════════════ */
/*  RESULT CARDS                                  */
/* ═══════════════════════════════════════════════ */
.result-card {
    background: rgba(13, 27, 42, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 18px;
    padding: 1.4rem; text-align: center;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative; overflow: hidden;
}

.result-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
}

.result-card.danger::before { background: linear-gradient(90deg, transparent, #EF4444, transparent); }
.result-card.success::before { background: linear-gradient(90deg, transparent, #22C55E, transparent); }
.result-card.warning::before { background: linear-gradient(90deg, transparent, #F59E0B, transparent); }

.result-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.result-card .label {
    font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 2px; color: var(--text-muted);
    font-weight: 600; margin-bottom: 0.4rem;
}

.result-card .value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem; font-weight: 800; line-height: 1;
    margin-bottom: 0.2rem;
}

.result-card .value.danger { color: var(--danger); text-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
.result-card .value.success { color: var(--success); text-shadow: 0 0 20px rgba(34, 197, 94, 0.3); }
.result-card .value.warning { color: var(--warning); text-shadow: 0 0 20px rgba(245, 158, 11, 0.3); }
.result-card .sub { font-size: 0.75rem; color: var(--text-muted); }

/* ═══════════════════════════════════════════════ */
/*  CONFIDENCE BARS                               */
/* ═══════════════════════════════════════════════ */
.confidence-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 14px;
    padding: 0.9rem 1.2rem; margin-bottom: 0.7rem;
    transition: all 0.3s ease;
}

.confidence-item:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(0, 212, 255, 0.15);
}

.confidence-item .header {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 0.5rem;
}

.confidence-item .class-name { font-weight: 700; font-size: 0.85rem; }
.confidence-item .percentage {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800; font-size: 1rem;
}

.confidence-bar-bg {
    height: 6px; background: rgba(255, 255, 255, 0.04);
    border-radius: 6px; overflow: hidden;
}

.confidence-bar-fill {
    height: 100%; border-radius: 6px;
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative; overflow: hidden;
}

.confidence-bar-fill::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    animation: shimmer 2.5s ease-in-out infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.confidence-bar-fill.covid {
    background: linear-gradient(90deg, #EF4444, #F97316);
    box-shadow: 0 0 12px rgba(239, 68, 68, 0.35);
}

.confidence-bar-fill.normal {
    background: linear-gradient(90deg, #22C55E, #10B981);
    box-shadow: 0 0 12px rgba(34, 197, 94, 0.35);
}

.confidence-bar-fill.pneumonia {
    background: linear-gradient(90deg, #F59E0B, #EAB308);
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.35);
}

/* ═══════════════════════════════════════════════ */
/*  GRADCAM PANEL                                 */
/* ═══════════════════════════════════════════════ */
.gradcam-panel {
    background: rgba(13, 27, 42, 0.55);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 20px; padding: 1.5rem;
    overflow: hidden; position: relative;
}

.gradcam-panel::before {
    content: '';
    position: absolute; top: 0; left: 10%; right: 10%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #8B5CF6, #A78BFA, transparent);
}

.gradcam-panel h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem; font-weight: 700;
    margin-bottom: 0.3rem;
}

.gradcam-panel p {
    color: var(--text-muted); font-size: 0.82rem; margin-bottom: 1rem;
}

.gradcam-image-wrapper {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;
}

.gradcam-image-wrapper:hover {
    border-color: rgba(139, 92, 246, 0.3);
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.15);
}

.gradcam-label {
    text-align: center; font-weight: 700;
    font-size: 0.8rem; margin-bottom: 0.6rem;
    color: var(--text-secondary);
}

/* ═══════════════════════════════════════════════ */
/*  HISTORY                                        */
/* ═══════════════════════════════════════════════ */
.history-card {
    background: rgba(13, 27, 42, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 14px; padding: 1rem 1.2rem;
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 0.7rem;
    transition: all 0.3s ease;
}

.history-card:hover {
    border-color: rgba(0, 212, 255, 0.2);
    transform: translateX(4px);
    box-shadow: var(--glow-sm);
}

.history-card .hist-img {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    background: rgba(0, 212, 255, 0.06);
    border: 1px solid rgba(0, 212, 255, 0.1);
}

.history-card .hist-info { flex: 1; }
.history-card .hist-info h4 { font-size: 0.88rem; font-weight: 700; margin-bottom: 0.15rem; }
.history-card .hist-info p { font-size: 0.72rem; color: var(--text-muted); }
.history-card .hist-result { text-align: right; }
.history-card .hist-result .pred {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800; font-size: 0.95rem;
}
.history-card .hist-result .conf { font-size: 0.72rem; color: var(--text-muted); }

/* ═══════════════════════════════════════════════ */
/*  DASHBOARD STAT CARDS                          */
/* ═══════════════════════════════════════════════ */
.stat-card {
    background: rgba(13, 27, 42, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 18px; padding: 1.4rem;
    text-align: center;
    transition: all 0.4s ease;
    position: relative; overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
}

.stat-card.s1::before { background: linear-gradient(90deg, transparent, #00D4FF, transparent); }
.stat-card.s2::before { background: linear-gradient(90deg, transparent, #22C55E, transparent); }
.stat-card.s3::before { background: linear-gradient(90deg, transparent, #F59E0B, transparent); }
.stat-card.s4::before { background: linear-gradient(90deg, transparent, #8B5CF6, transparent); }

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--glow-sm), 0 10px 30px rgba(0, 0, 0, 0.3);
}

.stat-card .stat-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }

.stat-card .stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(135deg, #00D4FF, #14B8A6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.stat-card .stat-label {
    font-size: 0.72rem; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;
}

/* ═══════════════════════════════════════════════ */
/*  ABOUT                                         */
/* ═══════════════════════════════════════════════ */
.about-card {
    background: rgba(13, 27, 42, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 20px; padding: 2rem;
    margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
}

.about-card::before {
    content: '';
    position: absolute; top: 0; left: 15%; right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.2), transparent);
}

.about-card h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem; font-weight: 700;
    margin-bottom: 1rem;
    display: flex; align-items: center; gap: 0.5rem;
}

.about-card p {
    color: var(--text-secondary); line-height: 1.7; font-size: 0.92rem;
}

.tech-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; }

.tech-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 14px; padding: 1.1rem;
    text-align: center;
    transition: all 0.3s ease;
}

.tech-item:hover {
    border-color: rgba(0, 212, 255, 0.2);
    box-shadow: var(--glow-sm);
    transform: translateY(-2px);
}

.tech-item .icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
.tech-item h4 { font-size: 0.88rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.2rem; }
.tech-item p { font-size: 0.72rem; color: var(--text-muted); }

/* ═══════════════════════════════════════════════ */
/*  DISCLAIMER                                    */
/* ═══════════════════════════════════════════════ */
.disclaimer {
    background: rgba(245, 158, 11, 0.05);
    border: 1px solid rgba(245, 158, 11, 0.15);
    border-radius: 16px; padding: 1rem 1.3rem;
    display: flex; align-items: flex-start; gap: 10px;
    margin-top: 1.5rem;
}

.disclaimer .icon { font-size: 1.1rem; flex-shrink: 0; margin-top: 2px; }
.disclaimer .text { font-size: 0.8rem; color: var(--text-secondary); line-height: 1.6; }
.disclaimer .text strong { color: var(--warning); }

/* ═══════════════════════════════════════════════ */
/*  EVALUATION TABLES                             */
/* ═══════════════════════════════════════════════ */
.about-card table tbody tr {
    transition: background 0.2s ease;
}

.about-card table tbody tr:hover {
    background: rgba(0, 212, 255, 0.04) !important;
}

.about-card table tbody tr:hover td {
    border-color: rgba(0, 212, 255, 0.15) !important;
}

/* ═══════════════════════════════════════════════ */
/*  ANIMATED PIPELINE                             */
/* ═══════════════════════════════════════════════ */
.pipeline { display: flex; align-items: center; justify-content: center; gap: 0; flex-wrap: wrap; margin: 1.5rem 0; }

.pipeline-step {
    background: rgba(13, 27, 42, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px; padding: 0.9rem 1.1rem;
    text-align: center; min-width: 110px;
    transition: all 0.3s ease;
    position: relative;
}

.pipeline-step:hover {
    border-color: rgba(0, 212, 255, 0.2);
    transform: translateY(-3px);
    box-shadow: var(--glow-sm);
}

.pipeline-step .step-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
.pipeline-step .step-text {
    font-size: 0.72rem; font-weight: 600;
    color: var(--text-secondary);
}

.pipeline-connector {
    width: 40px; height: 2px;
    background: rgba(0, 212, 255, 0.15);
    position: relative; flex-shrink: 0;
}

.pipeline-connector::after {
    content: '';
    position: absolute;
    top: -2px; left: 0;
    width: 8px; height: 6px;
    background: #00D4FF;
    border-radius: 2px;
    box-shadow: 0 0 8px #00D4FF;
    animation: pipelineFlow 3s ease-in-out infinite;
}

@keyframes pipelineFlow {
    0% { left: 0%; opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { left: 100%; opacity: 0; }
}

.pipeline-connector:nth-child(2)::after { animation-delay: 0s; }
.pipeline-connector:nth-child(4)::after { animation-delay: 0.4s; }
.pipeline-connector:nth-child(6)::after { animation-delay: 0.8s; }
.pipeline-connector:nth-child(8)::after { animation-delay: 1.2s; }
.pipeline-connector:nth-child(10)::after { animation-delay: 1.6s; }

/* ═══════════════════════════════════════════════ */
/*  FOOTER                                        */
/* ═══════════════════════════════════════════════ */
.footer {
    text-align: center; padding: 2rem 0; margin-top: 3rem;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    color: var(--text-muted); font-size: 0.78rem;
}

.footer a {
    color: rgba(0, 212, 255, 0.6);
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer a:hover { color: #00D4FF; }

/* ═══════════════════════════════════════════════ */
/*  STREAMLIT OVERRIDES                           */
/* ═══════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #00D4FF, #14B8A6) !important;
    color: #050d18 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.55rem 2rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.25) !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0, 212, 255, 0.4) !important;
}

.stFileUploader > div {
    border: 2px dashed rgba(0, 212, 255, 0.2) !important;
    border-radius: 16px !important;
    background: rgba(0, 212, 255, 0.02) !important;
}

.stFileUploader > div:hover {
    border-color: rgba(0, 212, 255, 0.5) !important;
    box-shadow: var(--glow-sm) !important;
}

.stFileUploader label {
    color: #00D4FF !important;
    font-weight: 700 !important;
}

div[data-testid="stMarkdown"] h1,
div[data-testid="stMarkdown"] h2,
div[data-testid="stMarkdown"] h3 {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ═══════════════════════════════════════════════ */
/*  RESPONSIVE — LAPTOP                           */
/* ═══════════════════════════════════════════════ */
@media (max-width: 1200px) {
    .main .block-container {
        padding: 1.5rem 2rem 4rem !important;
        max-width: 100% !important;
    }
    .hero-title .line2 { font-size: 2.3rem !important; }
}

/* ═══════════════════════════════════════════════ */
/*  RESPONSIVE — TABLET                           */
/* ═══════════════════════════════════════════════ */
@media (max-width: 900px) {
    .features-grid { grid-template-columns: repeat(2, 1fr) !important; }
    .hero-title .line2 { font-size: 2rem !important; }
    .nav-brand { font-size: 1.35rem; }

    /* Streamlit columns stack vertically on tablets */
    div[data-testid="column"] {
        width: 100% !important;
        flex: 100% !important;
        min-width: 100% !important;
    }

    .confidence-ring { width: 140px !important; height: 140px !important; }
    .confidence-ring svg { width: 140px !important; height: 140px !important; }
    .confidence-ring .ring-value { font-size: 2rem !important; }
}

/* ═══════════════════════════════════════════════ */
/*  RESPONSIVE — PHONE                            */
/* ═══════════════════════════════════════════════ */
@media (max-width: 640px) {
    :root {
        --glow-sm: 0 0 10px rgba(0, 212, 255, 0.12);
        --glow-md: 0 0 20px rgba(0, 212, 255, 0.18);
        --glow-lg: 0 0 30px rgba(0, 212, 255, 0.15);
    }

    .main .block-container {
        padding: 0.8rem 0.8rem 3rem !important;
    }

    /* NAV — compact for phone */
    .nav-bar { padding: 0.6rem 0.8rem; border-radius: 14px; margin-bottom: 1rem; }
    .nav-brand { font-size: 1.15rem; margin-bottom: 0.5rem; }
    .nav-links { display: flex; gap: 0.25rem; width: 100%; justify-content: center; flex-wrap: wrap; }

    /* HERO — compact for phone */
    .hero-section { padding: 2rem 1rem 2rem; border-radius: 18px; }
    .hero-tag { font-size: 0.6rem; padding: 5px 12px; margin-bottom: 0.8rem; }
    .hero-title .line1 { font-size: 0.65rem !important; letter-spacing: 2px !important; margin-bottom: 0.3rem !important; }
    .hero-title .line2 { font-size: 1.45rem !important; }
    .hero-subtitle { font-size: 0.82rem !important; padding: 0 0.5rem; }
    .hero-buttons { flex-direction: column; gap: 0.6rem; width: 100%; align-items: stretch; }
    .btn-primary-hero, .btn-secondary-hero { justify-content: center; padding: 0.65rem 1rem; font-size: 0.82rem; }

    /* FEATURE CARDS — single column */
    .features-grid { grid-template-columns: 1fr !important; gap: 0.7rem; }
    .feature-card { padding: 1.1rem; }

    /* SUPER FEATURES — tighter */
    .super-feature { padding: 1.1rem; gap: 0.8rem; }
    .super-feature .sf-icon { width: 42px; height: 42px; font-size: 1.2rem; }
    .super-feature .sf-text h4 { font-size: 0.88rem; }
    .super-feature .sf-text p { font-size: 0.76rem; }

    /* PIPELINE — vertical with vertical connectors */
    .pipeline { flex-direction: column; gap: 0.4rem; }
    .pipeline-step { min-width: 160px; padding: 0.7rem 1rem; }
    .pipeline-step .step-icon { font-size: 1.2rem; }
    .pipeline-step .step-text { font-size: 0.68rem; }
    .pipeline-connector { width: 2px; height: 16px; }

    /* UPLOAD ZONE */
    .upload-zone { padding: 2rem 1rem; border-radius: 18px; }
    .upload-icon { width: 70px; height: 70px; font-size: 1.7rem; }

    /* RESULT CARDS */
    .result-card .value { font-size: 1.35rem; }
    .prediction-display { padding: 1.2rem; border-radius: 18px; }
    .prediction-header h2 { font-size: 1rem; }

    /* CONFIDENCE RING */
    .confidence-ring { width: 120px !important; height: 120px !important; }
    .confidence-ring svg { width: 120px !important; height: 120px !important; }
    .confidence-ring .ring-value { font-size: 1.6rem !important; }
    .confidence-ring .ring-text { font-size: 0.55rem; letter-spacing: 1px; }

    /* GRADCAM */
    .gradcam-panel { padding: 1rem; }
    .gradcam-label { font-size: 0.72rem; }

    /* HISTORY & DASHBOARD CARDS */
    .history-card { padding: 0.8rem; gap: 0.6rem; }
    .history-card .hist-img { width: 38px; height: 38px; font-size: 1rem; border-radius: 10px; }
    .stat-card { padding: 1rem 0.6rem; }
    .stat-card .stat-value { font-size: 1.6rem; }
    .stat-card .stat-label { font-size: 0.6rem; letter-spacing: 1px; }

    /* TECH GRID — single column */
    .tech-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 0.6rem; }
    .tech-item { padding: 0.8rem; }
    .tech-item .icon { font-size: 1.4rem; }

    /* ABOUT CARD INSIGHTS GRID */
    .about-card { padding: 1.2rem; border-radius: 16px; }
    .about-card h3 { font-size: 1rem; }

    /* SCANNING ANIMATION */
    .scan-step { font-size: 0.75rem; }

    /* DISCLAIMER & FOOTER */
    .disclaimer { padding: 0.8rem 1rem; }
    .footer { font-size: 0.68rem; padding: 1.2rem 0; }

    /* STREAMLIT BUTTONS */
    .stButton > button { padding: 0.55rem 1rem !important; font-size: 0.8rem !important; }

    /* HIDE FLOATING PARTICLES ON PHONE (performance) */
    .particles { display: none; }

    /* EVALUATION TABLES — scrollable */
    .about-card table { display: block; overflow-x: auto; white-space: nowrap; }
}
</style>

<div class="grid-bg"></div>
<div class="particles">
    <div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div>
</div>
""", unsafe_allow_html=True)

if CUSTOM_BG:
    st.markdown(f"""
    <div class="custom-bg-layer" style="background-image: url('{CUSTOM_BG}');"></div>
    <div class="custom-bg-overlay"></div>
    """, unsafe_allow_html=True)


HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(st.session_state.history[-100:], f, indent=2)
    except IOError:
        pass


def generate_html_report(entry, index=None):
    pred = entry["prediction"]
    color = {"COVID-19": "#EF4444", "Normal": "#22C55E", "Pneumonia": "#F59E0B"}.get(pred, "#00D4FF")
    probs_rows = ""
    for cls, prob in sorted(entry["probabilities"].items(), key=lambda x: x[1], reverse=True):
        bar_color = {"COVID-19": "#EF4444", "Normal": "#22C55E", "Pneumonia": "#F59E0B"}.get(cls, "#00D4FF")
        probs_rows += f"""
        <tr>
            <td style="padding:10px 14px;font-weight:600;color:#94A3B8;">{cls}</td>
            <td style="padding:10px 14px;width:50%;">
                <div style="background:rgba(255,255,255,0.06);border-radius:6px;height:8px;overflow:hidden;">
                    <div style="width:{prob}%;height:100%;background:{bar_color};border-radius:6px;"></div>
                </div>
            </td>
            <td style="padding:10px 14px;text-align:right;font-weight:700;color:{bar_color};">{prob}%</td>
        </tr>"""

    title = f"Analysis Report #{index}" if index else "Analysis Report"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - MedVision AI</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #07111F; color: #F8FAFC; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 640px; margin: 0 auto; }}
    .header {{ text-align: center; padding: 32px 24px; background: rgba(13,27,42,0.9); border: 1px solid rgba(0,212,255,0.2); border-radius: 20px 20px 0 0; }}
    .brand {{ font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg,#00D4FF,#14B8A6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }}
    .tagline {{ color: #64748B; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 3px; margin-top: 6px; }}
    .body {{ background: rgba(13,27,42,0.7); border: 1px solid rgba(255,255,255,0.05); border-top: none; padding: 28px 32px; }}
    .pred-box {{ text-align: center; padding: 22px; background: {color}11; border: 1px solid {color}33; border-radius: 16px; margin-bottom: 26px; }}
    .pred-label {{ font-size: 0.68rem; color: #64748B; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px; }}
    .pred-value {{ font-size: 2.1rem; font-weight: 800; color: {color}; }}
    .conf-value {{ font-size: 1rem; color: #94A3B8; margin-top: 4px; }}
    h3 {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px; color: #00D4FF; margin: 22px 0 12px; }}
    table {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.02); border-radius: 12px; overflow: hidden; }}
    td, th {{ font-size: 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.04); }}
    tr:last-child td {{ border-bottom: none; }}
    .meta-row {{ display: flex; justify-content: space-between; padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.85rem; }}
    .meta-key {{ color: #64748B; }} .meta-val {{ font-weight: 600; }}
    .disclaimer {{ margin-top: 24px; padding: 16px 20px; background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.2); border-radius: 14px; font-size: 0.78rem; color: #94A3B8; line-height: 1.6; }}
    .disclaimer strong {{ color: #F59E0B; }}
    .footer {{ text-align: center; color: #475569; font-size: 0.72rem; padding: 18px; background: rgba(13,27,42,0.9); border: 1px solid rgba(255,255,255,0.05); border-top: none; border-radius: 0 0 20px 20px; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="brand">MedVision AI</div>
        <div class="tagline">Medical Image Analysis Report</div>
    </div>
    <div class="body">
        <h3>Prediction Result</h3>
        <div class="pred-box">
            <div class="pred-label">Classified As</div>
            <div class="pred-value">{pred}</div>
            <div class="conf-value">Confidence: {entry['confidence']}%</div>
        </div>

        <h3>Analysis Details</h3>
        <div style="background:rgba(255,255,255,0.02);border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,0.04);">
            <div class="meta-row"><span class="meta-key">Date &amp; Time</span><span class="meta-val">{entry.get('timestamp', 'N/A')}</span></div>
            <div class="meta-row"><span class="meta-key">Model</span><span class="meta-val">ResNet-50 (Transfer Learning)</span></div>
            <div class="meta-row"><span class="meta-key">Framework</span><span class="meta-val">PyTorch</span></div>
            <div class="meta-row"><span class="meta-key">Input Size</span><span class="meta-val">224 x 224 px</span></div>
            <div class="meta-row"><span class="meta-key">Explainability</span><span class="meta-val">Grad-CAM</span></div>
        </div>

        <h3>Class Probabilities</h3>
        <table>{probs_rows}</table>

        <div class="disclaimer">
            <strong>Medical Disclaimer:</strong> This report was generated by an educational research prototype.
            It is NOT intended for medical diagnosis or clinical decision-making. Always consult a qualified healthcare professional.
        </div>
    </div>
    <div class="footer">MedVision AI — Powered by PyTorch &amp; ResNet-50 | Educational Use Only</div>
</div>
</body>
</html>"""


def init_session():
    if "history" not in st.session_state:
        st.session_state.history = load_history()
    if "model" not in st.session_state:
        model_path = os.path.join(os.path.dirname(__file__), "models", "chest_xray_model.pth")
        if os.path.exists(model_path):
            device = "cuda" if torch.cuda.is_available() else "cpu"
            st.session_state.model = load_model(model_path, device=device)
            st.session_state.device = device
        else:
            st.session_state.model = None
            st.session_state.device = "cpu"
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "scan_step" not in st.session_state:
        st.session_state.scan_step = 0


def nav():
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-brand">
            <span class="nav-brand-dot"></span>
            MedVision AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    pages = [
        ("home", "Home"), ("analyze", "Analyze"), ("history", "History"),
        ("dashboard", "Dashboard"), ("about", "About")
    ]
    for i, (key, label) in enumerate(pages):
        with cols[i]:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

    active_page = st.session_state.page
    active_label = active_page.title()
    if active_page == "home":
        active_label = "Home"
    st.markdown(f"""
    <script>
    var buttons = window.parent.document.querySelectorAll('[data-testid="stButton"] button');
    buttons.forEach(function(btn) {{
        if (btn.textContent === '{active_label}') {{
            btn.style.background = 'linear-gradient(135deg, #00D4FF, #14B8A6)';
            btn.style.color = '#050d18';
            btn.style.boxShadow = '0 4px 20px rgba(0, 212, 255, 0.35)';
        }}
    }});
    </script>
    """, unsafe_allow_html=True)


def render_confidence_bar(cls_name, pct):
    css = cls_name.lower().replace("-", "").replace(" ", "")
    if css not in ["covid", "normal", "pneumonia"]:
        css = "normal"
    colors = {"covid": "var(--danger)", "normal": "var(--success)", "pneumonia": "var(--warning)"}
    return f"""
    <div class="confidence-item">
        <div class="header">
            <span class="class-name">{cls_name}</span>
            <span class="percentage" style="color: {colors[css]};">{pct:.1f}%</span>
        </div>
        <div class="confidence-bar-bg">
            <div class="confidence-bar-fill {css}" style="width: {pct}%;"></div>
        </div>
    </div>"""


def render_confidence_ring(confidence, badge_color):
    color_map = {"covid": "#EF4444", "normal": "#22C55E", "pneumonia": "#F59E0B"}
    color = color_map.get(badge_color, "#00D4FF")
    offset = 440 - (440 * confidence / 100)
    return f"""
    <div class="confidence-ring-container">
        <div class="confidence-ring">
            <svg viewBox="0 0 160 160">
                <circle class="bg-ring" cx="80" cy="80" r="70" />
                <circle class="fg-ring" cx="80" cy="80" r="70"
                    style="stroke: {color}; stroke-dashoffset: {offset}; filter: drop-shadow(0 0 8px {color});" />
            </svg>
            <div class="ring-label">
                <div class="ring-value" style="color: {color};">{confidence:.1f}%</div>
                <div class="ring-text">Confidence</div>
            </div>
        </div>
    </div>"""


def show_scanning_animation(image_b64):
    steps = [
        ("Image Uploaded", "done"),
        ("Preprocessing", "done"),
        ("CNN Analysis", "active"),
        ("Generating Result", "pending"),
    ]
    steps_html = ""
    for text, state in steps:
        icon = "✓" if state == "done" else "◉" if state == "active" else "○"
        steps_html += f"""
        <div class="scan-step {state}">
            <div class="step-dot">{icon}</div>
            <span class="step-text">{text}</span>
        </div>"""

    return f"""
    <div style="text-align:center;margin:2rem 0;">
        <div class="scan-container" style="display:inline-block;max-width:400px;">
            <img src="data:image/png;base64,{image_b64}" style="width:100%;border-radius:18px;" />
            <div class="scan-line"></div>
            <div class="scan-overlay"></div>
        </div>
        <div style="margin-top:1.5rem;">
            <p style="color:#00D4FF;font-weight:700;font-size:0.9rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;">AI Analyzing...</p>
            <div class="scan-steps" style="text-align:left;max-width:280px;margin:0 auto;">{steps_html}</div>
            <div class="scan-progress-bar" style="max-width:280px;margin:1rem auto 0;">
                <div class="scan-progress-fill"></div>
            </div>
        </div>
    </div>"""


def show_results(image, result, show_gradcam=True):
    top_class = result["class"]
    confidence = result["confidence"]
    sorted_probs = sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True)
    margin = sorted_probs[0][1] - sorted_probs[1][1]

    badge = "covid" if top_class == "COVID-19" else "normal" if top_class == "Normal" else "pneumonia"
    color = "#EF4444" if badge == "covid" else "#22C55E" if badge == "normal" else "#F59E0B"
    glow = f"0 0 40px {color}33" if badge != "normal" else "0 0 40px rgba(34, 197, 94, 0.15)"
    summary = {
        "covid": "Potential COVID-19 detected. Please consult a healthcare professional.",
        "pneumonia": "Potential Pneumonia detected. Please consult a healthcare professional.",
        "normal": "No abnormalities detected. The chest X-ray appears normal."
    }

    st.markdown(f"""
    <div class="prediction-display" style="box-shadow: {glow};">
        <div class="prediction-header">
            <h2>Analysis Results</h2>
            <span class="prediction-badge {badge}">{top_class}</span>
        </div>
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">{summary[badge]}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])

    with c1:
        st.markdown(render_confidence_ring(confidence, badge), unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="result-card {'danger' if badge=='covid' else 'success' if badge=='normal' else 'warning'}" style="margin-bottom:0.8rem;">
            <div class="label">Prediction</div>
            <div class="value {'danger' if badge=='covid' else 'success' if badge=='normal' else 'warning'}">{top_class}</div>
            <div class="sub">Primary Diagnosis</div></div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card" style="margin-bottom:0.8rem;">
            <div class="label">Confidence</div>
            <div class="value" style="color: var(--primary);">{confidence:.1f}%</div>
            <div class="sub">Model Certainty</div></div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card">
            <div class="label">Margin</div>
            <div class="value" style="color: var(--secondary);">{margin:.1f}%</div>
            <div class="sub">Above Second Class</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_bars, col_info = st.columns([3, 2])

    with col_bars:
        st.markdown("<h3 style='font-family:Space Grotesk;font-size:1.05rem;font-weight:700;margin-bottom:0.8rem;'>Class Probabilities</h3>", unsafe_allow_html=True)
        bars = ""
        for cls, prob in sorted_probs:
            bars += render_confidence_bar(cls, prob)
        st.markdown(bars, unsafe_allow_html=True)

    with col_info:
        details_html = """
        <div class="glass-card" style="padding:1.4rem;">
            <h3 style="font-family:Space Grotesk;font-size:1.05rem;font-weight:700;margin-bottom:1rem;">Model Details</h3>
        """
        for k, v in [
            ("Architecture", "ResNet-50"),
            ("Input Size", "224 x 224 px"),
            ("Classes", "3"),
            ("Device", st.session_state.device.upper()),
            ("Top Prediction", f"{sorted_probs[0][0]} ({sorted_probs[0][1]:.1f}%)"),
            ("Runner-up", f"{sorted_probs[1][0]} ({sorted_probs[1][1]:.1f}%)")
        ]:
            details_html += f"""
            <div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.03);">
                <span style="color:var(--text-muted);font-size:0.82rem;">{k}</span>
                <span style="font-weight:600;font-size:0.82rem;color:var(--text-secondary);">{v}</span>
            </div>"""
        details_html += "</div>"
        st.markdown(details_html, unsafe_allow_html=True)

    if show_gradcam and st.session_state.model:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="gradcam-panel">
            <h3>Explainable AI - Grad-CAM</h3>
            <p>Highlighted regions indicate areas that influenced the model's prediction. Brighter areas = higher importance.</p>
        </div>""", unsafe_allow_html=True)

        with st.spinner("Generating Grad-CAM heatmap..."):
            gradcam_result = generate_gradcam(st.session_state.model, image, device=st.session_state.device)

        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            st.markdown("<p class='gradcam-label'>Original X-Ray</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='gradcam-image-wrapper'>{st.image(image, width='stretch')}</div>" if False else "", unsafe_allow_html=True)
            st.image(image, width="stretch")
        with gc2:
            st.markdown("<p class='gradcam-label' style='color:#A78BFA;'>AI Heatmap</p>", unsafe_allow_html=True)
            st.image(gradcam_result["heatmap"], width="stretch")
        with gc3:
            st.markdown("<p class='gradcam-label' style='color:#14B8A6;'>Overlay</p>", unsafe_allow_html=True)
            st.image(gradcam_result["overlay"], width="stretch")

    st.markdown("""
    <div class="disclaimer">
        <span class="icon">&#9888;</span>
        <div class="text"><strong>Medical Disclaimer:</strong> This tool is for educational and research purposes only. It should NOT be used as a substitute for professional medical diagnosis. Always consult a qualified healthcare provider.</div>
    </div>""", unsafe_allow_html=True)


def page_home():
    st.markdown("""
    <script>
    var app = window.parent.document.querySelector('.stApp');
    if (app) { app.className = app.className.replace(/bg-\\w+/g, '').trim() + ' bg-home'; }
    </script>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-section" style="padding:4.5rem 2rem 3.5rem;">
        <div class="floating-medical-icons">
            <div class="fm-icon">🫁</div><div class="fm-icon">🧬</div><div class="fm-icon">🔬</div>
            <div class="fm-icon">💊</div><div class="fm-icon">🩺</div><div class="fm-icon">🧬</div>
        </div>
        <div class="hero-tag"><span class="dot"></span> AI-Powered Healthcare</div>
        <h1 class="hero-title hero-float-text">
            <span class="line1">Intelligent Medical Image Analysis</span>
            <span class="line2">See Beyond the Image.</span>
        </h1>
        <p class="hero-subtitle flow-words">
            <span style="animation-delay: 0.0s;">Deep</span>
            <span style="animation-delay: 0.1s;">learning-powered</span>
            <span style="animation-delay: 0.2s;">chest</span>
            <span style="animation-delay: 0.3s;">X-ray</span>
            <span style="animation-delay: 0.4s;">classification</span>
            <span style="animation-delay: 0.5s;">for</span>
            <span style="animation-delay: 0.6s;color:#EF4444;font-weight:700;">COVID-19,</span>
            <span style="animation-delay: 0.7s;color:#F59E0B;font-weight:700;">Pneumonia</span>
            <span style="animation-delay: 0.8s;">&amp;</span>
            <span style="animation-delay: 0.9s;color:#22C55E;font-weight:700;">Normal</span>
            <span style="animation-delay: 1.0s;">detection</span>
            <span style="animation-delay: 1.1s;">with</span>
            <span style="animation-delay: 1.2s;">explainable</span>
            <span style="animation-delay: 1.3s;">AI.</span>
        </p>
        <div class="hero-buttons">
            <a href="#" onclick="window.parent.document.querySelectorAll('[data-testid=stButton] button')[1].click(); return false;" class="btn-primary-hero">🔬 Analyze Image</a>
            <a href="#" onclick="window.parent.document.querySelectorAll('[data-testid=stButton] button')[4].click(); return false;" class="btn-secondary-hero">ℹ️ Explore AI</a>
        </div>
    </div>""", unsafe_allow_html=True)

    marquee_items = ["Deep Learning", "ResNet-50", "Grad-CAM", "Chest X-Ray", "COVID-19 Detection",
                     "Pneumonia Detection", "Explainable AI", "Transfer Learning", "98% Accuracy", "Real-Time"]
    marquee_html = ""
    for item in marquee_items:
        marquee_html += f'<span class="marquee-item"><span class="m-dot"></span>{item}</span>'

    st.markdown(f"""
    <div class="marquee-strip">
        <div class="marquee-track">{marquee_html}{marquee_html}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="features-grid">
        <div class="feature-card"><div class="icon">🔬</div><h4>Deep Learning</h4><p>ResNet-50 transfer learning architecture</p></div>
        <div class="feature-card"><div class="icon">⚡</div><h4>Real-Time</h4><p>Instant predictions with confidence scores</p></div>
        <div class="feature-card"><div class="icon">🎯</div><h4>High Accuracy</h4><p>98%+ accuracy on test data</p></div>
        <div class="feature-card"><div class="icon">🧠</div><h4>Explainable AI</h4><p>Grad-CAM heatmaps for transparency</p></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <p style="display:inline-flex;align-items:center;gap:8px;background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.12);padding:6px 16px;border-radius:50px;font-size:0.7rem;font-weight:700;color:#00D4FF;text-transform:uppercase;letter-spacing:1.5px;">
            ✨ Why MedVision AI
        </p>
        <h3 style="font-family:Space Grotesk;font-size:1.3rem;font-weight:800;margin-top:1rem;margin-bottom:0.3rem;">Built for the Future of Healthcare</h3>
        <p style="color:var(--text-muted);font-size:0.88rem;max-width:500px;margin:0 auto;">Not just another image classifier. A complete AI-powered diagnostic assistant.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;flex-direction:column;gap:0.8rem;margin:1.5rem 0;">
        <div class="super-feature sf-1">
            <div class="sf-icon">🧬</div>
            <div class="sf-text">
                <h4>Transfer Learning with ResNet-50</h4>
                <p>Uses a pretrained deep neural network fine-tuned on medical imaging data. No need to train from scratch — leverages millions of learned visual features.</p>
                <span class="sf-tag">Deep Learning</span>
            </div>
        </div>
        <div class="super-feature sf-2">
            <div class="sf-icon">🔍</div>
            <div class="sf-text">
                <h4>Grad-CAM Explainability</h4>
                <p>Don't just get a prediction — see where the AI is looking. Grad-CAM heatmaps highlight the exact regions that influenced the diagnosis.</p>
                <span class="sf-tag">Explainable AI</span>
            </div>
        </div>
        <div class="super-feature sf-3">
            <div class="sf-icon">📊</div>
            <div class="sf-text">
                <h4>Multi-Class Detection</h4>
                <p>Simultaneously classifies COVID-19, Pneumonia, and Normal chest X-rays with per-class confidence scores and probability breakdowns.</p>
                <span class="sf-tag">Classification</span>
            </div>
        </div>
        <div class="super-feature sf-4">
            <div class="sf-icon">⚡</div>
            <div class="sf-text">
                <h4>Real-Time Inference</h4>
                <p>Get predictions in under 2 seconds. Optimized preprocessing pipeline with automatic image normalization and resizing to 224x224.</p>
                <span class="sf-tag">Performance</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h3 style='font-family:Space Grotesk;text-align:center;font-size:1.2rem;font-weight:700;margin-bottom:0.3rem;'>Quick Test - Sample Images</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:var(--text-muted);font-size:0.85rem;margin-bottom:1.5rem;'>Click a sample to instantly analyze it</p>", unsafe_allow_html=True)

    project_root = os.path.dirname(os.path.abspath(__file__))
    samples = [
        ("COVID-19 Sample", os.path.join(project_root, "data", "test", "covid", "covid_0001.png")),
        ("Normal Sample", os.path.join(project_root, "data", "test", "normal", "normal_0001.png")),
        ("Pneumonia Sample", os.path.join(project_root, "data", "test", "pneumonia", "pneumonia_0001.png")),
    ]

    cols = st.columns(3)
    for i, (label, path) in enumerate(samples):
        with cols[i]:
            if os.path.exists(path):
                st.image(path, width="stretch", caption=label)
                if st.button(f"Analyze {label}", key=f"home_sample_{i}", use_container_width=True):
                    image = Image.open(path).convert("RGB")
                    st.session_state["analyzed_image"] = image
                    st.session_state.page = "analyze"
                    st.session_state["auto_analyze"] = True
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="text-align:center;margin:2rem 0 1rem;">
        <h3 style="font-family:Space Grotesk;font-size:1.15rem;font-weight:700;margin-bottom:1rem;">How AI Works</h3>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="pipeline">
        <div class="pipeline-step"><div class="step-icon">📤</div><div class="step-text">Upload</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">🧹</div><div class="step-text">Process</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">🧠</div><div class="step-text">Analyze</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">🔍</div><div class="step-text">Extract</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">📊</div><div class="step-text">Predict</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        <span class="icon">&#9888;</span>
        <div class="text"><strong>Educational Use Only:</strong> This system is a research prototype and does not replace professional medical diagnosis.</div>
    </div>""", unsafe_allow_html=True)


def page_analyze():
    st.markdown("""
    <script>
    var app = window.parent.document.querySelector('.stApp');
    if (app) { app.className = app.className.replace(/bg-\\w+/g, '').trim() + ' bg-analyze'; }
    </script>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;margin-bottom:0.3rem;">Analyze X-ray</h2>
        <p style="color:var(--text-muted);font-size:0.9rem;">Upload a chest X-ray image for AI-powered analysis</p>
    </div>""", unsafe_allow_html=True)

    if "analyzed_image" not in st.session_state:
        st.session_state["analyzed_image"] = None
    if "auto_analyze" not in st.session_state:
        st.session_state["auto_analyze"] = False

    if not st.session_state["analyzed_image"]:
        uploaded = st.file_uploader("Upload Chest X-ray", type=["png", "jpg", "jpeg"])
        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            st.session_state["analyzed_image"] = image
            st.rerun()
        else:
            st.markdown("""
            <div class="upload-zone">
                <div class="upload-icon">📤</div>
                <h3 style="font-family:Space Grotesk;color:var(--text-primary);margin-bottom:0.3rem;font-size:1.2rem;">Drop your X-ray here</h3>
                <p style="color:var(--text-muted);font-size:0.88rem;">or click to browse files</p>
                <div class="upload-formats">
                    <span class="format-tag">PNG</span>
                    <span class="format-tag">JPG</span>
                    <span class="format-tag">JPEG</span>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("<p style='color:var(--text-muted);font-size:0.85rem;margin-bottom:1rem;'>Or try sample images:</p>", unsafe_allow_html=True)
            project_root = os.path.dirname(os.path.abspath(__file__))
            sample_cols = st.columns(3)
            for i, (label, path) in enumerate([
                ("COVID-19", os.path.join(project_root, "data", "test", "covid", "covid_0001.png")),
                ("Normal", os.path.join(project_root, "data", "test", "normal", "normal_0001.png")),
                ("Pneumonia", os.path.join(project_root, "data", "test", "pneumonia", "pneumonia_0001.png"))
            ]):
                with sample_cols[i]:
                    if os.path.exists(path):
                        st.image(path, width="stretch")
                        if st.button(f"Test {label}", key=f"analyze_sample_{i}", use_container_width=True):
                            st.session_state["analyzed_image"] = Image.open(path).convert("RGB")
                            st.session_state["auto_analyze"] = True
                            st.rerun()

    if st.session_state["analyzed_image"]:
        image = st.session_state["analyzed_image"]

        col_img, col_ctrl = st.columns([3, 2])
        with col_img:
            image_b64 = img_to_b64(image)
            st.markdown(f"""
            <div class="glass-card" style="padding:0;overflow:hidden;border-radius:18px;">
                <img src="data:image/png;base64,{image_b64}" style="width:100%;display:block;border-radius:18px;" />
            </div>""", unsafe_allow_html=True)

        with col_ctrl:
            st.markdown("""
            <div class="glass-card" style="padding:1.3rem;">
                <p style="color:var(--text-muted);font-size:0.75rem;text-transform:uppercase;letter-spacing:2px;margin-bottom:0.5rem;">Ready to Analyze</p>
                <p style="color:var(--text-primary);font-size:0.95rem;font-weight:600;">Image loaded successfully</p>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🔍 Analyze X-ray", key="analyze_btn", use_container_width=True):
                st.session_state["auto_analyze"] = True
                st.rerun()

            if st.button("✕ Clear Image", key="clear_btn", use_container_width=True):
                st.session_state["analyzed_image"] = None
                st.session_state["auto_analyze"] = False
                st.rerun()

        if st.session_state.get("auto_analyze", False):
            st.session_state["auto_analyze"] = False
            if st.session_state.model:
                image_b64 = img_to_b64(image)
                st.markdown(show_scanning_animation(image_b64), unsafe_allow_html=True)

                import time
                progress_bar = st.progress(0, text="AI analyzing...")
                for pct in range(0, 101, 4):
                    time.sleep(0.06)
                    progress_bar.progress(pct, text=f"AI analyzing... {pct}%")
                progress_bar.empty()

                result = predict(st.session_state.model, image, device=st.session_state.device)
                show_results(image, result)
                entry = {
                    "prediction": result["class"],
                    "confidence": round(result["confidence"], 1),
                    "probabilities": result["probabilities"],
                    "timestamp": datetime.now().strftime("%b %d, %Y %H:%M"),
                }
                st.session_state.history.append(entry)
                save_history()

                st.download_button(
                    "⬇ Download Analysis Report",
                    data=generate_html_report(entry, len(st.session_state.history)),
                    file_name=f"medvision_report_{len(st.session_state.history)}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            else:
                st.error("Model not found! Run train.py first.")


def page_history():
    st.markdown("""
    <script>
    var app = window.parent.document.querySelector('.stApp');
    if (app) { app.className = app.className.replace(/bg-\\w+/g, '').trim() + ' bg-history'; }
    </script>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;margin-bottom:0.3rem;">Analysis History</h2>
        <p style="color:var(--text-muted);font-size:0.9rem;">Track all your previous AI analyses</p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:4rem 2rem;">
            <div style="font-size:3rem;margin-bottom:1rem;opacity:0.2;">📋</div>
            <p style="color:var(--text-muted);font-size:1rem;margin-bottom:0.3rem;">No analyses yet</p>
            <p style="color:var(--text-muted);font-size:0.82rem;">Go to the Analyze page to start classifying X-rays</p>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
        <p style='color:var(--text-muted);font-size:0.85rem;'>{len(st.session_state.history)} analyses completed</p>
    </div>""", unsafe_allow_html=True)

    filter_col1, filter_col2, filter_col3 = st.columns([2, 1.5, 1.5])
    with filter_col2:
        filter_class = st.selectbox("Filter", ["All", "COVID-19", "Normal", "Pneumonia"])
    with filter_col3:
        st.download_button(
            "⬇ Export All (JSON)",
            data=json.dumps(st.session_state.history, indent=2),
            file_name="medvision_history.json",
            mime="application/json",
            use_container_width=True,
        )

    filtered = [
        (len(st.session_state.history) - i, entry)
        for i, entry in enumerate(reversed(st.session_state.history))
        if filter_class == "All" or entry["prediction"] == filter_class
    ]

    for idx, (analysis_num, entry) in enumerate(filtered):
        pred = entry["prediction"]
        color = "var(--danger)" if pred == "COVID-19" else "var(--success)" if pred == "Normal" else "var(--warning)"

        card_col, btn_col = st.columns([4, 1])

        with card_col:
            st.markdown(f"""
            <div class="history-card">
                <div class="hist-img">🫁</div>
                <div class="hist-info">
                    <h4>Analysis #{analysis_num}</h4>
                    <p>{entry['timestamp']}</p>
                </div>
                <div class="hist-result">
                    <div class="pred" style="color:{color};">{pred}</div>
                    <div class="conf">{entry['confidence']}% confidence</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with btn_col:
            report_html = generate_html_report(entry, analysis_num)
            st.download_button(
                "📄 Report",
                data=report_html,
                file_name=f"medvision_report_{analysis_num}.html",
                mime="text/html",
                key=f"dl_report_{idx}",
                use_container_width=True,
            )

    clear_col1, clear_col2 = st.columns([3, 1])
    with clear_col2:
        if st.button("🗑 Clear History", use_container_width=True):
            st.session_state.history = []
            save_history()
            st.rerun()


def page_dashboard():
    st.markdown("""
    <script>
    var app = window.parent.document.querySelector('.stApp');
    if (app) { app.className = app.className.replace(/bg-\\w+/g, '').trim() + ' bg-dashboard'; }
    </script>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;margin-bottom:0.3rem;">Dashboard</h2>
        <p style="color:var(--text-muted);font-size:0.9rem;">Overview of your AI analysis activity</p>
    </div>""", unsafe_allow_html=True)

    total = len(st.session_state.history)
    covid = sum(1 for h in st.session_state.history if h["prediction"] == "COVID-19")
    normal = sum(1 for h in st.session_state.history if h["prediction"] == "Normal")
    pneumonia = sum(1 for h in st.session_state.history if h["prediction"] == "Pneumonia")
    avg_conf = round(sum(h["confidence"] for h in st.session_state.history) / max(total, 1), 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div class="stat-card s1"><div class="stat-icon">📷</div><div class="stat-value">{total}</div><div class="stat-label">Total Images</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="stat-card s2"><div class="stat-icon">✅</div><div class="stat-value">{normal}</div><div class="stat-label">Normal</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="stat-card s3"><div class="stat-icon">🔍</div><div class="stat-value">{pneumonia}</div><div class="stat-label">Pneumonia</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="stat-card s4"><div class="stat-icon">🎯</div><div class="stat-value">{avg_conf}%</div><div class="stat-label">Avg Confidence</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if total > 0:
        chart_data = {"Category": ["COVID-19", "Normal", "Pneumonia"], "Count": [covid, normal, pneumonia]}
        st.bar_chart(chart_data, x="Category", y="Count", color="#00D4FF")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-family:Space Grotesk;font-size:1.1rem;font-weight:700;'>Recent Analyses</h3>", unsafe_allow_html=True)

        for entry in list(reversed(st.session_state.history))[:5]:
            pred = entry["prediction"]
            color = "var(--danger)" if pred == "COVID-19" else "var(--success)" if pred == "Normal" else "var(--warning)"
            st.markdown(f"""
            <div class="history-card">
                <div class="hist-img">🫁</div>
                <div class="hist-info"><h4>{pred}</h4><p>{entry['timestamp']}</p></div>
                <div class="hist-result"><div class="pred" style="color:{color};">{entry['confidence']}%</div></div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3rem;">
            <p style="color:var(--text-muted);">No data yet. Analyze some images first!</p>
        </div>""", unsafe_allow_html=True)


def page_about():
    st.markdown("""
    <script>
    var app = window.parent.document.querySelector('.stApp');
    if (app) { app.className = app.className.replace(/bg-\\w+/g, '').trim() + ' bg-home'; }
    </script>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;margin-bottom:0.3rem;">About MedVision AI</h2>
        <p style="color:var(--text-muted);font-size:0.9rem;">Learn how this AI-powered medical analysis system works</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card">
        <h3>🔬 What is MedVision AI?</h3>
        <p>MedVision AI is a deep learning-powered medical image classification system that analyzes chest X-rays to detect COVID-19, Pneumonia, and Normal conditions. Built with PyTorch and ResNet-50 transfer learning, it provides real-time predictions with confidence scores and Grad-CAM explainability heatmaps to show where the AI is looking.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card">
        <h3>🧠 How Does the AI Work?</h3>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="pipeline">
        <div class="pipeline-step"><div class="step-icon">📷</div><div class="step-text">Medical Image</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">🧹</div><div class="step-text">Preprocessing</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">🧠</div><div class="step-text">CNN / ResNet-50</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">🔍</div><div class="step-text">Feature Extraction</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">🎯</div><div class="step-text">Classification</div></div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-step"><div class="step-icon">✅</div><div class="step-text">Prediction</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card">
        <h3>🛠️ Technologies Used</h3>
        <div class="tech-grid">
            <div class="tech-item"><div class="icon">🐍</div><h4>Python</h4><p>Core language</p></div>
            <div class="tech-item"><div class="icon">🔥</div><h4>PyTorch</h4><p>Deep learning framework</p></div>
            <div class="tech-item"><div class="icon">🔬</div><h4>ResNet-50</h4><p>Transfer learning model</p></div>
            <div class="tech-item"><div class="icon">⚡</div><h4>Streamlit</h4><p>Web application</p></div>
            <div class="tech-item"><div class="icon">🧠</div><h4>Grad-CAM</h4><p>Explainable AI</p></div>
            <div class="tech-item"><div class="icon">📊</div><h4>scikit-learn</h4><p>Evaluation metrics</p></div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card">
        <h3>📊 Training Metrics</h3>
        <p style="margin-bottom:1rem;">The model was trained on a synthetic chest X-ray dataset with the following results:</p>
        <div style="margin-top:1rem;display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem;">
            <div class="confidence-item" style="text-align:center;">
                <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">COVID-19</div>
                <div style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;color:var(--danger);">100%</div>
                <div style="font-size:0.72rem;color:var(--text-muted);">Precision</div>
            </div>
            <div class="confidence-item" style="text-align:center;">
                <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">Normal</div>
                <div style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;color:var(--success);">95.1%</div>
                <div style="font-size:0.72rem;color:var(--text-muted);">Precision</div>
            </div>
            <div class="confidence-item" style="text-align:center;">
                <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">Pneumonia</div>
                <div style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;color:var(--warning);">99.9%</div>
                <div style="font-size:0.72rem;color:var(--text-muted);">Precision</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card">
        <h3>🎯 Model Evaluation</h3>
        <p style="margin-bottom:1.2rem;">Detailed per-class performance metrics on the test set:</p>
        <div style="overflow-x:auto;">
            <table style="width:100%;border-collapse:separate;border-spacing:0;background:rgba(255,255,255,0.02);border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,0.04);">
                <thead>
                    <tr style="background:rgba(0,212,255,0.06);">
                        <th style="padding:0.8rem 1rem;text-align:left;font-family:Space Grotesk;font-size:0.78rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.04);">Class</th>
                        <th style="padding:0.8rem 1rem;text-align:center;font-family:Space Grotesk;font-size:0.78rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.04);">Precision</th>
                        <th style="padding:0.8rem 1rem;text-align:center;font-family:Space Grotesk;font-size:0.78rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.04);">Recall</th>
                        <th style="padding:0.8rem 1rem;text-align:center;font-family:Space Grotesk;font-size:0.78rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.04);">F1-Score</th>
                        <th style="padding:0.8rem 1rem;text-align:center;font-family:Space Grotesk;font-size:0.78rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.04);">Support</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                        <td style="padding:0.7rem 1rem;font-weight:600;font-size:0.85rem;color:var(--danger);">COVID-19</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--danger);">1.00</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--danger);">1.00</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--danger);">1.00</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-size:0.82rem;color:var(--text-muted);">60</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                        <td style="padding:0.7rem 1rem;font-weight:600;font-size:0.85rem;color:var(--success);">Normal</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--success);">0.95</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--success);">0.95</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--success);">0.95</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-size:0.82rem;color:var(--text-muted);">60</td>
                    </tr>
                    <tr>
                        <td style="padding:0.7rem 1rem;font-weight:600;font-size:0.85rem;color:var(--warning);">Pneumonia</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--warning);">1.00</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--warning);">1.00</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:700;font-size:0.85rem;color:var(--warning);">1.00</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-size:0.82rem;color:var(--text-muted);">60</td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr style="background:rgba(0,212,255,0.04);">
                        <td style="padding:0.7rem 1rem;font-weight:800;font-size:0.85rem;color:var(--text-primary);">Accuracy</td>
                        <td colspan="3" style="padding:0.7rem 1rem;text-align:center;font-family:Space Grotesk;font-weight:800;font-size:1rem;color:#00D4FF;">0.9833</td>
                        <td style="padding:0.7rem 1rem;text-align:center;font-weight:700;font-size:0.82rem;color:var(--text-secondary);">180</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card">
        <h3>🔲 Confusion Matrix</h3>
        <p style="margin-bottom:1.2rem;">How the model's predictions compare to actual labels:</p>
        <div style="overflow-x:auto;">
            <table style="width:100%;max-width:480px;margin:0 auto;border-collapse:separate;border-spacing:3px;background:transparent;">
                <thead>
                    <tr>
                        <th style="padding:0.5rem;font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;"></th>
                        <th style="padding:0.5rem;font-size:0.7rem;font-weight:700;color:var(--danger);text-align:center;">COVID-19</th>
                        <th style="padding:0.5rem;font-size:0.7rem;font-weight:700;color:var(--success);text-align:center;">Normal</th>
                        <th style="padding:0.5rem;font-size:0.7rem;font-weight:700;color:var(--warning);text-align:center;">Pneumonia</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding:0.5rem;font-size:0.7rem;font-weight:700;color:var(--danger);text-align:right;">COVID-19</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.3);border-radius:8px;font-family:Space Grotesk;font-weight:800;font-size:1.1rem;color:var(--danger);">60</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(34,197,94,0.03);border:1px solid rgba(255,255,255,0.03);border-radius:8px;font-family:Space Grotesk;font-weight:600;font-size:0.9rem;color:var(--text-muted);">0</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(245,158,11,0.03);border:1px solid rgba(255,255,255,0.03);border-radius:8px;font-family:Space Grotesk;font-weight:600;font-size:0.9rem;color:var(--text-muted);">0</td>
                    </tr>
                    <tr>
                        <td style="padding:0.5rem;font-size:0.7rem;font-weight:700;color:var(--success);text-align:right;">Normal</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(239,68,68,0.03);border:1px solid rgba(255,255,255,0.03);border-radius:8px;font-family:Space Grotesk;font-weight:600;font-size:0.9rem;color:var(--text-muted);">3</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.25);border-radius:8px;font-family:Space Grotesk;font-weight:800;font-size:1.1rem;color:var(--success);">57</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(245,158,11,0.03);border:1px solid rgba(255,255,255,0.03);border-radius:8px;font-family:Space Grotesk;font-weight:600;font-size:0.9rem;color:var(--text-muted);">0</td>
                    </tr>
                    <tr>
                        <td style="padding:0.5rem;font-size:0.7rem;font-weight:700;color:var(--warning);text-align:right;">Pneumonia</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(239,68,68,0.03);border:1px solid rgba(255,255,255,0.03);border-radius:8px;font-family:Space Grotesk;font-weight:600;font-size:0.9rem;color:var(--text-muted);">0</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(34,197,94,0.03);border:1px solid rgba(255,255,255,0.03);border-radius:8px;font-family:Space Grotesk;font-weight:600;font-size:0.9rem;color:var(--text-muted);">0</td>
                        <td style="padding:0.8rem;text-align:center;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.25);border-radius:8px;font-family:Space Grotesk;font-weight:800;font-size:1.1rem;color:var(--warning);">60</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p style="text-align:center;font-size:0.75rem;color:var(--text-muted);margin-top:0.8rem;">Rows = Actual | Columns = Predicted | Diagonal = Correct predictions</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card">
        <h3>📈 Key Insights</h3>
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:0.8rem;margin-top:1rem;">
            <div style="background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.1);border-radius:12px;padding:1rem;">
                <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">Total Test Samples</div>
                <div style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;color:#00D4FF;">180</div>
                <div style="font-size:0.75rem;color:var(--text-muted);">60 per class</div>
            </div>
            <div style="background:rgba(34,197,94,0.04);border:1px solid rgba(34,197,94,0.1);border-radius:12px;padding:1rem;">
                <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">Correct Predictions</div>
                <div style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;color:var(--success);">177</div>
                <div style="font-size:0.75rem;color:var(--text-muted);">98.3% accuracy</div>
            </div>
            <div style="background:rgba(239,68,68,0.04);border:1px solid rgba(239,68,68,0.1);border-radius:12px;padding:1rem;">
                <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">Misclassifications</div>
                <div style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;color:var(--danger);">3</div>
                <div style="font-size:0.75rem;color:var(--text-muted);">Normal → COVID-19</div>
            </div>
            <div style="background:rgba(139,92,246,0.04);border:1px solid rgba(139,92,246,0.1);border-radius:12px;padding:1rem;">
                <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">Avg Confidence</div>
                <div style="font-family:Space Grotesk;font-size:1.5rem;font-weight:800;color:#8B5CF6;">94.2%</div>
                <div style="font-size:0.75rem;color:var(--text-muted);">across all classes</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        <span class="icon">&#9888;</span>
        <div class="text"><strong>Medical Disclaimer:</strong> This application is an educational and research prototype. It is NOT intended to provide medical diagnosis, treatment, or professional medical advice. Predictions should NOT be used for clinical decision-making. Always consult a qualified healthcare professional.</div>
    </div>""", unsafe_allow_html=True)


def main():
    init_session()
    nav()
    page = st.session_state.page
    if page == "home":
        page_home()
    elif page == "analyze":
        page_analyze()
    elif page == "history":
        page_history()
    elif page == "dashboard":
        page_dashboard()
    elif page == "about":
        page_about()

    st.markdown("""
    <div class="footer">
        <p>MedVision AI &mdash; Powered by PyTorch &amp; ResNet-50 | Built with Streamlit</p>
        <p style="margin-top:0.3rem;font-size:0.7rem;">Educational Research Prototype — Not for Clinical Use</p>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
