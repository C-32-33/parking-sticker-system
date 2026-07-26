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

            # 3. DRAW HIGH-RES STICKER (Matches your desired Image 2)
            draw_size = (2400, 2400) # High res for scaling
            final_size = (1200, 1200)
            img = Image.new('RGB', draw_size, 'white')
            draw = ImageDraw.Draw(img)

            center_x = draw_size[0] // 2
            center_y = draw_size[1] // 2
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

            # Paste QR Code
            qr_size = 1240
            qr_img_resized = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            # Add white padding around QR
            qr_padding = 70
            qr_bg_size = qr_size + qr_padding * 2
            qr_bg = Image.new('RGB', (qr_bg_size, qr_bg_size), white)
            qr_bg.paste(qr_img_resized, (qr_padding, qr_padding))
            
            qr_x = center_x - qr_bg_size // 2
            qr_y = center_y - qr_bg_size // 2 - 120 
            img.paste(qr_bg, (qr_x, qr_y))

            # Draw Car Logo in Center of QR Code
            logo_size = 180
            logo_x = center_x - logo_size // 2
            logo_y = center_y - 120 - logo_size // 2
            
            # Red circle for logo
            draw.ellipse([(logo_x, logo_y), (logo_x + logo_size, logo_y + logo_size)], fill=main_color)
            # Simple white car shape
            draw.rectangle([(logo_x + 40, logo_y + 90), (logo_x + 140, logo_y + 120)], fill=white)
            draw.polygon([(logo_x + 50, logo_y + 90), (logo_x + 70, logo_y + 60), (logo_x + 110, logo_y + 60), (logo_x + 130, logo_y + 90)], fill=white)
            draw.ellipse([(logo_x + 50, logo_y + 120), (logo_x + 70, logo_y + 140)], fill=white)
            draw.ellipse([(logo_x + 110, logo_y + 120), (logo_x + 130, logo_y + 140)], fill=white)

            # Large "PARKING PERMIT" Text
            label_font = get_font(70)
            draw.text((center_x, qr_y + qr_bg_size + 40), "PARKING PERMIT", fill=white, font=label_font, anchor="mm")

            # Large Sticker ID in Pill Shape
            id_font = get_font(140)
            id_bbox = id_font.getbbox(sticker_id)
            id_text_w = id_bbox[2] - id_bbox[0]
            id_text_h = id_bbox[3] - id_bbox[1]
            
            pill_padding_x = 80
            pill_padding_y = 40
            pill_w = id_text_w + pill_padding_x * 2
            pill_h = id_text_h + pill_padding_y * 2
            pill_x = center_x - pill_w // 2
            pill_y = qr_y + qr_bg_size + 120

            draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)], radius=pill_h // 2, fill=white)
            draw.text((center_x, pill_y + pill_h // 2), sticker_id, fill=main_color, font=id_font, anchor="mm")

            # Finalize
            final_img = img.resize(final_size, Image.Resampling.LANCZOS)
            img_bytes = BytesIO()
            final_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return img_bytes
            
        except Exception as e:
            st.error(f"Sticker Generation Error: {e}")
            return None
