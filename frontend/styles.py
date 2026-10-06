"""CSS styles and HTML visual helpers for professional UI design."""

from __future__ import annotations

import streamlit as st

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main layout container styling */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1240px;
    }
    
    /* Header Banner */
    .header-box {
        background: linear-gradient(135deg, #0b1329 0%, #1e293b 50%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        color: #f8fafc;
        box-shadow: 0 20px 30px -10px rgba(15, 23, 42, 0.5);
    }
    .header-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0 0 8px 0;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .header-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin: 0;
        font-weight: 500;
    }

    /* Feature Highlight Pill Badges */
    .feature-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(51, 65, 85, 0.8);
        color: #cbd5e1;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 14px;
        margin-right: 8px;
    }

    /* Tech badge chips */
    .tech-chip {
        display: inline-flex;
        align-items: center;
        background-color: #0f172a;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 8px;
        padding: 5px 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Metric Cards Override */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #f8fafc !important;
        font-weight: 800 !important;
    }

    /* Security callout alert */
    .security-callout {
        background: rgba(120, 53, 15, 0.2);
        border: 1px solid #d97706;
        border-radius: 10px;
        padding: 14px 18px;
        color: #fde68a;
        font-size: 0.9rem;
        margin-top: 16px;
    }
</style>
"""


def apply_custom_css():
    """Inject custom CSS into Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
