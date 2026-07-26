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
        # Fallback to safe defaults if config variables are missing
        charset = getattr(config, 'STICKER_ID_CHARSET', 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        length = getattr(config, 'STICKER_ID_LENGTH', 8)
        return ''.join(random.choices(charset, k=length))

    @staticmethod
    def generate_sticker(sticker_id: str, member_name: str, vehicle_type: str, flat_no: str, color: str = "red") -> BytesIO:
        try:
            # 1. DETERMINE THE LIVE APP URL FOR THE QR CODE
            # Tries Streamlit Secrets first, then config.py, then a safe default
            app_url = st.secrets.get("APP_URL", getattr(config, 'APP_URL', "https://parking-sticker-system.streamlit.app"))
            
            # Construct the exact URL for the Public Verify page
            # Streamlit maps "pages/6_Public_Verify.py" to "/Public_Verify"
            verify_url = f"{app_url}/Public_Verify?sticker_id={sticker_id}"
            
            # 2. GENERATE QR CODE WITH THE LIVE URL
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H, # High error correction for logos/scans
                box_size=10,
                border=2,
            )
            qr.add_data(verify_url)
            qr.make(fit=True)
            
            # Create QR image and convert to RGB for pasting
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

            # 3. DRAW THE STICKER (Your existing high-quality design)
            draw_size = (2400, 2400)
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

            # Outer rings
            draw.ellipse([(30, 30), (draw_size[0]-30, draw_size[1]-30)], fill=white)
            draw.ellipse([(70, 70), (draw_size[0]-70, draw_size[1]-70)], fill=main_color)
            draw.ellipse([(110, 110), (draw_size[0]-110, draw_size[1]-110)], outline=white, width=16)

            # Paste QR Code
            if qr_img:
                qr_size = 1240
                qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
                qr_padding = 70
                qr_bg_size = qr_size + qr_padding * 2
                qr_bg = Image.new('RGB', (qr_bg_size, qr_bg_size), white)
                qr_bg.paste(qr_img, (qr_padding, qr_padding))
                qr_x = center_x - qr_bg_size // 2
                qr_y = center_y - qr_bg_size // 2 - 120  # Shift up
                img.paste(qr_bg, (qr_x, qr_y))

            # Sticker ID & Label
            id_font = get_font(124)
            label_font = get_font(56)
            id_y = center_y + qr_size // 2 + 120
            
            id_bbox = id_font.getbbox(sticker_id)
            id_text_w = id_bbox[2] - id_bbox[0]
            id_text_h = id_bbox[3] - id_bbox[1]
            
            pill_padding_x = 60
            pill_padding_y = 30
            pill_w = id_text_w + pill_padding_x * 2
            pill_h = id_text_h + pill_padding_y * 2
            pill_x = center_x - pill_w // 2
            pill_y = id_y - pill_padding_y

            draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)], radius=pill_h // 2, fill=white)
            draw.text((center_x, pill_y - 50), "PARKING PERMIT", fill=white, font=label_font, anchor="mm")
            draw.text((center_x, id_y + id_text_h // 2), sticker_id, fill=main_color, font=id_font, anchor="mm")

            # Finalize and return
            final_img = img.resize(final_size, Image.Resampling.LANCZOS)
            img_bytes = BytesIO()
            final_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return img_bytes
            
        except Exception as e:
            st.error(f"Sticker Generation Error: {e}")
            return None
