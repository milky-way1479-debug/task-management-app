import streamlit as st
import uuid
import base64

# ページ設定（ファイルを大きく見せるため wide モードに変更）
st.set_page_config(page_title="タスク管理アプリ v2", page_icon="📝", layout="wide")

# --- セッション状態の初期化 ---
if "app_title" not in st.session_state:
    st.session_state.app_title = "タスク管理アプリへようこそ"

if "categories" not in st.session_state:
    st.session_state.categories = []

if "trash" not in st.session_state:
    st.session_state.trash = []

# --- ユーティリティ関数 ---
def display_pdf(file_bytes):
    """PDFをBase64変換してiframeで表示"""
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 操作関数 ---
def add_category():
    st.session_state.categories.append({
        "id": str(uuid.uuid4()),
        "title": "新しい大見出し",
        "tasks": [],
        "file": None, # ファイル情報を保持
        "file_type": None
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
        if parent: parent["tasks"].append(trashed["item"])
        else: st.session_state.categories.append({"id": str(uuid.uuid4()), "title": "復元先(自動生成)", "tasks": [trashed["item"]], "file": None, "file_type": None})

def clear_trash():
    st.session_state.trash = []

# --- UI 描画 ---

# 1. アプリタイトル
st.session_state.app_title = st.text_input("アプリタイトル", value=st.session_state.app_title, label_visibility="collapsed")
st.divider()

# 2. メインコンテンツ
for cat_idx, category in enumerate(st.session_state.categories):
    with st.container(border=True):
        head_col1, head_col2, head_col3 = st.columns([6, 2, 1])
        
        with head_col1:
            category["title"] = st.text_input(f"Title_{category['id']}", value=category["title"], key=f"cat_t_{category['id']}", label_visibility="collapsed")
        
        with head_col2:
            st.button("＋ 中見出し", key=f"add_t_{category['id']}", on_click=add_task, args=(cat_idx,))
            
        with head_col3:
            st.button("✖", key=f"del_c_{category['id']}", on_click=delete_category, args=(cat_idx,))

        # --- ファイルアップロード＆表示エリア ---
        # 編集可能にするため、カラムで分割
        edit_col, view_col = st.columns([1, 2])
        
        with edit_col:
            st.write("📁 **資料の添付**")
            uploaded_file = st.file_uploader("PNG/PDFを選択", type=["png", "jpg", "pdf"], key=f"file_up_{category['id']}", label_visibility="collapsed")
            if uploaded_file:
                category["file"] = uploaded_file.read()
                category["file_type"] = uploaded_file.type
            
            if category["file"]:
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
                st.write("🧐 **資料プレビュー**")
                if category["file_type"] == "application/pdf":
                    display_pdf(category["file"])
                else:
                    st.image(category["file"], use_column_width=True)
            else:
                st.info("資料は添付されていません")

# 3. 追加ボタン
st.button("＋ 大見出しを追加", on_click=add_category, type="primary", use_container_width=True)

# 4. ゴミ箱
with st.expander(f"🗑️ ゴミ箱（{len(st.session_state.trash)} 件）"):
    if not st.session_state.trash:
        st.write("空です")
    else:
        st.button("ゴミ箱を空にする", on_click=clear_trash)
        for idx, item in enumerate(reversed(st.session_state.trash)):
            actual_idx = len(st.session_state.trash) - 1 - idx
            c1, c2 = st.columns([7, 2])
            c1.write(f"{'【大】' if item['type']=='category' else '【中】'} {item['item']['title']}")
            c2.button("復元", key=f"res_{idx}", on_click=restore_item, args=(actual_idx,))

