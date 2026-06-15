import streamlit as st

from datetime import datetime

from agent.chains import run_review

from utils.file_handler import (
    save_uploaded_file
)

from utils.report_generator import (
    generate_reports
)

from utils.database import (
    init_db,
    save_review,
    get_reviews
)

# ----------------------------------
# DATABASE INIT
# ----------------------------------

init_db()

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="Code Review Agent",
    layout="wide"
)

# ----------------------------------
# HEADER
# ----------------------------------

st.title("🤖 Code Review Agent")

st.write(
    "Upload a Python file and get a complete AI-powered code review."
)

# ----------------------------------
# FILE UPLOAD
# ----------------------------------

uploaded_file = st.file_uploader(
    "Upload Python File",
    type=["py"]
)

# ----------------------------------
# FILE INFO
# ----------------------------------

if uploaded_file:

    st.info(
        f"""
Filename: {uploaded_file.name}

Size: {uploaded_file.size} bytes
"""
    )

    # Save uploaded file

    saved_path = save_uploaded_file(
        uploaded_file
    )

    # Read file content

    code = uploaded_file.getvalue().decode(
        "utf-8"
    )

    # ------------------------------
    # REVIEW BUTTON
    # ------------------------------

    if st.button("Review Code"):

        with st.spinner(
            "Analyzing code..."
        ):

            (
                review,
                ast_data,
                pylint_data,
                flake8_data,
                bandit_data,
                complexity_data
            ) = run_review(code)

        # ------------------------------
        # AST
        # ------------------------------

        st.subheader(
            "Code Structure"
        )

        st.json(ast_data)

        # ------------------------------
        # PYLINT
        # ------------------------------

        st.subheader(
            "Pylint Findings"
        )

        st.code(
            pylint_data,
            language="text"
        )

        # ------------------------------
        # FLAKE8
        # ------------------------------

        st.subheader(
            "Flake8 Findings"
        )

        st.code(
            flake8_data,
            language="text"
        )

        # ------------------------------
        # BANDIT
        # ------------------------------

        st.subheader(
            "Security Findings"
        )

        st.code(
            bandit_data,
            language="text"
        )

        # ------------------------------
        # COMPLEXITY
        # ------------------------------

        st.subheader(
            "Complexity Analysis"
        )

        st.json(
            complexity_data
        )

        # ------------------------------
        # REVIEW
        # ------------------------------

        st.subheader(
            "Review Report"
        )

        st.write(
            review
        )

        # ------------------------------
        # GENERATE REPORTS
        # ------------------------------

        md_file, html_file = generate_reports(
            review,
            ast_data,
            complexity_data
        )

        # ------------------------------
        # SAVE TO DATABASE
        # ------------------------------

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        save_review(
            timestamp=timestamp,
            filename=uploaded_file.name,
            review=review,
            risk_level=complexity_data.get(
                "risk_level",
                "UNKNOWN"
            ),
            complexity=complexity_data.get(
                "total_complexity",
                0
            ),
            maintainability=complexity_data.get(
                "maintainability",
                0
            )
        )

        # ------------------------------
        # DOWNLOADS
        # ------------------------------

        st.subheader(
            "Download Reports"
        )

        with open(
            md_file,
            "rb"
        ) as f:

            st.download_button(
                label="📄 Download Markdown Report",
                data=f,
                file_name=md_file.split("\\")[-1],
                mime="text/markdown"
            )

        with open(
            html_file,
            "rb"
        ) as f:

            st.download_button(
                label="🌐 Download HTML Report",
                data=f,
                file_name=html_file.split("\\")[-1],
                mime="text/html"
            )

        st.success(
            "Reports generated successfully."
        )

        st.info(
            f"""
Markdown Report:
{md_file}

HTML Report:
{html_file}
"""
        )

# ----------------------------------
# DASHBOARD
# ----------------------------------

st.divider()

st.header(
    "Statistics"
)

reviews = get_reviews()

st.metric(
    "Total Reviews",
    len(reviews)
)

# ----------------------------------
# REVIEW HISTORY
# ----------------------------------

st.header(
    "Review History"
)

reviews = get_reviews()

if reviews:

    for row in reviews:

        review_id = row[0]

        timestamp = (
            row[1]
            if len(row) > 1
            else "Unknown"
        )

        filename = (
            row[2]
            if len(row) > 2
            else "Unknown File"
        )

        review_text = (
            row[3]
            if len(row) > 3
            else ""
        )

        risk_level = (
            row[4]
            if len(row) > 4
            else "UNKNOWN"
        )

        complexity = (
            row[5]
            if len(row) > 5
            else 0
        )

        maintainability = (
            row[6]
            if len(row) > 6
            else 0
        )

        with st.expander(
            f"Review #{review_id} | {filename} | {timestamp}"
        ):

            st.write(review_text)

            st.caption(
                f"""
Risk Level: {risk_level}

Complexity: {complexity}

Maintainability: {maintainability}
"""
            )

else:

    st.info(
        "No reviews stored yet."
    )