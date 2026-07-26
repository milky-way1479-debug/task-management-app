import streamlit as st

# タイトル表示
st.title("🎉 テストアプリへようこそ！")

# メッセージ表示
st.write("StreamlitとGitHubの連携テストが成功しました。")

# ボタンの動作テスト
if st.button("ここをクリック"):
    st.balloons()
    st.success("正常に動作しています！")
