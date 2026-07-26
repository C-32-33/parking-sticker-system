import streamlit as st
from utils.sheets import get_sheets_handler
from utils.theme import apply_theme, render_banner, render_footer
import config
import pandas as pd
from datetime import datetime


if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

# Only Admin and Committee can manage members
if st.session_state.user_role not in ["Admin", "Committee"]:
    st.error("🚫 Access Denied. This page requires Admin or Committee privileges.")
    st.stop()


st.set_page_config(page_title="Manage Members", page_icon="👥", layout="wide")
apply_theme()

if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

render_banner("👥 Manage Members")
sheets = get_sheets_handler()

# Initialize session state for deletion
if "delete_member_id" not in st.session_state:
    st.session_state.delete_member_id = None
if "delete_member_name" not in st.session_state:
    st.session_state.delete_member_name = None

tab1, tab2 = st.tabs(["➕ Add Member", " Member List"])

# ===== TAB 1: ADD MEMBER =====
with tab1:
    st.markdown("### Add New Member")
    col1, col2 = st.columns(2)
    
    with col1:
        building = st.selectbox("🏢 Building", config.BUILDINGS)
        flat_no = st.selectbox("🚪 Flat No", config.ALL_FLAT_NUMBERS)
        member_id = st.text_input("🆔 Member ID", placeholder=f"{building.replace('-', '')}{flat_no}")
        name = st.text_input(" Name")
        mobile = st.text_input("📱 Mobile", placeholder="10-digit number")
        email = st.text_input("📧 Email", placeholder="email@example.com")
    
    with col2:
        vehicle_type = st.selectbox(" Vehicle Type", ["Car", "Bike", "Scooter"])
        vehicle_number = st.text_input(" Vehicle Number", placeholder="MH04HG75432")
        valid_period = st.number_input("📅 Valid Period (months)", min_value=1, max_value=60, value=12)
        today = datetime.now()
        from datetime import timedelta
        valid_till = today + timedelta(days=30 * valid_period)
        valid_till_date = st.date_input("📅 Valid Till Date", value=valid_till)
        status = st.selectbox("📊 Status", ["Active", "Blocked"])
        date_added = today.strftime('%Y-%m-%d')
    
    if st.button("➕ Add Member", type="primary", use_container_width=True):
        if not member_id or not name:
            st.error("❌ Member ID and Name are required")
        else:
            existing = sheets.get_member_by_id(member_id)
            if existing:
                st.error(f"❌ Member ID '{member_id}' already exists!")
            else:
                member_data = {
                    "Building": building, "ID": member_id, "Name": name, "Flat No": flat_no,
                    "Mobile": mobile, "Email": email, "Vehicle Type": vehicle_type,
                    "Vehicle Number": vehicle_number, "Status": status, "DateAdded": date_added,
                    "Valid Period": f"{valid_period} months", "Valid Till Date": valid_till_date.strftime('%Y-%m-%d')
                }
                if sheets.add_member(member_data):
                    st.success(f"✅ Member '{name}' added successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to add member")

# ===== TAB 2: MEMBER LIST =====
with tab2:
    st.markdown("### All Members")
    members = sheets.get_all_members()
    
    if not members:
        st.info("No members added yet.")
    else:
        display_data = []
        for m in members:
            display_data.append({
                "Building": m.get("Building", ""), "Flat No": m.get("Flat No", ""),
                "Member ID": m.get("ID", ""), "Name": m.get("Name", ""),
                "Mobile": m.get("Mobile", ""), "Vehicle Type": m.get("Vehicle Type", ""),
                "Vehicle Number": m.get("Vehicle Number", ""), "Status": m.get("Status", "Active"),
                "Valid Period": m.get("Valid Period", ""), "Valid Till Date": m.get("Valid Till Date", "")
            })
        
        df = pd.DataFrame(display_data)
        def highlight_status(row):
            color = '#C8E6C9' if row['Status'] == 'Active' else '#FFCDD2'
            return [f'background-color: {color}'] * len(row)
        
        st.dataframe(df.style.apply(highlight_status, axis=1), use_container_width=True, height=400, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### ⚙️ Quick Actions")
        
        # Create member labels list
        member_labels = [f"{m.get('ID')} - {m.get('Name')} ({m.get('Building')}-{m.get('Flat No')}) [{m.get('Status', 'Active')}]" for m in members]
        
        mcol1, mcol2, mcol3, mcol4 = st.columns([2, 1, 1, 1])
        with mcol1:
            selected_member = st.selectbox("Select Member", member_labels, key="manage_actions")
        
        # Extract member info from selection
        if " - " in selected_member:
            sel_member_id = selected_member.split(" - ")[0]
            member_name = selected_member.split(" - ")[1].split(" (")[0]
        else:
            sel_member_id = None
            member_name = None
        
        with mcol2:
            st.write(""); st.write("")
            if st.button("🚫 Block", use_container_width=True, key="block_btn"):
                if sel_member_id:
                    sheets.update_member_status(sel_member_id, "Blocked")
                    st.success("✅ Member blocked!")
                    st.rerun()
        
        with mcol3:
            st.write(""); st.write("")
            if st.button("✅ Unblock", use_container_width=True, key="unblock_btn"):
                if sel_member_id:
                    sheets.update_member_status(sel_member_id, "Active")
                    st.success("✅ Member unblocked!")
                    st.rerun()
        
        with mcol4:
            st.write(""); st.write("")
            
            # Handle deletion confirmation flow
            if st.session_state.delete_member_id is None:
                # Show initial delete button
                if st.button("️ Delete", use_container_width=True, key="delete_btn", type="secondary"):
                    if sel_member_id:
                        st.session_state.delete_member_id = sel_member_id
                        st.session_state.delete_member_name = member_name
                        st.rerun()
            else:
                # Show confirmation
                st.warning(f"⚠️ Delete **{st.session_state.delete_member_name}**?")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("⚠️ Yes", key="confirm_yes", type="primary", use_container_width=True):
                        if sheets.delete_member(st.session_state.delete_member_id):
                            st.success(f"🗑️ Deleted '{st.session_state.delete_member_name}'!")
                            st.session_state.delete_member_id = None
                            st.session_state.delete_member_name = None
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete member")
                with c_no:
                    if st.button("Cancel", key="confirm_no", use_container_width=True):
                        st.session_state.delete_member_id = None
                        st.session_state.delete_member_name = None
                        st.rerun()

render_footer()
