import streamlit as st

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Study Buddy AI")

topic = st.text_input(
    "Enter Topic"
)

col1,col2,col3,col4 = st.columns(4)

study_btn = col1.button("Study")

notes_btn = col2.button("Notes")

quiz_btn = col3.button("Quiz")

roadmap_btn = col4.button("Roadmap")