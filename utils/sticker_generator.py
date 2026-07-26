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
    # Fallback to default if specific fonts aren't found on the server
    try:
        return ImageFont.load_default(size=size)
    except:
        return ImageFont.load_default()

class StickerGenerator:
    @staticmethod
    def generate_random_sticker_id() -> str:
        charset = getattr(config, 'STICKER_ID_CHARSET', 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        length = getattr(config, 'STICKER_ID_LENGTH', 8)
        return ''.join(random.choices(charset, k=length))

    @staticmethod
    def generate_sticker(sticker_id: str, member_name: str, vehicle_type: str, flat_no: str, color: str = "red") -> BytesIO:
        try:
            # 1. Generate QR Code with live URL
            app_url = st.secrets.get("APP_URL", getattr(config, 'APP_URL', "https://parking-sticker-system.streamlit.app"))
            verify_url = f"{app_url}/Public_Verify?sticker_id={sticker_id}"
            
            # High error correction so the logo doesn't break the scan
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
            qr.add_data(verify_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            
            # 2. Create high-res canvas
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
            
            # 3. Draw Outer Circle (Radius 1100)
            draw.ellipse([(100, 100), (2300, 2300)], fill=main_color)
            # White inner ring
            draw.ellipse([(150, 150), (2250, 2250)], outline=white, width=20)
            
            # 4. Paste QR Code (Size 1000, shifted up to leave room at bottom)
            qr_size = 1000
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            qr_x = center_x - qr_size // 2
            qr_y = 450  # Shifted up
            img.paste(qr_img, (qr_x, qr_y))
            
            # 5. Superimpose Logo from 'logos' folder
            v_type = vehicle_type.lower() if vehicle_type else "car"
            logo_path = "logos/bike.png" if ("bike" in v_type or "scooter" in v_type) else "logos/car.png"
            
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                logo_size = 250  # Small size relative to QR
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Calculate exact center of the QR code
                logo_x = center_x - logo_size // 2
                logo_y = qr_y + (qr_size // 2) - (logo_size // 2)
                
                # Paste with transparency mask
                img.paste(logo, (logo_x, logo_y), logo)
            
            # 6. Draw "PARKING PERMIT" Text
            label_font = get_font(100)
            text_y = qr_y + qr_size + 100
            draw.text((center_x, text_y), "PARKING PERMIT", fill=white, font=label_font, anchor="mm")
            
            # 7. Draw Bold Sticker ID in White Pill
            id_font = get_font(140)
            id_bbox = id_font.getbbox(sticker_id)
            id_text_w = id_bbox[2] - id_bbox[0]
            id_text_h = id_bbox[3] - id_bbox[1]
            
            pill_padding_x = 80
            pill_padding_y = 30
            pill_w = id_text_w + pill_padding_x * 2
            pill_h = id_text_h + pill_padding_y * 2
            pill_x = center_x - pill_w // 2
            pill_y = text_y + 120  # Positioned below text, well inside the circle
            
            # White pill background
            draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)], radius=pill_h // 2, fill=white)
            # Bold colored ID text
            draw.text((center_x, pill_y + pill_h // 2), sticker_id, fill=main_color, font=id_font, anchor="mm")
            
            # 8. Finalize
            final_img = img.resize(final_size, Image.Resampling.LANCZOS)
            img_bytes = BytesIO()
            final_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return img_bytes
            
        except Exception as e:
            st.error(f"Sticker Error: {e}")
            return None
