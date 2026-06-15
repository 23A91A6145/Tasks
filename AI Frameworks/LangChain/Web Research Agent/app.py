import streamlit as st

from agents.researcher import run_agent

from database.db import (
    create_database,
    save_research,
    get_all_research,
    get_research_by_id
)

from exports.pdf_exporter import generate_pdf


# =====================================
# DATABASE INITIALIZATION
# =====================================

create_database()


# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Web Research Agent",
    page_icon="🔎",
    layout="wide"
)


# =====================================
# HEADER
# =====================================

st.title("🔎 Web Research Agent")

st.markdown(
    "Research any topic using DuckDuckGo, Wikipedia, and Llama 3.2"
)


# =====================================
# RESEARCH INPUT
# =====================================

query = st.text_input(
    "Enter Research Topic"
)


# =====================================
# RESEARCH BUTTON
# =====================================

if st.button("Research"):

    if query.strip():

        with st.spinner("Researching..."):

            report = run_agent(query)

            save_research(
                query,
                report
            )

            pdf_path = generate_pdf(
                query,
                report
            )

        st.success(
            "Research Completed & Saved"
        )

        st.markdown(report)

        # =============================
        # PDF DOWNLOAD BUTTON
        # =============================

        with open(pdf_path, "rb") as pdf_file:

            st.download_button(
                label="📄 Download PDF",
                data=pdf_file,
                file_name=f"{query}.pdf",
                mime="application/pdf"
            )

    else:

        st.warning(
            "Please enter a topic."
        )


# =====================================
# DIVIDER
# =====================================

st.divider()


# =====================================
# HISTORY SECTION
# =====================================

st.subheader("📚 Research History")

history = get_all_research()


# =====================================
# HISTORY BUTTONS
# =====================================

for item in history:

    research_id = item[0]
    topic = item[1]
    created_at = item[2]

    if st.button(
        f"{topic} ({created_at})",
        key=f"history_{research_id}"
    ):

        report_data = get_research_by_id(
            research_id
        )

        if report_data:

            report = report_data[0]

            st.markdown(report)

            pdf_path = generate_pdf(
                topic,
                report
            )

            with open(pdf_path, "rb") as pdf_file:

                st.download_button(
                    label=f"📄 Download {topic} PDF",
                    data=pdf_file,
                    file_name=f"{topic}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{research_id}"
                )