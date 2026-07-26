import os

# Data storage
SHEET_ID = os.getenv("SHEET_ID", "19OHfLUOiUuN748ZUmR14dmTMvea8UzfxwzxKXdZmHhA")
SHEET_NAME = "ParkingStickers"

# Sticker config - Updated to square for high-quality circular design
STICKER_SIZE = (1200, 1200)
STICKER_ID_LENGTH = 8
STICKER_ID_CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# QR config
QR_SIZE = 12
QR_BORDER = 2

# Colors
COLOR_VALID = "#00C853"
COLOR_INVALID = "#D50000"
COLOR_PRIMARY = "#1565C0"
COLOR_SECONDARY = "#0D47A1"
COLOR_ACCENT = "#FFC107"
COLOR_DARK = "#263238"

# URLs
BASE_VERIFY_URL = "http://localhost:8501"

# Society Info
SOCIETY_NAME = "C-32/33 Poonam Nagar CHS"
SOCIETY_CONTACT = "+91-12345678"
SOCIETY_ADDRESS = "Buildings C-32 & C-33"
LEGAL_WARNING = "This is an official page for C-32/33 Poonam Nagar CHS. Unauthorized use, duplication or transfer is strictly prohibited and punishable under society bylaws."

# Building structure
BUILDINGS = ["C-32", "C-33"]
FLOORS = ["G", "1", "2", "3", "4"]
FLATS_PER_FLOOR = 4

def generate_flat_numbers():
    flats = []
    floor_prefixes = {"G": "0", "1": "1", "2": "2", "3": "3", "4": "4"}
    for floor, prefix in floor_prefixes.items():
        for f in range(1, FLATS_PER_FLOOR + 1):
            flats.append(f"{prefix}{f:02d}")
    return flats

ALL_FLAT_NUMBERS = generate_flat_numbers()