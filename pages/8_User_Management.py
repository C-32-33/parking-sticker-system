import streamlit as st
from utils.sheets import get_sheets_handler
from utils.theme import apply_theme, render_banner, render_footer
import config
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="User Management", page_icon="👨‍", layout="wide")
apply_theme()

if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

# Only Admin can access this page
if st.session_state.user_role != "Admin":
    st.error("🚫 Access Denied. Admin privileges required.")
    st.stop()

render_banner("👨‍💼 User Management")
sheets = get_sheets_handler()

tab1, tab2, tab3 = st.tabs(["➕ Add User", " User List", "🔑 Change My Password"])

# ===== TAB 1: ADD USER =====
with tab1:
    st.markdown("### Add New User")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_username = st.text_input(" Username *", placeholder="Enter username")
        new_email = st.text_input("📧 Email (Optional)", placeholder="email@example.com")
        new_password = st.text_input("🔑 Password *", type="password", placeholder="Enter password")
    
    with col2:
        new_role = st.selectbox("🎭 Role", ["Admin", "Committee", "Member"])
        new_status = st.selectbox("📊 Status", ["Active", "Inactive"])
    
    if st.button("➕ Add User", type="primary", use_container_width=True):
        if not new_username or not new_password:
            st.error("❌ Username and Password are required!")
        else:
            # Check if username already exists
            users = sheets._get_data("Users")
            username_exists = any(str(u.get("Username")).strip().lower() == new_username.strip().lower() for u in users)
            
            if username_exists:
                st.error(f"❌ Username '{new_username}' already exists!")
            else:
                # Add user to Google Sheet
                headers = ["Username", "Email", "PasswordHash", "Role", "Status", "DateAdded"]
                row = [
                    new_username,
                    new_email,
                    new_password,
                    new_role,
                    new_status,
                    datetime.now().strftime("%Y-%m-%d")
                ]
                
                result = sheets._post_action({
                    "action": "append",
                    "sheet": "Users",
                    "headers": headers,
                    "data": row
                })
                
                if result.get("success"):
                    st.success(f"✅ User '{new_username}' added successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to add user")

# ===== TAB 2: USER LIST =====
with tab2:
    st.markdown("### All Users")
    users = sheets._get_data("Users")
    
    if not users:
        st.info("No users found.")
    else:
        df = pd.DataFrame(users)
        
        # Color-code by role
        def highlight_role(row):
            colors = {
                "Admin": "#FFD700",       # Gold
                "Committee": "#90EE90",   # Light green
                "Member": "#ADD8E6"       # Light blue
            }
            color = colors.get(row.get("Role", ""), "white")
            return [f'background-color: {color}'] * len(row)
        
        # Show only relevant columns
        display_df = df[['Username', 'Email', 'Role', 'Status', 'DateAdded']]
        
        st.dataframe(
            display_df.style.apply(highlight_role, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        st.markdown("#### ⚙️ User Actions")
        
        user_labels = [f"{u.get('Username')} - {u.get('Role')} ({u.get('Status')})" for u in users]
        selected_user = st.selectbox("Select User", user_labels)
        selected_username = selected_user.split(" - ")[0]
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("🚫 Block User", use_container_width=True):
                sheets._post_action({
                    "action": "update",
                    "sheet": "Users",
                    "idColumn": "Username",
                    "idValue": selected_username,
                    "updates": {"Status": "Inactive"}
                })
                st.success("✅ User blocked!")
                st.rerun()
        
        with action_col2:
            if st.button("✅ Unblock User", use_container_width=True):
                sheets._post_action({
                    "action": "update",
                    "sheet": "Users",
                    "idColumn": "Username",
                    "idValue": selected_username,
                    "updates": {"Status": "Active"}
                })
                st.success("✅ User unblocked!")
                st.rerun()
        
        with action_col3:
            if st.button("🗑️ Delete User", use_container_width=True, type="secondary"):
                if st.session_state.username == selected_username:
                    st.error("❌ You cannot delete your own account!")
                else:
                    sheets._post_action({
                        "action": "delete",
                        "sheet": "Users",
                        "idColumn": "Username",
                        "idValue": selected_username
                    })
                    st.success("✅ User deleted!")
                    st.rerun()

# ===== TAB 3: CHANGE MY PASSWORD =====
with tab3:
    st.markdown("### 🔑 Change Your Password")
    
    st.info(f"Logged in as: **{st.session_state.username}**")
    
    old_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    if st.button(" Update Password", type="primary", use_container_width=True):
        if len(new_password) < 4:
            st.error("❌ Password must be at least 4 characters!")
        elif new_password != confirm_password:
            st.error(" New passwords don't match!")
        else:
            # Update password in Google Sheet
            result = sheets._post_action({
                "action": "update",
                "sheet": "Users",
                "idColumn": "Username",
                "idValue": st.session_state.username,
                "updates": {"PasswordHash": new_password}
            })
            
            if result.get("success"):
                st.success("✅ Password updated successfully! Please login again.")
                st.session_state.authenticated = False
                st.rerun()
            else:
                st.error("❌ Failed to update password")

render_footer()