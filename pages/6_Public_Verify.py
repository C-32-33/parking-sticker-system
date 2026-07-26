import streamlit as st
from utils.sheets import get_sheets_handler
from utils.theme import apply_theme, render_banner, render_footer
from datetime import datetime
import config

st.set_page_config(
    page_title="Public Parking Verification",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

apply_theme()

# Try to import camera input for QR scanning
try:
    from streamlit_camera_input_live import camera_input_live
    HAS_CAMERA = True
except ImportError:
    HAS_CAMERA = False

# Get sticker_id from URL
query_params = st.query_params
sticker_id = query_params.get("sticker_id", None)

# If no sticker_id in URL, show scanner
if not sticker_id:
    render_banner("🔍 Public Parking Verification")
    
    st.markdown("""
        <div style='
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            text-align: center;
        '>
            <h2 style='color: #1976D2; margin-top: 0;'>Scan Parking Sticker</h2>
            <p style='color: #666; margin-bottom: 30px;'>
                Point your camera at the parking sticker QR code to verify validity
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Option 1: Camera Scanner (if available)
    if HAS_CAMERA:
        st.markdown("### 📷 Camera Scanner")
        st.info("📱 Allow camera access when prompted")
        
        img_file_buffer = camera_input_live()
        
        if img_file_buffer is not None:
            st.success("✅ QR code detected! Processing...")
            # Note: In a real implementation, you'd decode the QR here
            # For now, we'll show a manual input fallback
            st.warning("⚠️ QR decoding requires additional setup. Please use manual entry below.")
    
    # Option 2: Manual Entry (fallback)
    st.markdown("### 🔢 Manual Entry")
    st.write("Or enter the Sticker ID manually:")
    
    manual_id = st.text_input(
        "Sticker ID",
        placeholder="Enter sticker ID (e.g., ABC123)",
        label_visibility="collapsed"
    )
    
    if manual_id:
        st.query_params["sticker_id"] = manual_id
        st.rerun()
    
    st.markdown("---")
    st.info(" **Tip:** You can also scan the QR code with any QR scanner app on your phone, then paste the Sticker ID above.")
    
    render_footer()
    st.stop()

# If we have sticker_id, verify it
sheets = get_sheets_handler()
stickers = sheets.get_all_stickers()

# Find the sticker
sticker = None
for s in stickers:
    if s.get("StickerID") == sticker_id:
        sticker = s
        break

if not sticker:
    # Sticker not found
    st.markdown(f"""
        <div style='
            background: #ffebee;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
            margin: 20px 0;
        '>
            <div style='font-size: 80px; margin-bottom: 20px;'>❌</div>
            <h1 style='color: #d32f2f; margin: 0;'>Invalid Sticker</h1>
            <p style='color: #666; font-size: 18px; margin: 10px 0;'>
                This parking sticker is not recognized in our system
            </p>
            <p style='color: #999; font-size: 14px;'>
                Sticker ID: {sticker_id}
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    # Sticker found - check validity
    status = sticker.get("Status", "")
    expiry_date = sticker.get("ExpiryDate", "")
    
    # Check if expired
    is_expired = False
    if expiry_date:
        try:
            # Handle both formats
            if "T" in expiry_date:
                expiry = datetime.fromisoformat(expiry_date.replace("Z", "+00:00"))
            else:
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
            
            is_expired = expiry < datetime.now(expiry.tzinfo if expiry.tzinfo else None)
        except:
            pass
    
    is_valid = (status == "Active" and not is_expired)
    
    if is_valid:
        # VALID PARKING
        st.markdown(f"""
            <div style='
                background: #e8f5e9;
                padding: 40px;
                border-radius: 12px;
                text-align: center;
                margin: 20px 0;
                border: 4px solid #4caf50;
            '>
                <div style='font-size: 100px; margin-bottom: 20px;'>✅</div>
                <h1 style='color: #2e7d32; margin: 0; font-size: 36px;'>Valid Parking</h1>
                <p style='color: #666; font-size: 18px; margin: 10px 0;'>
                    This parking sticker is active and valid
                </p>
                <div style='
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 20px;
                    display: inline-block;
                '>
                    <p style='margin: 5px 0; color: #333;'><b>Sticker ID:</b> {sticker_id}</p>
                    <p style='margin: 5px 0; color: #333;'><b>Status:</b> <span style='color: #4caf50; font-weight: bold;'>Active</span></p>
                    {f"<p style='margin: 5px 0; color: #333;'><b>Valid Until:</b> {expiry.strftime('%d %b %Y') if expiry else 'N/A'}</p>" if expiry else ""}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # INVALID PARKING
        reason = ""
        if status == "Blocked":
            reason = "This sticker has been blocked by society management"
        elif is_expired:
            reason = f"This sticker expired on {expiry.strftime('%d %b %Y') if expiry else 'N/A'}"
        else:
            reason = f"Status: {status}"
        
        st.markdown(f"""
            <div style='
                background: #ffebee;
                padding: 40px;
                border-radius: 12px;
                text-align: center;
                margin: 20px 0;
                border: 4px solid #f44336;
            '>
                <div style='font-size: 100px; margin-bottom: 20px;'>❌</div>
                <h1 style='color: #c62828; margin: 0; font-size: 36px;'>Invalid Parking</h1>
                <p style='color: #666; font-size: 18px; margin: 10px 0;'>
                    {reason}
                </p>
                <div style='
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 20px;
                    display: inline-block;
                '>
                    <p style='margin: 5px 0; color: #333;'><b>Sticker ID:</b> {sticker_id}</p>
                    <p style='margin: 5px 0; color: #333;'><b>Status:</b> <span style='color: #f44336; font-weight: bold;'>{status}</span></p>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Back button
if st.button("🔙 Scan Another Sticker", use_container_width=True):
    st.query_params.clear()
    st.rerun()

render_footer()
