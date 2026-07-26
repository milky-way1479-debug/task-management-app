import streamlit as st
import uuid
import base64

# ページ設定
st.set_page_config(page_title="タスク管理アプリ", page_icon="📝", layout="wide")

# --- セッション状態の初期化 ---
if "app_title" not in st.session_state:
    st.session_state.app_title = "タスク管理アプリへようこそ"
if "categories" not in st.session_state:
    st.session_state.categories = []
if "trash" not in st.session_state:
    st.session_state.trash = []

# --- キャンバス・要素の操作関数 ---
def add_text_element(cat_idx):
    st.session_state.categories[cat_idx]["elements"].append({
        "id": str(uuid.uuid4()), "type": "text", "content": "新しいテキスト",
        "x": 50, "y": 50, "size": 24
    })

def delete_element(cat_idx, el_idx):
    st.session_state.categories[cat_idx]["elements"].pop(el_idx)

# --- 基本の操作関数 ---
def add_category():
    st.session_state.categories.append({
        "id": str(uuid.uuid4()), "title": "新しい大見出し", "tasks": [], "elements": [], "canvas_height": 500
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
    elif trashed["type"] == "task":
        parent = next((c for c in st.session_state.categories if c["id"] == trashed["parent_id"]), None)
        if parent:
            parent["tasks"].append(trashed["item"])
        else:
            # 親が見つからない場合は新しい大見出しを作成して中身を戻す
            st.session_state.categories.append({
                "id": str(uuid.uuid4()),
                "title": "復元されたタスクの親見出し",
                "tasks": [trashed["item"]],
                "elements": [],
                "canvas_height": 500
            })

def clear_trash():
    st.session_state.trash = []

# --- HTML/CSSでキャンバスを描画する関数 ---
def render_canvas(elements, height):
    html = f'<div style="position: relative; width: 100%; height: {height}px; background-color: #ffffff; border: 1px solid #ccc; border-radius: 8px; overflow: hidden; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">'
    
    for el in elements:
        if el["type"] == "text":
            html += f'<div style="position: absolute; left: {el["x"]}px; top: {el["y"]}px; font-size: {el["size"]}px; color: #333; font-weight: bold; white-space: pre-wrap; line-height: 1.2;">{el["content"]}</div>'
        elif el["type"] == "image":
            html += f'<img src="{el["content"]}" style="position: absolute; left: {el["x"]}px; top: {el["y"]}px; width: {el["size"]}px;">'
            
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# --- UI 描画 ---

# 1. アプリタイトル
st.session_state.app_title = st.text_input("アプリタイトル", value=st.session_state.app_title, label_visibility="collapsed")
st.divider()

# 2. メインコンテンツ
for cat_idx, category in enumerate(st.session_state.categories):
    # 互換性維持のための安全策
    if "elements" not in category: category["elements"] = []
    if "canvas_height" not in category: category["canvas_height"] = 500

    with st.container(border=True):
        head_col1, head_col2, head_col3 = st.columns([6, 2, 1])
        with head_col1:
            category["title"] = st.text_input(f"Title_{category['id']}", value=category["title"], key=f"cat_t_{category['id']}", label_visibility="collapsed")
        with head_col2:
            st.button("＋ 中見出し", key=f"add_t_{category['id']}", on_click=add_task, args=(cat_idx,))
        with head_col3:
            st.button("✖", key=f"del_c_{category['id']}", on_click=delete_category, args=(cat_idx,))

        edit_col, view_col = st.columns([1, 2])
        
        with edit_col:
            st.write("📝 **タスク一覧**")
            for task_idx, task in enumerate(category["tasks"]):
                t_c1, t_c2 = st.columns([8, 1])
                with t_c1:
                    task["title"] = st.text_input(f"Task_{task['id']}", value=task["title"], key=f"task_t_{task['id']}", label_visibility="collapsed")
                with t_c2:
                    st.button("🗑️", key=f"del_t_{task['id']}", on_click=delete_task, args=(cat_idx, task_idx))
            
            st.divider()
            
            st.write("🎨 **キャンバス要素の追加**")
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                st.button("＋ テキスト", key=f"add_txt_{category['id']}", on_click=add_text_element, args=(cat_idx,))
            with c_btn2:
                uploaded_img = st.file_uploader("画像(PNG/JPG)", type=["png", "jpg"], key=f"up_img_{category['id']}", label_visibility="collapsed")
                if uploaded_img:
                    data_uri = f"data:{uploaded_img.type};base64,{base64.b64encode(uploaded_img.read()).decode('utf-8')}"
                    category["elements"].append({
                        "id": str(uuid.uuid4()), "type": "image", "content": data_uri, "x": 50, "y": 50, "size": 300
                    })
                    st.rerun()

            if category["elements"]:
                st.write("📐 **配置・サイズ調整**")
                for el_idx, el in enumerate(category["elements"]):
                    with st.expander(f"{'テキスト' if el['type']=='text' else '画像'} (X:{el['x']}, Y:{el['y']})"):
                        if el["type"] == "text":
                            el["content"] = st.text_input("文字内容", el["content"], key=f"t_c_{el['id']}")
                            el["size"] = st.slider("文字サイズ", 10, 100, el["size"], key=f"t_s_{el['id']}")
                        elif el["type"] == "image":
                            el["size"] = st.slider("画像サイズ（幅）", 50, 1000, el["size"], key=f"i_s_{el['id']}")
                        
                        xy1, xy2 = st.columns(2)
                        el["x"] = xy1.number_input("右へ (X)", 0, 1500, el["x"], key=f"x_{el['id']}")
                        el["y"] = xy2.number_input("下へ (Y)", 0, 1500, el["y"], key=f"y_{el['id']}")
                        
                        st.button("削除", on_click=delete_element, args=(cat_idx, el_idx), key=f"del_el_{el['id']}")

            category["canvas_height"] = st.slider("キャンバスの縦幅", 300, 1500, category["canvas_height"], step=50, key=f"cvs_h_{category['id']}")

        with view_col:
            st.write("🧐 **ホワイトボード プレビュー**")
            render_canvas(category["elements"], category["canvas_height"])

# 3. 大見出し追加ボタン
st.button("＋ 大見出しを追加", on_click=add_category, type="primary", use_container_width=True)

# 4. ゴミ箱
with st.expander(f"🗑️ ゴミ箱（{len(st.session_state.trash)} 件）"):
    if not st.session_state.trash:
        st.write("ゴミ箱は空です。")
    else:
        st.button("ゴミ箱を空にする", on_click=clear_trash)
        for idx, item in enumerate(reversed(st.session_state.trash)):
            actual_idx = len(st.session_state.trash) - 1 - idx
            c1, c2 = st.columns([7, 2])
            item_name = item['item']['title'] if 'title' in item['item'] else item['item'].get('content', 'アイテム')
            c1.write(f"{'【大見出し】' if item['type']=='category' else '【中見出し】'} {item_name}")
            c2.button("復元", key=f"res_{idx}", on_click=restore_item, args=(actual_idx,))
