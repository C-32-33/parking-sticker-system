# utils/theme.py
import streamlit as st
import config

def apply_theme():
    """Apply professional theme, banner, and footer to all pages"""
    st.markdown(f"""
        <style>
        /* Hide default streamlit elements */
        #MainMenu {{visibility: hidden;}}

        /* Main container */
        .main .block-container {{
            padding-top: 1rem;
            padding-bottom: 5rem;
            max-width: 1400px;
        }}

        /* Professional buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {config.COLOR_PRIMARY} 0%, {config.COLOR_SECONDARY} 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}

        /* Metric cards */
        [data-testid="stMetric"] {{
            background: white;
            border-left: 4px solid {config.COLOR_PRIMARY};
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        /* Data table styling */
        [data-testid="stDataFrame"] {{
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {config.COLOR_DARK} 0%, {config.COLOR_SECONDARY} 100%);
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def render_banner(subtitle="Parking Sticker Management System"):
    """Fixed size top banner"""
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {config.COLOR_PRIMARY} 0%, {config.COLOR_SECONDARY} 100%);
            padding: 25px 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        '>
            <div style='display: flex; align-items: center; gap: 20px;'>
                <div style='
                    background: white;
                    color: {config.COLOR_PRIMARY};
                    width: 70px; height: 70px;
                    border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 40px; font-weight: bold;
                '>P</div>
                <div>
                    <h1 style='color: white; margin: 0; font-size: 28px;'>{config.SOCIETY_NAME}</h1>
                    <p style='color: #E3F2FD; margin: 5px 0 0 0; font-size: 15px;'>{subtitle}</p>
                    <p style='color: #BBDEFB; margin: 2px 0 0 0; font-size: 12px;'>{config.SOCIETY_ADDRESS}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Fixed bottom footer with legal warning"""
    st.markdown(f"""
        <div style='
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: {config.COLOR_DARK};
            border-top: 4px solid {config.COLOR_ACCENT};
            padding: 12px 30px;
            z-index: 999;
            text-align: center;
        '>
            <p style='color: #FFC107; margin: 0; font-size: 12px; font-weight: 600;'>
                ⚠️ {config.LEGAL_WARNING}
            </p>
            <p style='color: #90A4AE; margin: 3px 0 0 0; font-size: 11px;'>
                © {config.SOCIETY_NAME} | {config.SOCIETY_ADDRESS} | Contact: {config.SOCIETY_CONTACT}
            </p>
        </div>
    """, unsafe_allow_html=True)