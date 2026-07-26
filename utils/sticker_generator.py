from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import config
from io import BytesIO
import os
import random
import qrcode

def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

def draw_car_icon(draw, cx, cy, size, color):
    """Draws a clean car silhouette inside a red circle"""
    # Red background circle
    draw.ellipse([(cx - size//2, cy - size//2), (cx + size//2, cy + size//2)], fill=color)
    
    # White Car Body (Side view)
    s = size // 4 # Scale factor
    # Main body
    draw.polygon([
        (cx - 3*s, cy + s), (cx - 2*s, cy - s), (cx + 1*s, cy - s), 
        (cx + 3*s, cy + s), (cx + 3.5*s, cy + 2*s), (cx - 3.5*s, cy + 2*s)
    ], fill="white")
    # Cabin/Windows
    draw.polygon([
        (cx - 2*s, cy - s), (cx - 1*s, cy - 2.5*s), (cx + 0.5*s, cy - 2.5*s), (cx + 1.5*s, cy - s)
    ], fill="white")
    # Wheels
    draw.ellipse([(cx - 2.5*s, cy + 1.5*s), (cx - 0.5*s, cy + 3.5*s)], fill=color) # Tire
    draw.ellipse([(cx - 2*s, cy + 2*s), (cx - 1*s, cy + 3*s)], fill="white") # Rim
    draw.ellipse([(cx + 0.5*s, cy + 1.5*s), (cx + 2.5*s, cy + 3.5*s)], fill=color) # Tire
    draw.ellipse([(cx + 1*s, cy + 2*s), (cx + 2*s, cy + 3*s)], fill="white") # Rim

def draw_bike_icon(draw, cx, cy, size, color):
    """Draws a clean bike/motorcycle silhouette inside a red circle"""
    # Red background circle
    draw.ellipse([(cx - size//2, cy - size//2), (cx + size//2, cy + size//2)], fill=color)
    
    s = size // 4
    # Wheels
    draw.ellipse([(cx - 3*s, cy + s), (cx - 1*s, cy + 3*s)], fill=color)
    draw.ellipse([(cx - 2.5*s, cy + 1.5*s), (cx - 1.5*s, cy + 2.5*s)], fill="white")
    draw.ellipse([(cx + 1*s, cy + s), (cx + 3*s, cy + 3*s)], fill=color)
    draw.ellipse([(cx + 1.5*s, cy + 1.5*s), (cx + 2.5*s, cy + 2.5*s)], fill="white")
    
    # Frame and Handlebars
    draw.line([(cx - 2*s, cy + 2*s), (cx, cy - 1*s)], fill="white", width=s//2)
    draw.line([(cx, cy - 1*s), (cx + 2*s, cy + 2*s)], fill="white", width=s//2)
    draw.line([(cx, cy - 1*s), (cx + 1.5*s, cy - 2*s)], fill="white", width=s//2) # Handlebars
    draw.line([(cx - 1*s, cy + 1*s), (cx + 1*s, cy + 1*s)], fill="white", width=s) # Seat

class StickerGenerator:
    @staticmethod
    def generate_random_sticker_id() -> str:
        charset = getattr(config, 'STICKER_ID_CHARSET', 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        length = getattr(config, 'STICKER_ID_LENGTH', 8)
        return ''.join(random.choices(charset, k=length))

    @staticmethod
    def generate_sticker(sticker_id: str, member_name: str, vehicle_type: str, flat_no: str, color: str = "red") -> BytesIO:
        try:
            # 1. DETERMINE LIVE URL
            app_url = st.secrets.get("APP_URL", getattr(config, 'APP_URL', "https://parking-sticker-system.streamlit.app"))
            verify_url = f"{app_url}/Public_Verify?sticker_id={sticker_id}"
            
            # 2. GENERATE HIGH-QUALITY QR CODE
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
            qr.add_data(verify_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

            # 3. DRAW HIGH-RES STICKER (Matches Image 2 exactly)
            draw_size = (2400, 2400) 
            final_size = (1200, 1200)
            img = Image.new('RGB', draw_size, 'white')
            draw = ImageDraw.Draw(img)

            center_x = draw_size[0] // 2
            white = (255, 255, 255)

            color_map = {
                "blue": (0, 102, 204), "red": (204, 0, 0), "green": (40, 167, 69),
                "gold": (255, 193, 7), "purple": (156, 39, 176),
            }
            main_color = color_map.get(color, (204, 0, 0))

            # Outer Red Rings
            draw.ellipse([(30, 30), (draw_size[0]-30, draw_size[1]-30)], fill=white)
            draw.ellipse([(70, 70), (draw_size[0]-70, draw_size[1]-70)], fill=main_color)
            draw.ellipse([(110, 110), (draw_size[0]-110, draw_size[1]-110)], outline=white, width=16)

            # QR Code Placement (Slightly higher to make room for large text below)
            qr_size = 1300
            qr_img_resized = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            qr_x = center_x - qr_size // 2
            qr_y = 450 # Top position of QR
            img.paste(qr_img_resized, (qr_x, qr_y))

            # Center Logo (Car or Bike)
            logo_size = 350
            logo_cx = center_x
            logo_cy = qr_y + (qr_size // 2) # Center of QR code
            
            # Determine icon type
            v_type = vehicle_type.lower() if vehicle_type else "car"
            if "bike" in v_type or "scooter" in v_type or "two" in v_type:
                draw_bike_icon(draw, logo_cx, logo_cy, logo_size, main_color)
            else:
                draw_car_icon(draw, logo_cx, logo_cy, logo_size, main_color)

            # Large "PARKING PERMIT" Text
            label_font = get_font(110)
            text_y = qr_y + qr_size + 80
            draw.text((center_x, text_y), "PARKING PERMIT", fill=white, font=label_font, anchor="mm")

            # Large Sticker ID in Pill Shape
            id_font = get_font(160)
            id_bbox = id_font.getbbox(sticker_id)
            id_text_w = id_bbox[2] - id_bbox[0]
            id_text_h = id_bbox[3] - id_bbox[1]
            
            pill_padding_x = 100
            pill_padding_y = 50
            pill_w = id_text_w + pill_padding_x * 2
            pill_h = id_text_h + pill_padding_y * 2
            pill_x = center_x - pill_w // 2
            pill_y = text_y + 120

            # White Pill Background
            draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)], radius=pill_h // 2, fill=white)
            # Red ID Text
            draw.text((center_x, pill_y + pill_h // 2), sticker_id, fill=main_color, font=id_font, anchor="mm")

            # Finalize and return
            final_img = img.resize(final_size, Image.Resampling.LANCZOS)
            img_bytes = BytesIO()
            final_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return img_bytes
            
        except Exception as e:
            st.error(f"Sticker Generation Error: {e}")
            return None
