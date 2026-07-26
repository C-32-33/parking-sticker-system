import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# Your Apps Script URL
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxBCLs4Coc-Ow5zV7Vzpev-qJHwIJyP3x6Yom3LbeawZGhK-vOcYamtG3ffa_DVKuDKkA/exec"

class SheetsHandler:
    def __init__(self):
        self.url = APPS_SCRIPT_URL

    def _get_data(self, sheet_name, retries=2):
        """Read data from Google Sheet with retries"""
        for attempt in range(retries):
            try:
                response = requests.get(self.url, params={"sheet": sheet_name}, timeout=30)
                if response.status_code == 200:
                    return response.json()
                return []
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    st.warning(f"⏳ Timeout reading {sheet_name}, retrying... ({attempt + 1}/{retries})")
                    time.sleep(2)
                else:
                    st.error(f"❌ Timeout reading {sheet_name} after {retries} attempts")
                    return []
            except Exception as e:
                st.error(f"Error reading {sheet_name}: {e}")
                return []

    def _post_action(self, payload, retries=3):
        """Write data to Google Sheet with retries and longer timeout"""
        for attempt in range(retries):
            try:
                response = requests.post(self.url, json=payload, timeout=60)  # Increased to 60 seconds
                if response.status_code == 200:
                    return response.json()
                return {"success": False, "error": f"HTTP {response.status_code}"}
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    st.warning(f"⏳ Timeout updating {payload.get('sheet')}, retrying... ({attempt + 1}/{retries})")
                    time.sleep(3)
                else:
                    st.error(f"❌ Timeout updating {payload.get('sheet')} after {retries} attempts")
                    return {"success": False, "error": "Timeout after retries"}
            except Exception as e:
                st.error(f"Error updating {payload.get('sheet')}: {e}")
                return {"success": False, "error": str(e)}

    # ===== CACHED DATA ACCESSORS =====
    def get_all_members(self):
        if "members_cache" not in st.session_state:
            st.session_state.members_cache = None
            st.session_state.members_cache_time = None
        
        if (st.session_state.members_cache is not None and 
            st.session_state.members_cache_time and
            datetime.now() - st.session_state.members_cache_time < timedelta(seconds=120)):
            return st.session_state.members_cache
        
        data = self._get_data("Members")
        st.session_state.members_cache = data
        st.session_state.members_cache_time = datetime.now()
        return data

    def get_all_stickers(self):
        if "stickers_cache" not in st.session_state:
            st.session_state.stickers_cache = None
            st.session_state.stickers_cache_time = None
        
        if (st.session_state.stickers_cache is not None and 
            st.session_state.stickers_cache_time and
            datetime.now() - st.session_state.stickers_cache_time < timedelta(seconds=120)):
            return st.session_state.stickers_cache
        
        data = self._get_data("Stickers")
        st.session_state.stickers_cache = data
        st.session_state.stickers_cache_time = datetime.now()
        return data

    def get_logs(self, limit=100):
        if "logs_cache" not in st.session_state:
            st.session_state.logs_cache = None
            st.session_state.logs_cache_time = None
        
        if (st.session_state.logs_cache is not None and 
            st.session_state.logs_cache_time and
            datetime.now() - st.session_state.logs_cache_time < timedelta(seconds=120)):
            return st.session_state.logs_cache
        
        data = self._get_data("Logs")[-limit:]
        st.session_state.logs_cache = data
        st.session_state.logs_cache_time = datetime.now()
        return data

    def clear_cache(self):
        """Clear all cached data"""
        st.session_state.members_cache = None
        st.session_state.stickers_cache = None
        st.session_state.logs_cache = None

    def get_member_by_id(self, member_id):
        for m in self.get_all_members():
            if str(m.get("ID")) == str(member_id):
                return m
        return None

    def get_sticker_by_id(self, sticker_id):
        for s in self.get_all_stickers():
            if str(s.get("StickerID")) == str(sticker_id):
                return s
        return None

    # ===== WRITE OPERATIONS =====
    def add_member(self, member_data):
        headers = ["Building", "ID", "Name", "Flat No", "Mobile", "Email", 
                   "Vehicle Type", "Vehicle Number", "Status", "DateAdded",
                   "Valid Period", "Valid Till Date"]
        row = [member_data.get(h, "") for h in headers]
        result = self._post_action({"action": "append", "sheet": "Members", "data": row})
        if result.get("success"):
            self.clear_cache()
        return result.get("success", False)

    def update_member_status(self, member_id, status):
        res = self._post_action({
            "action": "update", "sheet": "Members",
            "idColumn": "ID", "idValue": member_id,
            "updates": {"Status": status}
        })
        if res.get("success"):
            stickers = self.get_all_stickers()
            for s in stickers:
                if str(s.get("MemberID")) == str(member_id):
                    self._post_action({
                        "action": "update", "sheet": "Stickers",
                        "idColumn": "StickerID", "idValue": s.get("StickerID"),
                        "updates": {"Status": status}
                    })
            self.clear_cache()
        return res.get("success", False)

    def update_member_vehicle_info(self, member_id, vehicle_number, valid_period, valid_till_date):
        updates = {}
        if vehicle_number:
            updates["Vehicle Number"] = vehicle_number
        if valid_period:
            updates["Valid Period"] = valid_period
        if valid_till_date:
            updates["Valid Till Date"] = valid_till_date
        
        if not updates:
            return False
        
        result = self._post_action({
            "action": "update", "sheet": "Members",
            "idColumn": "ID", "idValue": member_id,
            "updates": updates
        })
        if result.get("success"):
            self.clear_cache()
        return result.get("success", False)

    def delete_member(self, member_id):
        """Delete a member from the database"""
        result = self._post_action({
            "action": "delete", "sheet": "Members",
            "idColumn": "ID", "idValue": member_id
        })
        if result.get("success"):
            self.clear_cache()
        return result.get("success", False)

    def delete_sticker(self, sticker_id):
        """Delete a sticker from the database"""
        result = self._post_action({
            "action": "delete", "sheet": "Stickers",
            "idColumn": "StickerID", "idValue": sticker_id
        })
        if result.get("success"):
            self.clear_cache()
        return result.get("success", False)

    def add_sticker(self, sticker_data):
        headers = ["StickerID", "MemberID", "Building", "FlatNo", "VehicleNo", 
                   "Status", "IssuedDate", "ExpiryDate", "Color", "Remarks"]
        row = [sticker_data.get(h, "") for h in headers]
        result = self._post_action({"action": "append", "sheet": "Stickers", "data": row})
        if result.get("success"):
            self.clear_cache()
        return result.get("success", False)

    def update_sticker_status(self, sticker_id, status):
        result = self._post_action({
            "action": "update", "sheet": "Stickers",
            "idColumn": "StickerID", "idValue": sticker_id,
            "updates": {"Status": status}
        })
        if result.get("success"):
            self.clear_cache()
        return result.get("success", False)

    def log_scan(self, log_data):
        headers = ["Timestamp", "StickerID", "Result", "UserEmail", "UserRole", "Notes"]
        row = [log_data.get(h, "") for h in headers]
        return self._post_action({"action": "append", "sheet": "Logs", "data": row}).get("success", False)

@st.cache_resource
def get_sheets_handler():
    return SheetsHandler()