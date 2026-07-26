import streamlit as st
from utils.theme import apply_theme, render_banner, render_footer
from utils.sheets import get_sheets_handler
import config

st.set_page_config(
    page_title="Parking Sticker Manager",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "show_qr" not in st.session_state:
    st.session_state.show_qr = None

# Check for sticker_id in URL (public QR scan redirect)
query_params = st.query_params
if "sticker_id" in query_params:
    st.switch_page("pages/6_Public_Verify.py")

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.get("authenticated"):
    render_banner("Parking Sticker Management System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div style='
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                border-top: 4px solid {config.COLOR_PRIMARY};
            '>
                <h2 style='color: {config.COLOR_PRIMARY}; text-align: center; margin-top: 0;'>
                    🔒 Secure Login
                </h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        username = st.text_input(" Username", placeholder="Enter username")
        password = st.text_input("🔑 Password", type="password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if not username or not password:
                st.error("❌ Please enter username and password")
            else:
                # Fetch users from Google Sheet
                sheets = get_sheets_handler()
                users = sheets._get_data("Users")
                
                # Find matching user
                user_found = None
                for u in users:
                    if (str(u.get("Username")).strip().lower() == username.strip().lower() and 
                        str(u.get("PasswordHash")) == password and
                        str(u.get("Status")).strip().lower() == "active"):
                        user_found = u
                        break
                
                if user_found:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = user_found.get("Role", "Member")
                    st.session_state.user_email = user_found.get("Email", "")
                    st.success(f"✅ Welcome, {user_found.get('Username')}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials or account inactive")
        
        st.info("""
            **Demo Logins:**
            - Admin: admin / admin123
            - Committee: ravi32 / ravi@32
            - Member: bankim33 / bankim@33
        """)
    
    render_footer()

# ==========================================
# HOME PAGE (Authenticated)
# ==========================================
else:
    render_banner(f"Welcome, {st.session_state.username}")
    
    with st.sidebar:
        st.markdown(f"""
            <div style='padding: 20px; text-align: center;'>
                <div style='
                    background: white;
                    color: {config.COLOR_PRIMARY};
                    width: 60px; height: 60px;
                    border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 30px; font-weight: bold;
                    margin: 0 auto 10px auto;
                '></div>
                <h3 style='margin: 0;'>{st.session_state.username}</h3>
                <p style='margin: 5px 0; font-size: 13px; color: #666;'>Role: {st.session_state.user_role}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ALL users can see these (Read-only access)
        st.page_link("pages/1_Dashboard.py", label="📊 Dashboard", icon="📊")
        st.page_link("pages/3_Verify_Sticker.py", label="🔍 Verify Sticker", icon="")
        st.page_link("pages/6_Public_Verify.py", label="🌐 Public Verify", icon="🌐")
        st.page_link("pages/7_Sticker_Viewer.py", label="🔎 Sticker Viewer", icon="")
        
        # Committee and Admin can see these (Add & Generate)
        if st.session_state.user_role in ["Admin", "Committee"]:
            st.markdown("---")
            st.markdown("**Management**")
            st.page_link("pages/2_Generate_Stickers.py", label="🎫 Generate Stickers", icon="🎫")
            st.page_link("pages/4_Manage_Members.py", label="👥 Manage Members", icon="👥")
        
        # Only Admin can see these
        if st.session_state.user_role == "Admin":
            st.markdown("---")
            st.markdown("**Admin Panel**")
            st.page_link("pages/5_Reports.py", label="📈 Reports", icon="📈")
            st.page_link("pages/8_User_Management.py", label="👨💼 User Management", icon="👨💼")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # Fetch data for quick overview
    sheets = get_sheets_handler()
    members = sheets.get_all_members()
    stickers = sheets.get_all_stickers()
    
    st.markdown("### 📊 Quick Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("👥 Total Members", len(members))
    with c2:
        st.metric("🎫 Total Stickers", len(stickers))
    with c3:
        active = len([s for s in stickers if s.get("Status") == "Active"])
        st.metric("✅ Active Stickers", active)
    with c4:
        blocked = len([m for m in members if m.get("Status") == "Blocked"])
        st.metric("🚫 Blocked Members", blocked)
    
    st.markdown("---")
    
    st.markdown(f"""
        <div style='
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        '>
            <h3 style='color: {config.COLOR_PRIMARY};'>🚀 Quick Actions</h3>
            <ul style='line-height: 2; color: #37474F;'>
                <li><b>📊 Dashboard</b> - View building-wise vehicle summary & stats</li>
                <li><b> Manage Members</b> - Add members, block/delete, and manage details</li>
                <li><b>🎫 Generate Stickers</b> - Create parking stickers with QR codes</li>
                <li><b>🔍 Verify Sticker</b> - Staff verification with full member details</li>
                <li><b>🌐 Public Verify</b> - Public QR scan verification page</li>
                <li><b>📈 Reports</b> - View scan logs, download Excel reports, and manage stickers</li>
                <li><b> Sticker Viewer</b> - Search, filter, and download generated stickers</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    render_footer()
