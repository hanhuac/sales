import streamlit as st
import pandas as pd
from datetime import datetime
import base64

# --- 頁面設定 ---
st.set_page_config(page_title="部門收支管理系統", layout="centered")

# --- 標題與樣式 ---
st.title("📊 部門收支明細系統")
st.info("歡迎使用，請輸入明細或生成報表。")

# --- 初始化資料庫 (使用 Session State 模擬資料庫) ---
if 'records' not in st.session_state:
    st.session_state.records = pd.DataFrame(columns=['日期', '項目', '類別', '金額', '銀行代碼', '備註'])

# --- 側邊欄：新增明細 ---
with st.sidebar:
    st.header("📝 新增消費明細")
    item = st.text_input("項目名稱")
    category = st.selectbox("類別", ["飲食", "交通", "購物", "學業", "娛樂", "其他"])
    amount = st.number_input("金額", min_value=0, step=1)
    bank_code = st.text_input("銀行代碼 / 付款方式", value="GEN")
    note = st.text_area("備註")
    
    if st.button("確認新增"):
        if item and amount > 0:
            new_data = {
                '日期': datetime.now().strftime('%Y-%m-%d %H:%M'),
                '項目': item,
                '類別': category,
                '金額': amount,
                '銀行代碼': bank_code,
                '備註': note
            }
            st.session_state.records = pd.concat([st.session_state.records, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"已記錄：{item}")
        else:
            st.error("請填寫項目與金額")

# --- 主要區域：顯示當前明細 ---
st.subheader("📋 當前消費明細")
st.dataframe(st.session_state.records, use_container_width=True)

# --- 權限驗證與報表生成 ---
st.divider()
st.subheader("🖨️ 導出部門報表")
auth_code = st.text_input("請輸入列印授權編號", type="password")

if st.button("生成 PDF 報表內容"):
    if auth_code == "0950108":
        if st.session_state.records.empty:
            st.warning("目前沒有資料可以匯出。")
        else:
            # 構建符合你要求的 HTML 內容
            today_date = datetime.now().strftime('%Y/%m/%d')
            now_time = datetime.now().strftime('%H:%M')
            total_amt = st.session_state.records['金額'].sum()
            
            html_report = f"""
            <div style="font-family: sans-serif; border: 1px solid #ccc; padding: 20px;">
                <h2 style="text-align: center;">部門收支額報告</h2>
                <div style="display: flex; justify-content: space-between;">
                    <span>日期：{today_date}</span>
                    <span>時間：{now_time}</span>
                </div>
                <div>部門：00001</div>
                <div>列印者編號：{auth_code}</div>
                <hr style="border: 1px solid black;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 2px solid #333;">
                            <th align="left">日期</th>
                            <th align="left">項目 (銀行)</th>
                            <th align="right">金額</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for _, row in st.session_state.records.iterrows():
                html_report += f"""
                        <tr>
                            <td>{row['日期'].split(' ')[0]}</td>
                            <td>{row['項目']} ({row['銀行代碼']})</td>
                            <td align="right">${row['金額']:,}</td>
                        </tr>
                """
            
            html_report += f"""
                    </tbody>
                </table>
                <div style="text-align: right; font-weight: bold; font-size: 1.2em; margin-top: 10px;">
                    總計金額：${total_amt:,}
                </div>
                <hr style="border: 1px solid black;">
                <div style="display: flex; align-items: center; text-align: center;">
                    <div style="flex: 1; border-bottom: 1px solid black;"></div>
                    <span style="padding: 0 10px;">報告結束</span>
                    <div style="flex: 1; border-bottom: 1px solid black;"></div>
                </div>
            </div>
            """
            
            # 在網頁上預覽
            st.markdown(html_report, unsafe_allow_html=True)
            st.success("報表已生成，您可以直接長按螢幕選擇列印或儲存為 PDF。")
            
    elif auth_code != "":
        st.error("授權編號錯誤！")