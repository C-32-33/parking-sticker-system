import streamlit as st
from utils.sheets import get_sheets_handler
from utils.theme import apply_theme, render_banner, render_footer
import config
import pandas as pd

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
apply_theme()

if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

render_banner("📊 Dashboard")
sheets = get_sheets_handler()
members = sheets.get_all_members()
stickers = sheets.get_all_stickers()
logs = sheets.get_logs()

st.markdown("### 📈 Overall Statistics")
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("👥 Total Members", len(members))
with c2: st.metric(" Total Stickers", len(stickers))
with c3: st.metric("✅ Active Stickers", len([s for s in stickers if s.get("Status") == "Active"]))
with c4: st.metric("📝 Total Scans", len(logs))
st.markdown("---")

st.markdown("### 🏢 Building-wise Vehicle Summary")
def count_vehicles(members_list, building, v_type):
    return sum(1 for m in members_list if str(m.get("Building")) == building and str(m.get("Vehicle Type")) == v_type and m.get("Status", "Active") == "Active")

# Use clean keys internally to avoid KeyError
summary_data = []
for building in config.BUILDINGS:
    cars = count_vehicles(members, building, "Car")
    bikes = count_vehicles(members, building, "Bike")
    scooters = count_vehicles(members, building, "Scooter")
    summary_data.append({"Building": building, "Cars": cars, "Bikes": bikes, "Scooters": scooters, "Total": cars + bikes + scooters})

grand_cars = sum(row["Cars"] for row in summary_data)
grand_bikes = sum(row["Bikes"] for row in summary_data)
grand_scooters = sum(row["Scooters"] for row in summary_data)
summary_data.append({"Building": "🔷 TOTAL", "Cars": grand_cars, "Bikes": grand_bikes, "Scooters": grand_scooters, "Total": grand_cars + grand_bikes + grand_scooters})

bcols = st.columns(len(config.BUILDINGS) + 1)
for idx, building in enumerate(config.BUILDINGS):
    with bcols[idx]:
        cars = count_vehicles(members, building, "Car")
        bikes = count_vehicles(members, building, "Bike")
        scooters = count_vehicles(members, building, "Scooter")
        st.markdown(f"""<div style='background: linear-gradient(135deg, {config.COLOR_PRIMARY} 0%, {config.COLOR_SECONDARY} 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin:0;'>🏢 {building}</h3><hr style='border-color: rgba(255,255,255,0.3);'>
            <div style='display:flex; justify-content:space-around;'>
                <div><div style='font-size:28px; font-weight:bold;'>🚗 {cars}</div><div style='font-size:12px;'>Cars</div></div>
                <div><div style='font-size:28px; font-weight:bold;'>🏍️ {bikes}</div><div style='font-size:12px;'>Bikes</div></div>
                <div><div style='font-size:28px; font-weight:bold;'>🛵 {scooters}</div><div style='font-size:12px;'>Scooters</div></div>
            </div></div>""", unsafe_allow_html=True)

with bcols[-1]:
    st.markdown(f"""<div style='background: linear-gradient(135deg, {config.COLOR_ACCENT} 0%, #FF8F00 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
        <h3 style='margin:0;'>🔷 TOTAL</h3><hr style='border-color: rgba(255,255,255,0.3);'>
        <div style='display:flex; justify-content:space-around;'>
            <div><div style='font-size:28px; font-weight:bold;'>🚗 {grand_cars}</div><div style='font-size:12px;'>Cars</div></div>
            <div><div style='font-size:28px; font-weight:bold;'>🏍️ {grand_bikes}</div><div style='font-size:12px;'>Bikes</div></div>
            <div><div style='font-size:28px; font-weight:bold;'>🛵 {grand_scooters}</div><div style='font-size:12px;'>Scooters</div></div>
        </div></div>""", unsafe_allow_html=True)

st.markdown("---")
with st.expander("📋 View Detailed Summary Table"):
    df = pd.DataFrame(summary_data).rename(columns={"Cars": "🚗 Cars", "Bikes": "🏍️ Bikes", "Scooters": "🛵 Scooters", "Total": "📊 Total"})
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 👥 Member Status Management")

if members:
    display_data = []
    for m in members:
        member_stickers = [s for s in stickers if s.get("MemberID") == m.get("ID")]
        display_data.append({
            "Building": m.get("Building", " "),
            "Flat No": m.get("Flat No", " "),
            "Member ID": m.get("ID", " "),
            "Name": m.get("Name", " "),
            "Mobile": m.get("Mobile", " "),
            "Vehicle": m.get("Vehicle Type", " "),
            "Vehicle Number": m.get("Vehicle Number", " "),  # NEW
            "Sticker ID": member_stickers[-1].get("StickerID") if member_stickers else "N/A",
            "Stickers": len(member_stickers),
            "Status": m.get("Status", "Active"),
            "Valid Period": m.get("Valid Period", " "),  # NEW
            "Valid Till": m.get("Valid Till Date", " ")  # NEW
        })
    
    df = pd.DataFrame(display_data)
    
    def highlight_status(row):
        color = '#C8E6C9' if row['Status'] == 'Active' else '#FFCDD2'
        return [f'background-color: {color}'] * len(row)
    
    st.dataframe(
        df.style.apply(highlight_status, axis=1),
        use_container_width=True,
        height=300,
        hide_index=True
    )
    
    st.markdown("#### ⚙️ Quick Block/Unblock")
    mcol1, mcol2, mcol3 = st.columns([2, 1, 1])
    with mcol1:
        member_labels = [
            f"{m.get('ID')} - {m.get('Name')} ({m.get('Building')}-{m.get('Flat No')}) [{m.get('Status', 'Active')}]"
            for m in members
        ]
        selected_member = st.selectbox("Select Member", member_labels, key="dash_block")
        sel_member_id = selected_member.split(" - ")[0]
    with mcol2:
        st.write(""); st.write("")
        if st.button(" Block", use_container_width=True, key="dash_block_btn"):
            sheets.update_member_status(sel_member_id, "Blocked")
            st.success("Member blocked!")
            st.rerun()
    with mcol3:
        st.write(""); st.write("")
        if st.button("✅ Unblock", use_container_width=True, key="dash_unblock_btn"):
            sheets.update_member_status(sel_member_id, "Active")
            st.success("Member unblocked!")
            st.rerun()
else:
    st.info("No members to manage.")

render_footer()