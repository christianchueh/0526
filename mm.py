import streamlit as st
import pandas as pd

# 假設這是你的連線物件
# conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 1. 初始化：確保 df 存在於 session_state 中
# ==========================================
if "df" not in st.session_state:
    # 第一次載入時從 Google Sheets 讀取
    # st.session_state.df = conn.read(worksheet="Tasks")
    
    # 範例測試資料（實際使用請換回上方連線讀取）
    st.session_state.df = pd.DataFrame([
        {"task_id": 1, "title": "任務一", "owner": "小明", "status": "To Do"},
        {"task_id": 2, "title": "任務二", "owner": "小華", "status": "In Progress"}
    ])

# ==========================================
# 2. 渲染卡片的函式
# ==========================================
def render_cards(task_df):
    if task_df.empty:
        st.info("目前沒有任務")
        return

    for _, row in task_df.iterrows():
        task_id = row["task_id"]

        with st.container(border=True):
            st.write(f"### {row['title']}")
            st.caption(f"👤 負責人：{row['owner']}")
            st.caption(f"📌 狀態：{row['status']}")

            status_options = ["To Do", "In Progress", "Done"]

            # ======================
            # 狀態更新
            # ======================
            new_status = st.selectbox(
                "變更狀態",
                status_options,
                index=status_options.index(row["status"]),
                key=f"status_{task_id}"
            )

            if new_status != row["status"]:
                # 直接修改 session_state 裡的 df
                idx = st.session_state.df[st.session_state.df["task_id"] == task_id].index
                st.session_state.df.loc[idx, "status"] = new_status
                
                # 同步回雲端
                conn.update(worksheet="Tasks", data=st.session_state.df)
                st.rerun()

            # ======================
            # 編輯
            # ======================
            with st.popover("✏️ 編輯"):
                edit_title = st.text_input("任務名稱", value=row["title"], key=f"title_{task_id}")
                edit_owner = st.text_input("負責人", value=row["owner"], key=f"owner_{task_id}")
                edit_status = st.selectbox("狀態", status_options, index=status_options.index(row["status"]), key=f"edit_status_{task_id}")

                if st.button("💾 儲存", key=f"save_{task_id}"):
                    idx = st.session_state.df[st.session_state.df["task_id"] == task_id].index
                    st.session_state.df.loc[idx, "title"] = edit_title
                    st.session_state.df.loc[idx, "owner"] = edit_owner
                    st.session_state.df.loc[idx, "status"] = edit_status
                    
                    conn.update(worksheet="Tasks", data=st.session_state.df)
                    st.rerun()

            # ======================
            # 刪除（已修復）
            # ======================
            if st.button("🗑️ 刪除", key=f"delete_{task_id}"):
                # 1. 篩選掉被刪除的資料，更新 session_state
                st.session_state.df = st.session_state.df[st.session_state.df["task_id"] != task_id].reset_index(drop=True)
                
                # 2. 將最新的正確資料寫回 Google Sheets
                conn.update(
                    worksheet="Tasks",
                    data=st.session_state.df
                )
                
                # 3. 強制刷新頁面，重新渲染
                st.rerun()

# ==========================================
# 3. 主程式呼叫
# ==========================================
# 傳入當前最新的 session_state 資料
render_cards(st.session_state.df)
