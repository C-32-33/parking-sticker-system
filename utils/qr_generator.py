import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
import streamlit as st
import config
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class QRGenerator:
    @staticmethod
    def generate_qr_pil(sticker_id: str, add_logo: bool = True):
        try:
            verify_url = f"{config.BASE_VERIFY_URL}/Public_Verify?sticker_id={sticker_id}"
            qr = qrcode.QRCode(
                version=4,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=config.QR_SIZE,
                border=config.QR_BORDER,
            )
            qr.add_data(verify_url)
            qr.make(fit=True)
            
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(
                    front_color=(0, 0, 0),  # Black for better scanning
                    back_color=(255, 255, 255)
                )
            ).convert("RGB")
            
            if add_logo:
                img = QRGenerator._add_center_logo(img)
            return img
        except Exception as e:
            st.error(f"QR Error: {e}")
            qr = qrcode.QRCode(box_size=10, border=2)
            qr.add_data(f"{config.BASE_VERIFY_URL}?sticker_id={sticker_id}")
            qr.make(fit=True)
            return qr.make_image(fill_color="black", back_color="white")

    @staticmethod
    def _draw_car_icon(draw, x, y, size, color):
        draw.rectangle([x-size//2, y-size//4, x+size//2, y+size//4], fill=color)
        draw.polygon([
            (x-size//3, y-size//4), (x-size//4, y-size//2), 
            (x+size//4, y-size//2), (x+size//3, y-size//4)
        ], fill=color)
        wheel_size = size // 6
        draw.ellipse([x-size//2+size//8, y+size//4-wheel_size//2, x-size//2+size//3, y+size//4+wheel_size//2], fill="black")
        draw.ellipse([x+size//2-size//3, y+size//4-wheel_size//2, x+size//2-size//8, y+size//4+wheel_size//2], fill="black")

    @staticmethod
    def _add_center_logo(qr_img):
        qr_w, qr_h = qr_img.size
        logo_size = qr_w // 4
        logo = Image.new("RGB", (logo_size, logo_size), "white")
        draw = ImageDraw.Draw(logo)
        draw.ellipse([(2, 2), (logo_size-2, logo_size-2)], fill=(204, 0, 0), outline="white", width=3)
        QRGenerator._draw_car_icon(draw, logo_size//2, logo_size//2, logo_size//2, "white")
        pos = ((qr_w - logo_size)//2, (qr_h - logo_size)//2)
        qr_img.paste(logo, pos)
        return qr_img

    @staticmethod
    def generate_qr_bytes(sticker_id: str) -> BytesIO:
        img = QRGenerator.generate_qr_pil(sticker_id)
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG", quality=100)
        img_bytes.seek(0)
        return img_bytes