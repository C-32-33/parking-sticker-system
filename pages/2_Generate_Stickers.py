import streamlit as st
from utils.sheets import get_sheets_handler
from utils.sticker_generator import StickerGenerator
from utils.theme import apply_theme, render_banner, render_footer
import config
from datetime import datetime, timedelta

if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

# Only Admin and Committee can generate stickers
if st.session_state.user_role not in ["Admin", "Committee"]:
    st.error("🚫 Access Denied. This page requires Admin or Committee privileges.")
    st.stop()


st.set_page_config(page_title="Generate Stickers", page_icon="", layout="wide")
apply_theme()

if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

render_banner("🎫 Generate Parking Stickers")
sheets = get_sheets_handler()
members = sheets.get_all_members()

active_members = [m for m in members if m.get("Status", "Active") == "Active"]

if not active_members:
    st.warning("⚠️ No active members found. Please add members first!")
    render_footer()
    st.stop()

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### Step 1: Select Member")
    
    filter_building = st.selectbox("🏢 Filter by Building", ["All"] + config.BUILDINGS)
    if filter_building != "All":
        filtered_members = [m for m in active_members if m.get("Building") == filter_building]
    else:
        filtered_members = active_members
    
    if not filtered_members:
        st.warning("⚠️ No members in this building.")
        render_footer()
        st.stop()
    
    # Create member labels with clear ID display
    member_labels = []
    for m in filtered_members:
        member_id = m.get("ID", "N/A")
        name = m.get("Name", "N/A")
        vtype = m.get("Vehicle Type", "N/A")
        vnum = m.get("Vehicle Number", "N/A")
        label = f"ID:{member_id} | {name} | {vtype} | {vnum}"
        member_labels.append(label)
    
    selected = st.selectbox("Choose Member", member_labels)
    selected_index = member_labels.index(selected)
    selected_member = filtered_members[selected_index]
    
    # CRITICAL: Extract and store the Member ID
    member_id = selected_member.get("ID")
    st.success(f"✅ Selected Member ID: **{member_id}**")
    
    st.markdown("### Step 2: Sticker Details")
    existing_vehicle = selected_member.get("Vehicle Number", "")
    vehicle_no = st.text_input("🚗 Vehicle Number", value=existing_vehicle, placeholder="MH02AB1234")
    color = st.selectbox(" Sticker Color", ["blue", "red", "green", "gold", "purple"])
    validity_months = st.number_input("📅 Valid For (months)", 1, 24, 12)
    
    today = datetime.now()
    expiry = today + timedelta(days=30 * validity_months)
    st.info(f"📆 Valid until: **{expiry.strftime('%d %b %Y')}**")

with col_right:
    st.markdown("### Member Info")
    st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid {config.COLOR_PRIMARY}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <p><b>🏢 Building:</b> {selected_member.get('Building')}</p>
            <p><b>🚪 Flat:</b> {selected_member.get('Flat No')}</p>
            <p><b>🆔 Member ID:</b> <span style='color: red; font-weight: bold;'>{selected_member.get('ID')}</span></p>
            <p><b> Name:</b> {selected_member.get('Name')}</p>
            <p><b>📱 Mobile:</b> {selected_member.get('Mobile')}</p>
            <p><b>🚗 Vehicle Type:</b> {selected_member.get('Vehicle Type')}</p>
            <p><b>🔢 Vehicle Number:</b> {selected_member.get('Vehicle Number', 'N/A')}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if st.button("✅ Generate Sticker", type="primary", use_container_width=True):
    if not vehicle_no:
        st.error(" Please enter a vehicle number")
    elif not member_id:
        st.error("❌ Member ID is missing! Please re-select the member.")
    else:
        # Generate sticker ID
        sticker_id = StickerGenerator.generate_random_sticker_id()
        
        # Generate sticker image
        sticker_img = StickerGenerator.generate_sticker(
            sticker_id=sticker_id,
            member_name=selected_member.get("Name"),
            vehicle_type=selected_member.get("Vehicle Type"),
            flat_no=f"{selected_member.get('Building')}-{selected_member.get('Flat No')}",
            color=color
        )
        
        if sticker_img:
            # CRITICAL: Save sticker with correct MemberID
            sticker_data = {
                "StickerID": sticker_id,
                "MemberID": member_id,  # This is the key fix!
                "Building": selected_member.get("Building"),
                "FlatNo": selected_member.get("Flat No"),
                "VehicleNo": vehicle_no,
                "Status": "Active",
                "IssuedDate": today.strftime('%Y-%m-%d'),
                "ExpiryDate": expiry.strftime('%Y-%m-%d'),
                "Color": color,
                "Remarks": ""
            }
            
            st.info(f"📝 Saving sticker with MemberID: **{member_id}**")
            
            if sheets.add_sticker(sticker_data):
                # Update member's vehicle info
                sheets.update_member_vehicle_info(
                    member_id=member_id,
                    vehicle_number=vehicle_no,
                    valid_period=f"{validity_months} months",
                    valid_till_date=expiry.strftime('%Y-%m-%d')
                )
                
                st.success(f"✅ Sticker Created!")
                st.write(f"**Sticker ID:** {sticker_id}")
                st.write(f"**Member ID:** {member_id}")
                st.balloons()
                
                rcol1, rcol2 = st.columns([2, 1])
                with rcol1:
                    st.image(sticker_img, caption=f"Sticker {sticker_id}", use_container_width=True)
                with rcol2:
                    building = selected_member.get('Building', 'Unknown')
                    flat = selected_member.get('Flat No', 'Unknown')
                    filename = f"sticker_{building}_{flat}_{sticker_id}.png"
                    st.download_button(
                        label="📥 Download Sticker",
                        data=sticker_img,
                        file_name=filename,
                        mime="image/png",
                        use_container_width=True
                    )
            else:
                st.error("❌ Failed to save sticker to database.")
                st.error("Check your Google Apps Script connection.")
        else:
            st.error("❌ Failed to generate sticker image.")

render_footer()
