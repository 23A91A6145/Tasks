import streamlit as st
from pathlib import Path

from crew import content_marketing_crew
from utils.analytics import file_word_count


st.set_page_config(
    page_title="AI Content Studio",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Content Studio")

topic = st.text_input(
    "Topic",
    placeholder="AI Agents in Healthcare"
)

if st.button("Generate Content"):

    with st.spinner("Generating..."):

        content_marketing_crew.kickoff(
            inputs={
                "topic": topic
            }
        )

    st.success("Generation Complete")


research_file = Path(
    "outputs/research.md"
)

seo_file = Path(
    "outputs/seo.md"
)

blog_file = Path(
    "outputs/blog.md"
)

linkedin_file = Path(
    "outputs/linkedin.txt"
)

twitter_file = Path(
    "outputs/twitter.txt"
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Research",
        "SEO",
        "Blog",
        "LinkedIn",
        "Twitter"
    ]
)

with tab1:

    if research_file.exists():

        st.markdown(
            research_file.read_text(
                encoding="utf-8"
            )
        )

with tab2:

    if seo_file.exists():

        st.markdown(
            seo_file.read_text(
                encoding="utf-8"
            )
        )

with tab3:

    if blog_file.exists():

        st.markdown(
            blog_file.read_text(
                encoding="utf-8"
            )
        )

with tab4:

    if linkedin_file.exists():

        st.text(
            linkedin_file.read_text(
                encoding="utf-8"
            )
        )

with tab5:

    if twitter_file.exists():

        st.text(
            twitter_file.read_text(
                encoding="utf-8"
            )
        )

st.divider()

st.subheader("Analytics")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Research Words",
        file_word_count(
            "outputs/research.md"
        )
    )

with col2:

    st.metric(
        "Blog Words",
        file_word_count(
            "outputs/blog.md"
        )
    )

with col3:

    st.metric(
        "LinkedIn Words",
        file_word_count(
            "outputs/linkedin.txt"
        )
    )