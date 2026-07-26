import streamlit as st
import uuid
import base64

# ページ設定（wide モードで広い作業域を確保）
st.set_page_config(page_title="タスク管理アプリ v3", page_icon="📝", layout="wide")

# --- セッション状態の初期化 ---
if "app_title" not in st.session_state:
    st.session_state.app_title = "タスク管理アプリへようこそ"

if "categories" not in st.session_state:
    st.session_state.categories = []

if "trash" not in st.session_state:
    st.session_state.trash = []

# --- ユーティリティ関数 ---
def display_pdf(file_bytes, height=500):
    """PDFをBase64変換して指定された高さのiframeで表示"""
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="{height}" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 操作関数 ---
def add_category():
    st.session_state.categories.append({
        "id": str(uuid.uuid4()),
        "title": "新しい大見出し",
        "tasks": [],
        "file": None,
        "file_type": None,
        "file_height": 500  # デフォルトのプレビュー高さ(px)
    })

def delete_category(cat_index):
    deleted = st.session_state.categories.pop(cat_index)
    st.session_state.trash.append({"type": "category", "item": deleted, "parent_id": None})

def add_task(cat_index):
    st.session_state.categories[cat_index]["tasks"].append({"id": str(uuid.uuid4()), "title": "新しい中見出し"})

def delete_task(cat_index, task_index):
    category = st.session_state.categories[cat_index]
    deleted_task = category["tasks"].pop(task_index)
    st.session_state.trash.append({"type": "task", "item": deleted_task, "parent_id": category["id"]})

def restore_item(trash_index):
    trashed = st.session_state.trash.pop(trash_index)
    if trashed["type"] == "category":
        st.session_state.categories.append(trashed["item"])
    else:
        parent = next((c for c in st.session_state.categories if c["id"] == trashed["parent_id"]), None)
        if parent: 
            parent["tasks"].append(trashed["item"])
        else: 
            st.session_state.categories.append({
                "id": str(uuid.uuid4()), 
                "title": "復元先(自動生成)", 
                "tasks": [trashed["item"]], 
                "file": None, 
                "file_type": None,
                "file_height": 500
            })

def clear_trash():
    st.session_state.trash = []

# --- UI 描画 ---

# 1. アプリタイトル
st.session_state.app_title = st.text_input("アプリタイトル", value=st.session_state.app_title, label_visibility="collapsed")
st.divider()

# 2. メインコンテンツ
for cat_idx, category in enumerate(st.session_state.categories):
    # データ構造の互換性チェック（既存セッション対策）
    if "file_height" not in category:
        category["file_height"] = 500

    with st.container(border=True):
        head_col1, head_col2, head_col3 = st.columns([6, 2, 1])
        
        with head_col1:
            category["title"] = st.text_input(f"Title_{category['id']}", value=category["title"], key=f"cat_t_{category['id']}", label_visibility="collapsed")
        
        with head_col2:
            st.button("＋ 中見出し", key=f"add_t_{category['id']}", on_click=add_task, args=(cat_idx,))
            
        with head_col3:
            st.button("✖", key=f"del_c_{category['id']}", on_click=delete_category, args=(cat_idx,))

        # 2カラム構成（左：設定・タスク、右：プレビュー）
        edit_col, view_col = st.columns([1, 2])
        
        with edit_col:
            st.write("📁 **資料の添付**")
            uploaded_file = st.file_uploader("PNG/PDFを選択", type=["png", "jpg", "pdf"], key=f"file_up_{category['id']}", label_visibility="collapsed")
            if uploaded_file:
                category["file"] = uploaded_file.read()
                category["file_type"] = uploaded_file.type
            
            if category["file"]:
                # --- 表示サイズ変更スライダー ---
                category["file_height"] = st.slider(
                    "🔍 プレビューサイズ（高さpx）",
                    min_value=200,
                    max_value=1000,
                    value=category["file_height"],
                    step=50,
                    key=f"size_slider_{category['id']}"
                )

                if st.button("添付ファイルを消去", key=f"clear_f_{category['id']}"):
                    category["file"] = None
                    category["file_type"] = None
                    st.rerun()

            st.write("📝 **タスク一覧**")
            for task_idx, task in enumerate(category["tasks"]):
                t_c1, t_c2 = st.columns([8, 1])
                with t_c1:
                    task["title"] = st.text_input(f"Task_{task['id']}", value=task["title"], key=f"task_t_{task['id']}", label_visibility="collapsed")
                with t_c2:
                    st.button("🗑️", key=f"del_t_{task['id']}", on_click=delete_task, args=(cat_idx, task_idx))

        with view_col:
            if category["file"]:
                st.write(f"🧐 **資料プレビュー** (高さ: {category['file_height']}px)")
                if category["file_type"] == "application/pdf":
                    display_pdf(category["file"], height=category["file_height"])
                else:
                    # スライダーの高さに合わせてコンテナ枠を調整
                    with st.container(height=category["file_height"], border=False):
                        st.image(category["file"], use_container_width=True)
            else:
                st.info("資料は添付されていません")

# 3. 大見出し追加ボタン
st.button("＋ 大見出しを追加", on_click=add_category, type="primary", use_container_width=True)

# 4. ゴミ箱（削除履歴）
with st.expander(f"🗑️ ゴミ箱（{len(st.session_state.trash)} 件）"):
    if not st.session_state.trash:
        st.write("ゴミ箱は空です。")
    else:
        st.button("ゴミ箱を空にする", on_click=clear_trash)
        for idx, item in enumerate(reversed(st.session_state.trash)):
            actual_idx = len(st.session_state.trash) - 1 - idx
            c1, c2 = st.columns([7, 2])
            c1.write(f"{'【大見出し】' if item['type']=='category' else '【中見出し】'} {item['item']['title']}")
            c2.button("復元", key=f"res_{idx}", on_click=restore_item, args=(actual_idx,))
