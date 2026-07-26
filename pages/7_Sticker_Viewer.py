import streamlit as st
from utils.sheets import get_sheets_handler
from utils.sticker_generator import StickerGenerator
from utils.theme import apply_theme, render_banner, render_footer
import config
import pandas as pd

if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

# Only Admin and Committee can generate stickers
if st.session_state.user_role not in ["Admin", "Committee"]:
    st.error("🚫 Access Denied. This page requires Admin or Committee privileges.")
    st.stop()
    
st.set_page_config(page_title="Sticker Viewer", page_icon="🎫", layout="wide")
apply_theme()

if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

render_banner("🔎 Sticker Viewer & Download")
sheets = get_sheets_handler()

st.markdown("### 🔍 Search & Filter Stickers")

stickers = sheets.get_all_stickers()
members = sheets.get_all_members()

# Show debug info
st.info(f"📊 Found {len(stickers)} stickers and {len(members)} members in database")

if not stickers:
    st.warning("⚠️ No stickers generated yet.")
    render_footer()
    st.stop()

if not members:
    st.warning("⚠️ No members found in database.")
    render_footer()
    st.stop()

# Show all Member IDs for reference
st.markdown("### 📋 Available Member IDs in Database:")
member_id_list = [m.get("ID") for m in members]
st.write(f"**Member IDs:** {', '.join(member_id_list)}")

# Match stickers with members - DEBUG VERSION
st.markdown("---")
st.markdown("###  Stickers with Member Mapping")

sticker_data = []
for s in stickers:
    sticker_member_id = str(s.get("MemberID", "")).strip()
    member = None
    matched_member_id = None
    
    # Try to find matching member
    for m in members:
        member_id_in_sheet = str(m.get("ID", "")).strip()
        if sticker_member_id == member_id_in_sheet:
            member = m
            matched_member_id = member_id_in_sheet
            break
    
    if member:
        # Member found - use member data
        sticker_data.append({
            "StickerID": s.get("StickerID"),
            "MemberID": member.get("ID"),
            "MemberName": member.get("Name"),
            "Building": member.get("Building"),
            "FlatNo": member.get("Flat No"),
            "VehicleNo": s.get("VehicleNo"),
            "Status": s.get("Status"),
            "Color": s.get("Color", "red"),
            "IssuedDate": s.get("IssuedDate"),
            "ExpiryDate": s.get("ExpiryDate"),
            "MatchStatus": "✅ Matched"
        })
    else:
        # Member not found - show debug info
        sticker_data.append({
            "StickerID": s.get("StickerID"),
            "MemberID": sticker_member_id if sticker_member_id else "N/A",
            "MemberName": "Unknown Member",
            "Building": "N/A",
            "FlatNo": "N/A",
            "VehicleNo": s.get("VehicleNo"),
            "Status": s.get("Status"),
            "Color": s.get("Color", "red"),
            "IssuedDate": s.get("IssuedDate"),
            "ExpiryDate": s.get("ExpiryDate"),
            "MatchStatus": f"❌ No match for '{sticker_member_id}'"
        })

df = pd.DataFrame(sticker_data)

# Show which stickers have issues
unmatched = df[df["MatchStatus"].str.contains("❌")]
if len(unmatched) > 0:
    st.error(f"⚠️ **{len(unmatched)} sticker(s) not linked to any member:**")
    for idx, row in unmatched.iterrows():
        st.write(f"- Sticker `{row['StickerID']}` has MemberID: **`{row['MemberID']}`** (not found in members list)")
    st.markdown("---")

# Filter options
fcol1, fcol2, fcol3, fcol4 = st.columns(4)

with fcol1:
    buildings = ["All"] + sorted([b for b in df["Building"].dropna().unique().tolist() if b != "N/A"])
    filter_building = st.selectbox("🏢 Building", buildings if buildings else ["All"])

