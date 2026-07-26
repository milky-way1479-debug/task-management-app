import streamlit as st
import pandas as pd

# ページの設定（タイトルやレイアウト）
st.set_page_config(page_title="タスク管理アプリ", layout="wide")

st.title("📋 タスク管理アプリ")

# データを一時保存するスペースの準備
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- ① タスク追加フォーム ---
st.subheader("➕ 新規タスクの追加")
with st.form("add_task_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("プロダクト名", placeholder="例: プロダクトA")
    with col2:
        member = st.text_input("担当メンバー", placeholder="例: 山田")
    
    task_content = st.text_input("タスク内容", placeholder="例: 仕様書の確認")
    status = st.selectbox("ステータス", ["未着手", "進行中", "完了"])
    
    submitted = st.form_submit_button("タスクを追加")
    
    if submitted:
        if not task_content:
            st.error("⚠️ タスク内容を入力してください")
        else:
            st.session_state.tasks.append({
                "プロダクト名": product if product else "未設定",
                "担当メンバー": member if member else "未設定",
                "タスク内容": task_content,
                "ステータス": status
            })
            st.success("✅ タスクを追加しました！")

st.divider()

# --- ② タスク一覧・絞り込み表示 ---
st.subheader("📌 タスク一覧")

if not st.session_state.tasks:
    st.info("登録されているタスクはまだありません。上のフォームから追加してください。")
else:
    df = pd.DataFrame(st.session_state.tasks)
    
    # 絞り込み用ドロップダウン
    col_filter1, col_filter2 = st.columns(2)
    
    all_products = ["すべて"] + list(df["プロダクト名"].unique())
    all_members = ["すべて"] + list(df["担当メンバー"].unique())
    
    with col_filter1:
        selected_product = st.selectbox("🔍 プロダクトで絞り込み", all_products)
    with col_filter2:
        selected_member = st.selectbox("🔍 メンバーで絞り込み", all_members)
    
    # データの抽出処理
    filtered_df = df.copy()
    if selected_product != "すべて":
        filtered_df = filtered_df[filtered_df["プロダクト名"] == selected_product]
    if selected_member != "すべて":
        filtered_df = filtered_df[filtered_df["担当メンバー"] == selected_member]
    
    # 一覧テーブルの表示
    st.dataframe(filtered_df, use_container_width=True)
