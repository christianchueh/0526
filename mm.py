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

st.title("📋 Trello 雲端任務管理系統")
st.caption("edit by 闕河正 | Ultimate CRUD Version")

# ==========================================
# Google Sheets 連線
# ==========================================

conn = st.connection(
    "gsheets",
    type=GSheetsConnection
)

df = conn.read(
    worksheet="Tasks",
    ttl=0
)

# 若試算表為空
if df.empty:
    df = pd.DataFrame(
        columns=["title", "status", "owner"]
    )

# ==========================================
# 新增任務區塊
# ==========================================

st.write("## ✨ 新增任務")

with st.form("task_form", clear_on_submit=True):

    c1, c2, c3 = st.columns([2, 1, 1])

    with c1:
        new_title = st.text_input(
            "📌 任務名稱",
            placeholder="輸入任務名稱..."
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

    submit_btn = st.form_submit_button("✅ 新增任務")

# ==========================================
# 新增任務邏輯
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

        st.success("🎉 任務已成功新增！")

        st.rerun()

    else:
        st.warning("⚠️ 任務名稱與負責人不可空白")

st.divider()

# ==========================================
# 統計區塊
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
# 卡片渲染函式
# ==========================================

def render_cards(task_df):

    if task_df.empty:
        st.info("目前沒有任務")
        return

    for idx, row in task_df.iterrows():

        with st.container(border=True):

            # ==========================
            # 卡片標題
            # ==========================

            if row["status"] == "Done":
                st.write(f"### ~~{row['title']}~~")
            else:
                st.write(f"### {row['title']}")

            st.caption(f"👤 負責人：{row['owner']}")
            st.caption(f"📌 狀態：{row['status']}")

            # ==========================
            # 快速狀態切換
            # ==========================

            status_options = [
                "To Do",
                "In Progress",
                "Done"
            ]

            new_status = st.selectbox(
                "變更狀態",
                status_options,
                index=status_options.index(row["status"]),
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

            # ==========================
            # 操作按鈕列
            # ==========================

            btn_col1, btn_col2 = st.columns(2)

            # ==========================
            # 編輯任務
            # ==========================

            with btn_col1:

                with st.popover("✏️ 編輯任務"):

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
                        status_options,
                        index=status_options.index(row["status"]),
                        key=f"edit_status_{idx}"
                    )

                    # 儲存修改
                    if st.button(
                        "💾 儲存修改",
                        key=f"save_{idx}",
                        use_container_width=True
                    ):

                        df.at[idx, "title"] = edit_title
                        df.at[idx, "owner"] = edit_owner
                        df.at[idx, "status"] = edit_status

                        conn.update(
                            worksheet="Tasks",
                            data=df
                        )

                        st.success("✅ 任務已更新")

                        st.rerun()

            # ==========================
            # 刪除任務
            # ==========================

            with btn_col2:

                if st.button(
                    "🗑️ 刪除任務",
                    key=f"delete_{idx}",
                    use_container_width=True
                ):

                    df = df.drop(idx)

                    conn.update(
                        worksheet="Tasks",
                        data=df
                    )

                    st.warning("⚠️ 任務已刪除")

                    st.rerun()

# ==========================================
# Trello 三欄
# ==========================================

st.write("## 📊 Trello 任務看板")

col1, col2, col3 = st.columns(3)

# ==========================================
# To Do
# ==========================================

with col1:

    st.markdown(
        """
        ### <span style='color:red'>
        🔴 To Do（待辦）
        </span>
        """,
        unsafe_allow_html=True
    )

    todo_df = df[df["status"] == "To Do"]

    render_cards(todo_df)

# ==========================================
# In Progress
# ==========================================

with col2:

    st.markdown(
        """
        ### <span style='color:orange'>
        🟠 In Progress（執行中）
        </span>
        """,
        unsafe_allow_html=True
    )

    ip_df = df[df["status"] == "In Progress"]

    render_cards(ip_df)

# ==========================================
# Done
# ==========================================

with col3:

    st.markdown(
        """
        ### <span style='color:green'>
        🟢 Done（已完成）
        </span>
        """,
        unsafe_allow_html=True
    )

    done_df = df[df["status"] == "Done"]

    render_cards(done_df)