with fcol2:
    if filter_building != "All":
        filtered_df_temp = df[df["Building"] == filter_building]
        flats = ["All"] + sorted([f for f in filtered_df_temp["FlatNo"].dropna().unique().tolist() if f != "N/A"])
    else:
        flats = ["All"] + sorted([f for f in df["FlatNo"].dropna().unique().tolist() if f != "N/A"])
    filter_flat = st.selectbox("🚪 Flat No", flats if flats else ["All"])

with fcol3:
    if filter_building != "All" and filter_flat != "All":
        filtered_members = df[(df["Building"] == filter_building) & (df["FlatNo"] == filter_flat)]
    elif filter_building != "All":
        filtered_members = df[df["Building"] == filter_building]
    elif filter_flat != "All":
        filtered_members = df[df["FlatNo"] == filter_flat]
    else:
        filtered_members = df
    
    member_ids = ["All"] + sorted(filtered_members["MemberID"].dropna().unique().tolist())
    filter_member_id = st.selectbox("🆔 Member ID", member_ids if member_ids else ["All"])

with fcol4:
    search_text = st.text_input("🔎 Search", placeholder="Sticker ID or Vehicle No")

# Apply filters
filtered_df = df.copy()

if filter_building != "All":
    filtered_df = filtered_df[filtered_df["Building"] == filter_building]
if filter_flat != "All":
    filtered_df = filtered_df[filtered_df["FlatNo"] == filter_flat]
if filter_member_id != "All":
    filtered_df = filtered_df[filtered_df["MemberID"] == filter_member_id]
if search_text:
    filtered_df = filtered_df[
        (filtered_df["StickerID"].str.contains(search_text, case=False, na=False)) |
        (filtered_df["VehicleNo"].str.contains(search_text, case=False, na=False))
    ]

st.markdown(f"###  Found {len(filtered_df)} Sticker(s)")
st.markdown("---")

if filtered_df.empty:
    st.info("No stickers match the selected filters.")
else:
    for idx, row in filtered_df.iterrows():
        if row['MemberName'] != "Unknown Member":
            expander_label = f"🎫 {row['StickerID']} - {row['MemberName']} ({row['Building']}-{row['FlatNo']}) - {row['VehicleNo']} {row['MatchStatus']}"
        else:
            expander_label = f" {row['StickerID']} - {row['VehicleNo']} {row['MatchStatus']}"
        
        with st.expander(expander_label, expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**📋 Details:**")
                st.write(f"**Member ID:** {row['MemberID']}")
                st.write(f"**Name:** {row['MemberName']}")
                
                if row['Building'] != "N/A":
                    st.write(f"**Location:** {row['Building']} - {row['FlatNo']}")
                else:
                    st.write(f"**Location:** Not Available")
                
                st.write(f"**Vehicle:** {row['VehicleNo']}")
                st.write(f"**Status:** {row['Status']}")
                st.write(f"**Color:** {row['Color']}")
                st.write(f"**Issued:** {row['IssuedDate']}")
                st.write(f"**Expires:** {row['ExpiryDate']}")
                
                if row['MemberName'] == "Unknown Member":
                    st.error(f"⚠️ **Mismatch Detected:**")
                    st.write(f"Sticker has MemberID: **`{row['MemberID']}`**")
                    st.write(f"But this ID doesn't exist in Members sheet!")
                    st.write(f"Available IDs: **{', '.join(member_id_list)}**")
            
            with col2:
                st.markdown("**🖼️ Preview:**")
                sticker_img = StickerGenerator.generate_sticker(
                    sticker_id=row['StickerID'],
                    member_name=row['MemberName'],
                    vehicle_type="",
                    flat_no=f"{row['Building']}-{row['FlatNo']}" if row['Building'] != "N/A" else "N/A",
                    color=row['Color']
                )
                if sticker_img:
                    st.image(sticker_img, width=300)
                    filename = f"sticker_{row['StickerID']}.png"
                    st.download_button(
                        label="📥 Download Sticker",
                        data=sticker_img,
                        file_name=filename,
                        mime="image/png",
                        use_container_width=True
                    )

render_footer()
