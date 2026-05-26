import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 0. 初始化 Google Sheets 連線（修復 NameError 核心）
# ==========================================

# 建立與 Google Sheets 的連線物件（請確保你的 .streamlit/secrets.toml 設定正確）
conn = st.connection("gsheets", type=GSheetsConnection)


# ==========================================
# 1. 初始化資料並存入 session_state
# ==========================================

if "df" not in st.session_state:

    # 第一次執行時，從 Google Sheets 讀取最新資料並存入 session_state
    st.session_state.df = conn.read(worksheet="Tasks")


# ==========================================
# 2. 卡片渲染函式（保留你原汁原味的漂亮排版）
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

            # ======================
            # 狀態更新（用 task_id 找原 df）
            # ======================

            status_options = ["To Do", "In Progress", "Done"]

            new_status = st.selectbox(
                "變更狀態",
                status_options,
                index=status_options.index(row["status"]),
                key=f"status_{task_id}"
            )

            if new_status != row["status"]:

                # 使用 session_state 更新狀態，確保 Rerun 後資料不會被蓋掉
                idx = st.session_state.df[st.session_state.df["task_id"] == task_id].index
                st.session_state.df.loc[idx, "status"] = new_status

                conn.update(
                    worksheet="Tasks",
                    data=st.session_state.df
                )

                st.rerun()

            # ======================
            # 編輯
            # ======================

            with st.popover("✏️ 編輯"):

                edit_title = st.text_input(
                    "任務名稱",
                    value=row["title"],
                    key=f"title_{task_id}"
                )

                edit_owner = st.text_input(
                    "負責人",
                    value=row["owner"],
                    key=f"owner_{task_id}"
                )

                edit_status = st.selectbox(
                    "狀態",
                    status_options,
                    index=status_options.index(row["status"]),
                    key=f"edit_status_{task_id}"
                )

                if st.button("💾 儲存", key=f"save_{task_id}"):

                    # 使用 session_state 更新編輯內容
                    idx = st.session_state.df[st.session_state.df["task_id"] == task_id].index
                    st.session_state.df.loc[idx, "title"] = edit_title
                    st.session_state.df.loc[idx, "owner"] = edit_owner
                    st.session_state.df.loc[idx, "status"] = edit_status

                    conn.update(
                        worksheet="Tasks",
                        data=st.session_state.df
                    )

                    st.rerun()

            # ======================
            # 刪除（修復核心）
            # ======================

            if st.button("🗑️ 刪除", key=f"delete_{task_id}"):

                # 使用 session_state 進行篩選，徹底從暫存與雲端抹除
                st.session_state.df = st.session_state.df[st.session_state.df["task_id"] != task_id].reset_index(drop=True)

                conn.update(
                    worksheet="Tasks",
                    data=st.session_state.df
                )

                st.rerun()


# ==========================================
# 3. 主程式呼叫：傳入最新的暫存資料
# ==========================================

render_cards(st.session_state.df)
