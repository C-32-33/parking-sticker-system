import streamlit as st
from datetime import datetime

# ============================================
# APP METADATA & BRANDING
# ============================================
APP_TITLE = "Parking Sticker Management System"
APP_ICON = "🅿️"
SOCIETY_NAME = "C-32/33 Poonam Nagar CHS"
SOCIETY_BUILDINGS = "Buildings C-32 & C-33"
CONTACT_NUMBER = "+91-12345678"
COPYRIGHT_TEXT = f"© {datetime.now().year} {SOCIETY_NAME}. All rights reserved."

# ============================================
# COLOR SCHEME (Fixes the AttributeError)
# ============================================
COLOR_PRIMARY = "#1976D2"       # Deep blue - main brand color
COLOR_ACCENT = "#0D47A1"        # Darker blue - accents and hover states
COLOR_SIDEBAR = "#1565C0"       # Sidebar background color (REQUIRED TO FIX ERROR)
COLOR_FOOTER = "#0D47A1"        # Footer background color
COLOR_PRIMARY_LIGHT = "#42A5F5" # Light blue - backgrounds and highlights
COLOR_SUCCESS = "#4CAF50"       # Green - success messages
COLOR_ERROR = "#F44336"         # Red - error messages
COLOR_WARNING = "#FF9800"       # Orange - warning messages
COLOR_INFO = "#2196F3"          # Blue - info messages
COLOR_TEXT = "#333333"          # Dark gray for text
COLOR_BACKGROUND = "#F5F5F5"    # Light gray for main background

# ============================================
# ADDITIONAL COLOR VARIABLES
# ============================================
COLOR_SECONDARY = "#0D47A1"  # Same as COLOR_ACCENT
COLOR_BACKGROUND = "#F5F5F5"
COLOR_TEXT = "#333333"

# ============================================
# BASE URL FOR QR CODES
# ============================================
# This will be updated dynamically, but set a default
BASE_VERIFY_URL = "https://parking-sticker-system-ou7pk mfjuvehgx8kmsg9mg.streamlit.app"

# ============================================
# QR CODE SETTINGS
# ============================================
QR_CODE_SIZE = 300
QR_CODE_BORDER = 2

# ============================================
# APP SETTINGS & LAYOUT
# ============================================
BUILDINGS = ["C-32", "C-33"]
# Generates flat numbers from 001 to 200
ALL_FLAT_NUMBERS = [str(i).zfill(3) for i in range(1, 201)] 
VEHICLE_TYPES = ["Car", "Bike", "Scooter", "Auto", "Truck"]
STICKER_COLORS = ["blue", "red", "green", "gold", "purple", "orange"]
MEMBER_STATUS_OPTIONS = ["Active", "Blocked"]
STICKER_STATUS_OPTIONS = ["Active", "Blocked", "Expired"]
VALIDITY_PERIODS_MONTHS = [1, 3, 6, 12, 24, 36]

# ============================================
# LOGIN CREDENTIALS (Demo / Default)
# ============================================
ADMIN_EMAIL = "admin@society.com"
ADMIN_PASSWORD = "admin123"

# ============================================
# GOOGLE APPS SCRIPT CONFIGURATION
# ============================================
# Note: It is highly recommended to put this in Streamlit Secrets,
# but keeping it here as a fallback.
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxBCLs4Coc-Ow5zV7Vzpev-qJHwIJyP3x6Yom3LbeawZGhK-vOcYamtG3ffa_DVKuDKkA/exec"
