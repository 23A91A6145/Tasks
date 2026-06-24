import streamlit as st
import pandas as pd

from crews.validator_crew import create_validator_crew

from reports.report_generator import (
    save_txt_report,
    save_json_report
)

from database.db import (
    init_db,
    save_validation,
    get_all_validations,
    get_top_startups
)

from analytics.scoring import calculate_scores

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Startup Validator Crew",
    page_icon="🚀",
    layout="wide"
)

init_db()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

with st.sidebar:

    st.title("🚀 Startup Validator")

    st.markdown("---")

    st.subheader("Project")

    st.write("CrewAI")
    st.write("Ollama")
    st.write("llama3.2:3b")

    st.markdown("---")

    st.subheader("Status")

    st.success("Local AI Active")

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("🚀 Startup Validator Crew")

st.caption(
    "Validate startup ideas using CrewAI + Ollama + Multi-Agent Analysis"
)

# -------------------------------------------------
# INPUT SECTION
# -------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    business_type = st.selectbox(
        "Business Category",
        [
            "SaaS",
            "Education",
            "Healthcare",
            "Finance",
            "E-Commerce",
            "Productivity",
            "Other"
        ]
    )

with col2:

    audience = st.selectbox(
        "Target Audience",
        [
            "Students",
            "Developers",
            "Businesses",
            "Consumers",
            "Professionals"
        ]
    )

startup_idea = st.text_area(
    "Startup Idea",
    height=150
)

# -------------------------------------------------
# VALIDATION
# -------------------------------------------------

if st.button(
    "🚀 Validate Startup",
    use_container_width=True
):

    if not startup_idea.strip():

        st.warning(
            "Please enter a startup idea."
        )

    else:

        prompt = f"""
        Startup Idea:
        {startup_idea}

        Business Type:
        {business_type}

        Audience:
        {audience}
        """

        with st.spinner(
            "Running AI Validation..."
        ):

            crew = create_validator_crew(
                prompt
            )

            result = crew.kickoff()

            save_txt_report(result)

            save_json_report(result)

            save_validation(
                startup_idea,
                business_type,
                audience,
                result
            )

            scores = calculate_scores(
                result
            )

        st.success(
            "Validation Complete"
        )

        # -----------------------------
        # SCORE CARDS
        # -----------------------------

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Demand",
            f"{scores['demand']}/10"
        )

        c2.metric(
            "Revenue",
            f"{scores['revenue']}/10"
        )

        c3.metric(
            "Risk",
            f"{scores['risk']}/10"
        )

        c4.metric(
            "Overall",
            f"{scores['overall']}/10"
        )

        # -----------------------------
        # CHART
        # -----------------------------

        chart_df = pd.DataFrame({
            "Metric": [
                "Demand",
                "Revenue",
                "Risk"
            ],
            "Score": [
                scores["demand"],
                scores["revenue"],
                scores["risk"]
            ]
        })

        st.bar_chart(
            chart_df.set_index(
                "Metric"
            )
        )

        # -----------------------------
        # REPORT
        # -----------------------------

        st.markdown("---")

        st.subheader(
            "📊 Validation Report"
        )

        st.markdown(
            str(result)
        )

# -------------------------------------------------
# COMPARISON
# -------------------------------------------------

st.markdown("---")

st.header("⚔ Startup Comparison")

idea_a = st.text_input(
    "Startup A",
    placeholder="AI Admin Assistant"
)

idea_b = st.text_input(
    "Startup B",
    placeholder="AI Content Creator"
)

if st.button("Compare Startups"):

    if not idea_a or not idea_b:

        st.warning(
            "Please enter both startup ideas."
        )

    else:

        with st.spinner(
            "Analyzing both startups..."
        ):

            crew_a = create_validator_crew(
                idea_a
            )

            report_a = crew_a.kickoff()

            crew_b = create_validator_crew(
                idea_b
            )

            report_b = crew_b.kickoff()

            from analytics.comparator import compare_startups

            comparison = compare_startups(
                report_a,
                report_b
            )

        st.success(
            "Comparison Completed"
        )

        st.subheader("Startup A")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Demand",
            comparison["startup_a"]["demand"]
        )

        col2.metric(
            "Revenue",
            comparison["startup_a"]["revenue"]
        )

        col3.metric(
            "Risk",
            comparison["startup_a"]["risk"]
        )

        col4.metric(
            "Overall",
            comparison["startup_a"]["overall"]
        )

        st.markdown("---")

        st.subheader("Startup B")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Demand",
            comparison["startup_b"]["demand"]
        )

        col2.metric(
            "Revenue",
            comparison["startup_b"]["revenue"]
        )

        col3.metric(
            "Risk",
            comparison["startup_b"]["risk"]
        )

        col4.metric(
            "Overall",
            comparison["startup_b"]["overall"]
        )

        st.markdown("---")

        st.subheader("🏆 Winner")

        st.success(
            comparison["winner"]
        )

        st.markdown("---")

        cdf = pd.DataFrame({

            "Metric": [
                "Demand",
                "Revenue",
                "Risk",
                "Overall"
            ],

            "Startup A": [
                comparison["startup_a"]["demand"],
                comparison["startup_a"]["revenue"],
                comparison["startup_a"]["risk"],
                comparison["startup_a"]["overall"]
            ],

            "Startup B": [
                comparison["startup_b"]["demand"],
                comparison["startup_b"]["revenue"],
                comparison["startup_b"]["risk"],
                comparison["startup_b"]["overall"]
            ]
        })

        st.bar_chart(
            cdf.set_index("Metric")
        )

# -------------------------------------------------
# LEADERBOARD
# -------------------------------------------------

st.markdown("---")

st.subheader(
    "🏆 Startup Leaderboard"
)

top_startups = get_top_startups()

if top_startups:

    for item in top_startups:

        st.write(
            f"🚀 {item[0]}"
        )

# -------------------------------------------------
# HISTORY
# -------------------------------------------------

st.markdown("---")

st.subheader(
    "📜 Validation History"
)

history = get_all_validations()

if history:

    for row in history:

        with st.expander(
            f"{row[1]} | {row[5]}"
        ):

            st.write(
                f"Category: {row[2]}"
            )

            st.write(
                f"Audience: {row[3]}"
            )

            st.markdown(
                row[4]
            )