import streamlit as st
from utils.sheets import get_sheets_handler
from utils.sticker_generator import StickerGenerator
from utils.theme import apply_theme
import config
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO
import base64

st.set_page_config(page_title="Parking Verification", page_icon="🅿️", layout="centered")
apply_theme()

sheets = get_sheets_handler()
query_params = st.query_params
sticker_id = query_params.get("sticker_id", "")

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
    <h1 style='color: white; margin: 0;'>🅿️ Parking Permit Verification</h1>
    <p style='color: #E3F2FD; margin: 5px 0 0 0;'>{config.SOCIETY_NAME}</p>
</div>""", unsafe_allow_html=True)

# --- Verification Logic ---
if sticker_id:
    sticker = sheets.get_sticker_by_id(sticker_id)
    
    if not sticker:
        status_type = "INVALID"
    else:
        member = sheets.get_member_by_id(sticker.get("MemberID"))
        if member and member.get("Status") == "Blocked":
            status_type = "BLOCKED"
        elif sticker.get("Status") == "Blocked":
            status_type = "BLOCKED"
        elif sticker.get("Status") != "Active":
            status_type = "INVALID"
        else:
            try:
                expiry = datetime.strptime(sticker.get("ExpiryDate", ""), "%Y-%m-%d")
                status_type = "VALID" if expiry >= datetime.now() else "INVALID"
            except:
                status_type = "VALID"

    sticker_with_overlay = create_sticker_with_overlay(sticker_id, status_type)
    if sticker_with_overlay:
        base64_img = get_base64_image(sticker_with_overlay)
        status_text = "✅ Valid Parking" if status_type == "VALID" else ("🚫 Blocked Parking" if status_type == "BLOCKED" else "❌ Invalid Parking")
        status_color = "#00C853" if status_type == "VALID" else "#D50000"
        
        st.markdown(f"""<div style='text-align: center; margin: 30px 0;'>
            <img src="data:image/png;base64,{base64_img}" style="max-width: 600px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);" />
            <h1 style='color: {status_color}; margin-top: 20px; font-size: 48px; font-weight: bold;'>{status_text}</h1>
            <p style='color: #666; font-size: 16px;'>Sticker ID: {sticker_id}</p>
        </div>""", unsafe_allow_html=True)
        
        # Log the scan (public)
        sheets.log_scan({"Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "StickerID": sticker_id, "Result": status_type, "UserEmail": "public", "UserRole": "outsider", "Notes": f"Status: {sticker.get('Status') if sticker else 'Not Found'}"})
    else:
        st.error("Failed to generate verification image")
else:
    st.markdown(f"""<div style='text-align: center; padding: 60px 20px;'>
        <div style='font-size: 80px; margin-bottom: 20px;'>📱</div>
        <h2 style='color: {config.COLOR_PRIMARY};'>No Sticker ID Provided</h2>
        <p style='font-size: 18px; color: #666;'>Please scan the QR code on the parking sticker using your phone camera.</p>
        <p style='font-size: 16px; color: #999; margin-top: 30px;'>This is an official verification page for {config.SOCIETY_NAME}</p>
    </div>""", unsafe_allow_html=True)

# --- Footer ---
st.markdown(f"""<div style='text-align: center; padding: 20px; margin-top: 40px; border-top: 1px solid #e0e0e0; color: #999; font-size: 12px;'>
    <p>{config.SOCIETY_NAME} | {config.SOCIETY_ADDRESS}</p>
    <p>{config.LEGAL_WARNING}</p>
</div>""", unsafe_allow_html=True)