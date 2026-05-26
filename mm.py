import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 頁面設定
# ==========================================

st.set_page_config(
    page_title="Trello 任務看板",
    layout="wide"
)

st.title("📋 階段四終極完成版：GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正 | 完整功能版")

# ==========================================
# Google Sheets 連線
# ==========================================

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    worksheet="Tasks",
    ttl=0
)

# 避免空資料報錯
if df.empty:
    df = pd.DataFrame(columns=["title", "status", "owner"])

# ==========================================
# 上方新增任務區塊
# ==========================================

st.write("## ✨ 指派新任務")

with st.form("task_input_form", clear_on_submit=True):

    c1, c2, c3 = st.columns([2, 1, 1])

    with c1:
        new_title = st.text_input(
            "📌 任務名稱",
            placeholder="請輸入任務名稱..."
        )

    with c2:
        new_status = st.selectbox(
            "📍 狀態",
            ["To Do", "In Progress", "Done"]
        )

    with c3:
        new_owner = st.text_input(
            "👤 負責人",
            placeholder="誰來負責..."
        )

    submit_btn = st.form_submit_button("✅ 確認指派並同步雲端")

# ==========================================
# 新增任務
# ==========================================

if submit_btn:

    if new_title and new_owner:

        new_data = {
            "title": new_title,
            "status": new_status,
            "owner": new_owner
        }

        new_row = pd.DataFrame([new_data])

        updated_df = pd.concat(
            [df, new_row],
            ignore_index=True
        )

        conn.update(
            worksheet="Tasks",
            data=updated_df
        )

        st.success("🎉 任務已成功同步至 Google Sheets！")

        st.rerun()

    else:
        st.warning("⚠️ 任務名稱與負責人不可空白")

st.divider()

# ==========================================
# 任務統計
# ==========================================

todo_count = len(df[df["status"] == "To Do"])
ip_count = len(df[df["status"] == "In Progress"])
done_count = len(df[df["status"] == "Done"])

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("📝 待辦", todo_count)

with m2:
    st.metric("🚧 執行中", ip_count)

with m3:
    st.metric("✅ 已完成", done_count)

st.divider()

# ==========================================
# Trello 三欄
# ==========================================

st.write("## 📊 看板動態狀態監控")

col1, col2, col3 = st.columns(3)

# ==========================================
# To Do
# ==========================================

with col1:

    st.markdown(
        "### <span style='color:red'>🔴 To Do (待辦)</span>",
        unsafe_allow_html=True
    )

    todo_list = df[df["status"] == "To Do"]

    if not todo_list.empty:

        for idx, row in todo_list.iterrows():

            with st.container(border=True):

    # 顯示卡片
    st.write(f"### {row['title']}")
    st.caption(f"👤 負責人：{row['owner']}")
    st.caption(f"📌 狀態：{row['status']}")

    # =====================================
    # 狀態快速切換
    # =====================================

    new_status = st.selectbox(
        "變更狀態",
        ["To Do", "In Progress", "Done"],
        index=["To Do", "In Progress", "Done"].index(row["status"]),
        key=f"status_{idx}"
    )

    if new_status != row["status"]:

        df.at[idx, "status"] = new_status

        conn.update(
            worksheet="Tasks",
            data=df
        )

        st.success("✅ 狀態已更新")

        st.rerun()

    # =====================================
    # 編輯卡片區塊
    # =====================================

    with st.expander("✏️ 編輯任務"):

        edit_title = st.text_input(
            "任務名稱",
            value=row["title"],
            key=f"title_{idx}"
        )

        edit_owner = st.text_input(
            "負責人",
            value=row["owner"],
            key=f"owner_{idx}"
        )

        edit_status = st.selectbox(
            "任務狀態",
            ["To Do", "In Progress", "Done"],
            index=["To Do", "In Progress", "Done"].index(row["status"]),
            key=f"edit_status_{idx}"
        )

        # 儲存修改
        if st.button("💾 儲存修改", key=f"save_{idx}"):

            df.at[idx, "title"] = edit_title
            df.at[idx, "owner"] = edit_owner
            df.at[idx, "status"] = edit_status

            conn.update(
                worksheet="Tasks",
                data=df
            )

            st.success("✅ 任務已更新")

            st.rerun()

    # =====================================
    # 刪除任務
    # =====================================

    if st.button("🗑️ 刪除任務", key=f"delete_{idx}"):

        df = df.drop(idx)

        conn.update(
            worksheet="Tasks",
            data=df
        )

        st.warning("任務已刪除")

        st.rerun()

    else:
        st.info("目前沒有待辦任務")

# ==========================================
# In Progress
# ==========================================

with col2:

    st.markdown(
        "### <span style='color:orange'>🟠 In Progress (執行中)</span>",
        unsafe_allow_html=True
    )

    ip_list = df[df["status"] == "In Progress"]

    if not ip_list.empty:

        for idx, row in ip_list.iterrows():

            with st.container(border=True):

                st.write(f"### {row['title']}")
                st.caption(f"👤 負責人：{row['owner']}")

                # 狀態切換
                new_status = st.selectbox(
                    "變更狀態",
                    ["To Do", "In Progress", "Done"],
                    index=["To Do", "In Progress", "Done"].index(row["status"]),
                    key=f"status_{idx}"
                )

                # 更新狀態
                if new_status != row["status"]:

                    df.at[idx, "status"] = new_status

                    conn.update(
                        worksheet="Tasks",
                        data=df
                    )

                    st.success("✅ 狀態已更新")

                    st.rerun()

                # 刪除按鈕
                if st.button("🗑️ 刪除任務", key=f"delete_{idx}"):

                    df = df.drop(idx)

                    conn.update(
                        worksheet="Tasks",
                        data=df
                    )

                    st.warning("任務已刪除")

                    st.rerun()

    else:
        st.info("目前沒有執行中任務")

# ==========================================
# Done
# ==========================================

with col3:

    st.markdown(
        "### <span style='color:green'>🟢 Done (已完成)</span>",
        unsafe_allow_html=True
    )

    done_list = df[df["status"] == "Done"]

    if not done_list.empty:

        for idx, row in done_list.iterrows():

            with st.container(border=True):

                st.write(f"### ~~{row['title']}~~")
                st.caption(f"👤 負責人：{row['owner']}")

                # 狀態切換
                new_status = st.selectbox(
                    "變更狀態",
                    ["To Do", "In Progress", "Done"],
                    index=["To Do", "In Progress", "Done"].index(row["status"]),
                    key=f"status_{idx}"
                )

                # 更新狀態
                if new_status != row["status"]:

                    df.at[idx, "status"] = new_status

                    conn.update(
                        worksheet="Tasks",
                        data=df
                    )

                    st.success("✅ 狀態已更新")

                    st.rerun()

                # 刪除按鈕
                if st.button("🗑️ 刪除任務", key=f"delete_{idx}"):

                    df = df.drop(idx)

                    conn.update(
                        worksheet="Tasks",
                        data=df
                    )

                    st.warning("任務已刪除")

                    st.rerun()

    else:
        st.info("目前沒有已完成任務")
