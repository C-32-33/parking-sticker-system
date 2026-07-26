import streamlit as st
import config

def apply_theme():
    st.markdown(f"""
        <style>
        /* Responsive Design - Auto-scale for all devices */
        @media (max-width: 768px) {{
            .main > div {{
                padding-left: 10px;
                padding-right: 10px;
            }}
            h1 {{ font-size: 1.5rem !important; }}
            h2 {{ font-size: 1.3rem !important; }}
            h3 {{ font-size: 1.1rem !important; }}
            .stButton > button {{
                width: 100%;
                font-size: 14px;
            }}
            .stTextInput > div > input,
            .stSelectbox > div > select {{
                font-size: 14px;
            }}
        }}
        
        @media (max-width: 480px) {{
            h1 {{ font-size: 1.3rem !important; }}
            h2 {{ font-size: 1.1rem !important; }}
            .css-1r6slb0 {{
                padding: 0.5rem;
            }}
        }}
        
        /* Main container */
        .main {{
            background-color: #f5f5f5;
        }}
        
        /* Sidebar */
        .css-1d391kg {{
            background-color: {config.COLOR_SIDEBAR};
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {config.COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .stButton > button:hover {{
            background-color: {config.COLOR_ACCENT};
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        /* Cards */
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid {config.COLOR_PRIMARY};
            margin: 10px 0;
        }}
        
        /* Banner */
        .banner {{
            background: linear-gradient(135deg, {config.COLOR_PRIMARY} 0%, {config.COLOR_ACCENT} 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        
        /* Footer */
        .footer {{
            background-color: {config.COLOR_SIDEBAR};
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            margin-top: 50px;
            font-size: 12px;
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: white;
            border-radius: 8px;
            padding: 15px;
        }}
        
        /* Mobile-friendly columns */
        .stColumns > div {{
            padding: 5px;
        }}
        </style>
    """, unsafe_allow_html=True)

def render_banner(title="Parking Sticker Management System"):
    st.markdown(f"""
        <div class='banner'>
            <div style='display: flex; align-items: center; gap: 20px;'>
                <div style='
                    background: white;
                    color: {config.COLOR_PRIMARY};
                    width: 60px; height: 60px;
                    border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 36px; font-weight: bold;
                    flex-shrink: 0;
                '>P</div>
                <div style='flex: 1;'>
                    <h1 style='margin: 0; font-size: 24px;'>{title}</h1>
                    <p style='margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;'>
                        C-32/33 Poonam Nagar CHS | Buildings C-32 & C-33
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown(f"""
        <div class='footer'>
            <p style='margin: 0;'>
                © C-32/33 Poonam Nagar CHS | Unauthorized use, duplication or transfer is strictly prohibited and punishable under society bylaws.
            </p>
            <p style='margin: 5px 0 0 0; opacity: 0.8;'>
                Buildings C-32 & C-33 | Contact: +91-12345678
            </p>
        </div>
    """, unsafe_allow_html=True)
