# ============================================
# PARKING STICKER MANAGEMENT SYSTEM - CONFIG
# ============================================

# ============================================
# APP METADATA & BRANDING
# ============================================
APP_TITLE = "Parking Sticker Management System"
APP_ICON = "🅿️"
SOCIETY_NAME = "C-32/33 Poonam Nagar CHS"
SOCIETY_ADDRESS = "Buildings C-32 & C-33, Poonam Nagar CHS"
SOCIETY_BUILDINGS = "Buildings C-32 & C-33"
CONTACT_NUMBER = "+91-12345678"
COPYRIGHT_TEXT = "© 2026 C-32/33 Poonam Nagar CHS. All rights reserved."

# ============================================
# COLOR SCHEME (All Required Variables)
# ============================================
COLOR_PRIMARY = "#1976D2"
COLOR_ACCENT = "#0D47A1"
COLOR_SECONDARY = "#0D47A1"
COLOR_SIDEBAR = "#1565C0"
COLOR_FOOTER = "#0D47A1"
COLOR_PRIMARY_LIGHT = "#42A5F5"
COLOR_SUCCESS = "#4CAF50"
COLOR_ERROR = "#F44336"
COLOR_WARNING = "#FF9800"
COLOR_INFO = "#2196F3"
COLOR_BACKGROUND = "#F5F5F5"
COLOR_TEXT = "#333333"
COLOR_SIDEBAR_BG = "#1565C0"

# ============================================
# APP SETTINGS & LAYOUT
# ============================================
BUILDINGS = ["C-32", "C-33"]
ALL_FLAT_NUMBERS = [str(i).zfill(3) for i in range(1, 201)]
VEHICLE_TYPES = ["Car", "Bike", "Scooter", "Auto", "Truck"]
STICKER_COLORS = ["blue", "red", "green", "gold", "purple", "orange"]
MEMBER_STATUS_OPTIONS = ["Active", "Blocked"]
STICKER_STATUS_OPTIONS = ["Active", "Blocked", "Expired"]
VALIDITY_PERIODS_MONTHS = [1, 3, 6, 12, 24, 36]

# ============================================
# STICKER ID GENERATION
# ============================================
STICKER_ID_CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
STICKER_ID_LENGTH = 8

# ============================================
# LOGIN CREDENTIALS (Demo / Default Admin)
# ============================================
ADMIN_EMAIL = "admin@society.com"
ADMIN_PASSWORD = "admin123"

# ============================================
# APP URL (Your Live Streamlit Cloud URL)
# ============================================
APP_URL = "https://parking-sticker-system-ou7pkmfjuvehgx8kmsg9mg.streamlit.app"

# ============================================
# GOOGLE APPS SCRIPT CONFIGURATION
# ============================================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxBCLs4Coc-Ow5zV7Vzpev-qJHwIJyP3x6Yom3LbeawZGhK-vOcYamtG3ffa_DVKuDKkA/exec"

# ============================================
# QR CODE SETTINGS
# ============================================
QR_CODE_SIZE = 300
QR_CODE_BORDER = 2
BASE_VERIFY_URL = APP_URL  # Uses APP_URL for QR code verification

# ============================================
# CACHE SETTINGS
# ============================================
CACHE_TTL = 3600  # Cache time-to-live in seconds (1 hour)
