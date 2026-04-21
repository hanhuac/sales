import streamlit as st
import pandas as pd
from datetime import datetime

# --- 頁面設定 ---
st.set_page_config(page_title="部門收支系統", layout="centered")

# --- 樣式美化 (隱藏 Streamlit 預設選單) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 初始化資料 (Session State) ---
if 'records' not in st.session_state:
    st.session_state.records = pd.DataFrame(columns=['日期', '項目', '類別', '金額', '銀行代碼', '備註'])

if 'assets' not in st.session_state:
    st.session_state.assets = {"現金": 0, "國泰世華銀行": 0, "中國信託銀行": 0, "中華郵政": 0}

# --- 導航選單 ---
menu = st.sidebar.radio("功能導航", ["快速記帳", "後台管理系統"])

# --- 1. 前台：快速記帳 ---
if menu == "快速記帳":
    st.title("➕ 新增消費明細")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            item = st.text_input("項目名稱")
            category = st.selectbox("類別", ["飲食", "交通", "購物", "學業", "娛樂", "其他"])
        with col2:
            amount = st.number_input("金額", min_value=0, step=1)
            bank_code = st.text_input("銀行代碼 / 付款方式", value="GEN")
        
        note = st.text_area("備註")
        submit = st.form_submit_button("確認新增", use_container_width=True)
        
        if submit:
            if item and amount > 0:
                new_row = {
                    '日期': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    '項目': item, '類別': category, '金額': amount,
                    '銀行代碼': bank_code, '備註': note
                }
                st.session_state.records = pd.concat([st.session_state.records, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"✅ 已記錄：{item}")
            else:
                st.error("請輸入完整資料")

# --- 2. 後台：管理與 PDF 匯出 ---
elif menu == "後台管理系統":
    st.title("⚙️ 後台管理中心")
    admin_code = st.text_input("請輸入管理授權編號", type="password")
    
    if admin_code == "0950108":
        st.success("身分確認：管理員已登入")
        
        # 資產修改區
        st.subheader("🏦 目前資產管理")
        cols = st.columns(4)
        asset_keys = list(st.session_state.assets.keys())
        for i, key in enumerate(asset_keys):
            st.session_state.assets[key] = cols[i].number_input(key, value=st.session_state.assets[key])
            
        st.divider()
        
        # 明細編輯區
        st.subheader("📜 完整歷史明細")
        edited_df = st.data_editor(st.session_state.records, use_container_width=True, num_rows="dynamic")
        if st.button("儲存修改資料"):
            st.session_state.records = edited_df
            st.toast("資料同步成功！")
        
        st.divider()

        # PDF 匯出區 (HTML 格式邏輯)
        st.subheader("🖨️ 匯出部門報表")
        if not st.session_state.records.empty:
            today_date = datetime.now().strftime('%Y/%m/%d')
            now_time = datetime.now().strftime('%H:%M')
            total_amt = st.session_state.records['金額'].sum()
            
            # 構建 HTML 報表內容
            html_report = f"""
            <div style="font-family: 'Arial', sans-serif; padding: 20px; border: 1px solid #000;">
                <h2 style="text-align: center;">部門收支額報告</h2>
                <p style="display: flex; justify-content: space-between;">
                    <span>日期：{today_date}</span>
                    <span style="float: right;">時間：{now_time}</span>
                </p>
                <div style="clear: both;"></div>
                <p>部門：00001<br>列印者編號：{admin_code}</p>
                <hr style="border-top: 2px solid black;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 1px solid black;">
                            <th align="left">日期</th><th align="left">項目 (銀行)</th><th align="right">金額</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for _, row in st.session_state.records.iterrows():
                html_report += f"<tr><td>{row['日期'].split(' ')[0]}</td><td>{row['項目']} ({row['銀行代碼']})</td><td align='right'>${row['金額']:,}</td></tr>"
            
            html_report += f"""
                    </tbody>
                </table>
                <div style="text-align: right; font-weight: bold; margin-top: 10px;">總計金額：${total_amt:,}</div>
                <hr style="border-top: 2px solid black;">
                <div style="text-align: center; margin-top: 10px; position: relative;">
                    <span style="background: white; padding: 0 10px; position: relative; z-index: 1;">報告結束</span>
                    <div style="position: absolute; top: 50%; left: 0; right: 0; border-top: 1px solid black; z-index: 0;"></div>
                </div>
            </div>
            """
            
            # 轉換為下載按鈕
            # 註：在 Streamlit 中直接匯出 PDF 檔案通常透過 HTML 封裝成下載連結
            st.download_button(
                label="📥 下載 PDF 報表 (HTML格式)",
                data=html_report,
                file_name=f"Report_{datetime.now().strftime('%m%d%H%M')}.html",
                mime="text/html",
                use_container_width=True
            )
            st.caption("提示：下載後使用瀏覽器開啟，按 Ctrl+P 並選擇『另存為 PDF』即可永久儲存。")
        else:
            st.write("尚無資料可供匯出。")
            
    elif admin_code != "":
        st.error("授權編號錯誤！")