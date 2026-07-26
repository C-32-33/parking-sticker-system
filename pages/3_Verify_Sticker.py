import streamlit as st
from utils.sheets import get_sheets_handler
from utils.sticker_generator import StickerGenerator
from utils.theme import apply_theme, render_footer
import config
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO
import base64

st.set_page_config(page_title="Verify Sticker", page_icon="🔍", layout="wide")
apply_theme()

sheets = get_sheets_handler()

# Get sticker ID from URL or manual entry
query_params = st.query_params
sticker_id_from_url = query_params.get("sticker_id", "")

# Check authentication
is_authenticated = st.session_state.get("authenticated", False)
user_email = st.session_state.get("user_email", "")
user_role = st.session_state.get("user_role", "")

# --- Drawing Functions for Overlays ---
def draw_checkmark(draw, cx, cy, size, color, thickness):
    pts = [(cx - size//2, cy), (cx - size//6, cy + size//3), (cx + size//2, cy - size//3)]
    draw.line([pts[0], pts[1]], fill=color, width=thickness)
    draw.line([pts[1], pts[2]], fill=color, width=thickness)

def draw_x_mark(draw, cx, cy, size, color, thickness):
    h = size // 2
    draw.line([(cx - h, cy - h), (cx + h, cy + h)], fill=color, width=thickness)
    draw.line([(cx + h, cy - h), (cx - h, cy + h)], fill=color, width=thickness)

def draw_prohibition_sign(draw, cx, cy, size, color, thickness):
    r = size // 2
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=color, width=thickness)
    draw.line([(cx - r + thickness//2, cy - r + thickness//2), (cx + r - thickness//2, cy + r - thickness//2)], fill=color, width=thickness)

def create_sticker_with_overlay(sticker_id, status_type):
    """Generate sticker and apply the correct overlay"""
    sticker_bytes = StickerGenerator.generate_sticker(sticker_id, "", "", "", "red")
    if not sticker_bytes: return None
    
    sticker_img = Image.open(sticker_bytes).convert('RGBA')
    overlay = Image.new('RGBA', sticker_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Center on QR code (shifted up by 60px as per design)
    cx = sticker_img.size[0] // 2
    cy = (sticker_img.size[1] // 2) - 60
    circle_size = 560

    if status_type == "VALID":
        draw.ellipse([(cx - circle_size//2, cy - circle_size//2), (cx + circle_size//2, cy + circle_size//2)], fill=(0, 200, 83, 220), outline=(0, 150, 60, 255), width=25)
        draw_checkmark(draw, cx, cy, 380, (255, 255, 255, 255), 50)
    elif status_type == "BLOCKED":
        draw.ellipse([(cx - circle_size//2, cy - circle_size//2), (cx + circle_size//2, cy + circle_size//2)], fill=(213, 0, 0, 220), outline=(180, 0, 0, 255), width=25)
        draw_prohibition_sign(draw, cx, cy, 450, (255, 255, 255, 255), 60)
    else: # INVALID
        draw.ellipse([(cx - circle_size//2, cy - circle_size//2), (cx + circle_size//2, cy + circle_size//2)], fill=(213, 0, 0, 220), outline=(180, 0, 0, 255), width=25)
        draw_x_mark(draw, cx, cy, 380, (255, 255, 255, 255), 50)
    
    result = Image.alpha_composite(sticker_img, overlay)
    img_bytes = BytesIO()
    result.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

def get_base64_image(img_bytes):
    return base64.b64encode(img_bytes.read()).decode('utf-8')

# --- UI Header ---
st.markdown(f"""<div style='background: linear-gradient(135deg, {config.COLOR_PRIMARY} 0%, {config.COLOR_SECONDARY} 100%); padding: 20px 30px; border-radius: 12px; margin-bottom: 25px; text-align: center;'>
    <h1 style='color: white; margin: 0;'>🔍 Sticker Verification</h1>
    <p style='color: #E3F2FD; margin: 5px 0 0 0;'>{config.SOCIETY_NAME} - {config.SOCIETY_BUILDINGS}</p>
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 📱 Scan QR Code")
    st.info("Scan the QR code on the sticker using your phone camera or QR scanner app.")
with col2:
    st.markdown("### 📝 Manual Entry")
    manual_sticker_id = st.text_input("Enter Sticker ID", value=sticker_id_from_url, placeholder="e.g. W86UEXRB")
    verify_clicked = st.button("🔍 Verify", use_container_width=True, type="primary")
st.markdown("---")

# --- Verification Logic ---
sticker_id = sticker_id_from_url or manual_sticker_id

if sticker_id and (verify_clicked or sticker_id_from_url):
    sticker = sheets.get_sticker_by_id(sticker_id)
    
    # Determine status (Check Member first, then Sticker)
    if not sticker:
        status_type = "INVALID"
        status_message = "Sticker not found in database"
    else:
        member = sheets.get_member_by_id(sticker.get("MemberID"))
        
        if member and member.get("Status") == "Blocked":
            status_type = "BLOCKED"
            status_message = "Member has been blocked by administration"
        elif sticker.get("Status") == "Blocked":
            status_type = "BLOCKED"
            status_message = "Sticker has been blocked"
        elif sticker.get("Status") != "Active":
            status_type = "INVALID"
            status_message = f"Sticker status is: {sticker.get('Status')}"
        else:
            try:
                expiry = datetime.strptime(sticker.get("ExpiryDate", ""), "%Y-%m-%d")
                if expiry >= datetime.now():
                    status_type = "VALID"
                    status_message = "Sticker is active and valid"
                else:
                    status_type = "INVALID"
                    status_message = f"Sticker expired on {sticker.get('ExpiryDate')}"
            except:
                status_type = "VALID"
                status_message = "Sticker is active"

    # Generate and display the sticker with overlay
    sticker_with_overlay = create_sticker_with_overlay(sticker_id, status_type)
    if sticker_with_overlay:
        base64_img = get_base64_image(sticker_with_overlay)
        status_text = "✅ Valid Parking" if status_type == "VALID" else ("🚫 Blocked Parking" if status_type == "BLOCKED" else " Invalid Parking")
        status_color = "#00C853" if status_type == "VALID" else "#D50000"
        
        st.markdown(f"""<div style='text-align: center; margin: 30px 0;'>
            <img src="data:image/png;base64,{base64_img}" style="max-width: 600px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);" />
            <h1 style='color: {status_color}; margin-top: 20px; font-size: 48px; font-weight: bold;'>{status_text}</h1>
        </div>""", unsafe_allow_html=True)
        
        # Show details ONLY if authenticated (staff view)
        if is_authenticated and sticker:
            member = sheets.get_member_by_id(sticker.get("MemberID"))
            st.markdown("### 📋 Full Details (Staff View)")
            dcol1, dcol2 = st.columns(2)
            
            with dcol1:
                member_status_color = "red" if member and member.get("Status") == "Blocked" else "green"
                st.markdown(f"""<div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid {config.COLOR_PRIMARY}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                    <h4 style='color: {config.COLOR_PRIMARY}; margin-top: 0;'>👤 Member Details</h4>
                    <p><b>Name:</b> {member.get('Name') if member else 'N/A'}</p>
                    <p><b>Building:</b> {member.get('Building') if member else 'N/A'}</p>
                    <p><b>Flat No:</b> {member.get('Flat No') if member else 'N/A'}</p>
                    <p><b>Mobile:</b> {member.get('Mobile') if member else 'N/A'}</p>
                    <p><b>Member Status:</b> <span style='color: {member_status_color}; font-weight: bold;'>{member.get('Status') if member else 'N/A'}</span></p>
                </div>""", unsafe_allow_html=True)
                
            with dcol2:
                sticker_status_color = "red" if sticker.get("Status") == "Blocked" else "green"
                st.markdown(f"""<div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid {config.COLOR_ACCENT}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                    <h4 style='color: {config.COLOR_PRIMARY}; margin-top: 0;'>🎫 Sticker Details</h4>
                    <p><b>Vehicle No:</b> {sticker.get('VehicleNo')}</p>
                    <p><b>Issued:</b> {sticker.get('IssuedDate')}</p>
                    <p><b>Expires:</b> {sticker.get('ExpiryDate')}</p>
                    <p><b>Sticker Status:</b> <span style='color: {sticker_status_color}; font-weight: bold;'>{sticker.get('Status')}</span></p>
                </div>""", unsafe_allow_html=True)
                
            # Log the scan
            sheets.log_scan({"Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "StickerID": sticker_id, "Result": status_type, "UserEmail": user_email, "UserRole": user_role, "Notes": status_message})
        elif not is_authenticated:
            st.info("🔒 Login as staff to view full member details.")
    else:
        st.error("Failed to generate sticker image")
else:
    st.markdown("<div style='text-align: center; padding: 40px; color: #90A4AE;'><div style='font-size: 60px;'>👆</div><p style='font-size: 18px;'>Scan a QR code or enter a Sticker ID to verify</p></div>", unsafe_allow_html=True)

render_footer()
