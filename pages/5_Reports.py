import streamlit as st
from utils.sheets import get_sheets_handler
from utils.theme import apply_theme, render_banner, render_footer
import config
import pandas as pd
from io import BytesIO


if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

# Only Admin can view reports
if st.session_state.user_role != "Admin":
    st.error("🚫 Access Denied. This page requires Admin privileges.")
    st.stop()


st.set_page_config(page_title="Reports", page_icon="📈", layout="wide")
apply_theme()

if not st.session_state.get("authenticated"):
    st.error("Please login first")
    st.stop()

render_banner("📈 Reports & Analytics")
sheets = get_sheets_handler()

members = sheets.get_all_members()
stickers = sheets.get_all_stickers()
logs = sheets.get_logs()

tab1, tab2, tab3 = st.tabs(["👥 Members Report", "🎫 Stickers Report", "📝 Scan Logs"])

# ===== TAB 1: MEMBERS REPORT =====
with tab1:
    st.markdown("### Members Report")
    if members:
        report_data = [{
            "Building": m.get("Building", ""), "Flat No": m.get("Flat No", ""),
            "Member ID": m.get("ID", ""), "Name": m.get("Name", ""),
            "Mobile": m.get("Mobile", ""), "Email": m.get("Email", ""),
            "Vehicle Type": m.get("Vehicle Type", ""), "Vehicle Number": m.get("Vehicle Number", ""),
            "Status": m.get("Status", "Active"), "Date Added": m.get("DateAdded", ""),
            "Valid Period": m.get("Valid Period", ""), "Valid Till Date": m.get("Valid Till Date", "")
        } for m in members]
        
        df = pd.DataFrame(report_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Members')
            return output.getvalue()
        
        st.download_button(label="📥 Download Members Report (Excel)", data=to_excel(df),
            file_name=f"members_report_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.info("No members data available.")

# ===== TAB 2: STICKERS REPORT (WITH FIXED DELETE) =====
with tab2:
    st.markdown("### 🎫 Stickers Report")
    if stickers:
        report_data = []
        for s in stickers:
            member = sheets.get_member_by_id(s.get("MemberID"))
            report_data.append({
                "Sticker ID": s.get("StickerID", ""), "Member ID": s.get("MemberID", ""),
                "Member Name": member.get("Name", "N/A") if member else "N/A",
                "Building": s.get("Building", ""), "Flat No": s.get("FlatNo", ""),
                "Vehicle No": s.get("VehicleNo", ""), "Status": s.get("Status", ""),
                "Issued Date": s.get("IssuedDate", ""), "Expiry Date": s.get("ExpiryDate", ""),
                "Color": s.get("Color", ""), "Remarks": s.get("Remarks", "")
            })
        
        df = pd.DataFrame(report_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### 🗑️ Delete Sticker")
        
        dcol1, dcol2, dcol3 = st.columns([2, 1, 1])
        with dcol1:
            sticker_labels = [f"{s.get('StickerID')} - {report_data[i]['Member Name']} ({s.get('Building')}-{s.get('FlatNo')}) - {s.get('VehicleNo')} [{s.get('Status')}]" for i, s in enumerate(stickers)]
            selected_sticker = st.selectbox("Select Sticker to Delete", sticker_labels, key="delete_sticker_select")
            selected_sticker_id = selected_sticker.split(" - ")[0]
        
        with dcol2:
            st.write(""); st.write("")
            # FIXED DELETION LOGIC USING SESSION STATE
            if st.button("🗑️ Delete Sticker", use_container_width=True, type="secondary", key=f"del_sticker_btn_{selected_sticker_id}"):
                st.session_state[f"confirm_del_sticker_{selected_sticker_id}"] = True
            
            if st.session_state.get(f"confirm_del_sticker_{selected_sticker_id}"):
                st.warning(f"⚠️ Delete sticker **{selected_sticker_id}**?")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("⚠️ Yes", key=f"yes_sticker_{selected_sticker_id}", type="primary", use_container_width=True):
                        if sheets.delete_sticker(selected_sticker_id):
                            st.success(f"🗑️ Sticker '{selected_sticker_id}' deleted!")
                            st.session_state[f"confirm_del_sticker_{selected_sticker_id}"] = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete sticker")
                with c_no:
                    if st.button("Cancel", key=f"no_sticker_{selected_sticker_id}", use_container_width=True):
                        st.session_state[f"confirm_del_sticker_{selected_sticker_id}"] = False
                        st.rerun()
        
        with dcol3:
            st.write(""); st.write("")
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Stickers')
                return output.getvalue()
            st.download_button(label="📥 Download Stickers Report", data=to_excel(df),
                file_name=f"stickers_report_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.info("No stickers data available.")

# ===== TAB 3: SCAN LOGS =====
with tab3:
    st.markdown("### 📝 Scan Logs Report")
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True, hide_index=True)
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Logs')
            return output.getvalue()
        st.download_button(label="📥 Download Scan Logs", data=to_excel(df),
            file_name=f"scan_logs_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.info("No scan logs available.")

render_footer()
