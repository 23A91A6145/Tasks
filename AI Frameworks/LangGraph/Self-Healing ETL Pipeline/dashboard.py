import sys
from pathlib import Path

# =====================================================
# PROJECT ROOT FIX
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# =====================================================
# IMPORTS
# =====================================================

import json
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

from graph.workflow import workflow

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="ETLGuardian-AI",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# HEADER
# =====================================================

st.title("🤖 ETLGuardian-AI Dashboard")

st.caption(
    "Self-Healing ETL Pipeline | LangGraph | SQLite | Ollama"
)

st.divider()

# =====================================================
# RUN PIPELINE
# =====================================================

st.header("⚙️ Pipeline Control")

if st.button(
    "▶ Run ETL Workflow",
    use_container_width=True
):

    with st.spinner(
        "Running Workflow..."
    ):

        result = workflow.invoke({

            "data": None,

            "validation_report": {},

            "status": "",

            "start_time": datetime.now(),

            "end_time": None,

            "metrics": {},

            "analysis": "",

            "quality_score": 0
        })

    st.success(
        "Workflow Completed Successfully"
    )

    st.json(
        result["metrics"]
    )

st.divider()

# =====================================================
# EXECUTION METRICS
# =====================================================

st.header("📊 Execution Metrics")

metrics_file = Path(
    "reports/metrics.json"
)

if metrics_file.exists():

    with open(
        metrics_file,
        "r",
        encoding="utf-8"
    ) as f:

        metrics = json.load(f)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Rows",
            metrics.get(
                "rows",
                0
            )
        )

    with col2:
        st.metric(
            "Columns",
            metrics.get(
                "columns",
                0
            )
        )

    with col3:
        st.metric(
            "Status",
            metrics.get(
                "status",
                "N/A"
            )
        )

    st.json(metrics)

else:

    st.warning(
        "No metrics found."
    )

st.divider()

# =====================================================
# DATA QUALITY SCORE
# =====================================================

st.header("📈 Data Quality Score")

quality_file = Path(
    "reports/quality_history.json"
)

if quality_file.exists():

    with open(
        quality_file,
        "r",
        encoding="utf-8"
    ) as f:

        history = json.load(f)

    latest = history[-1]

    score = latest.get(
        "quality_score",
        0
    )

    st.metric(
        "Quality Score",
        f"{score}%"
    )

else:

    st.info(
        "No quality score available."
    )

st.divider()

# =====================================================
# QUALITY HISTORY
# =====================================================

st.header("📋 Quality History")

if quality_file.exists():

    history_df = pd.DataFrame(
        history
    )

    st.dataframe(
        history_df,
        use_container_width=True
    )

else:

    st.info(
        "No quality history available."
    )

st.divider()

# =====================================================
# AI ANALYSIS
# =====================================================

st.header("🧠 AI Analysis")

analysis_file = Path(
    "reports/ai_analysis.txt"
)

if analysis_file.exists():

    analysis = analysis_file.read_text(
        encoding="utf-8"
    )

    st.text_area(
        "AI Insights",
        analysis,
        height=350
    )

else:

    st.info(
        "No AI analysis report available."
    )

st.divider()

# =====================================================
# DATABASE RECORDS
# =====================================================

st.header("🗄 Database Records")

db_path = Path(
    "database/etl.db"
)

if db_path.exists():

    try:

        conn = sqlite3.connect(
            db_path
        )

        df = pd.read_sql(
            "SELECT * FROM iris_data",
            conn
        )

        conn.close()

        st.success(
            f"{len(df)} rows loaded from database"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Database Error: {e}"
        )

else:

    st.warning(
        "Database not found."
    )

st.divider()

# =====================================================
# EXECUTION REPORT
# =====================================================

st.header("📄 Execution Report")

report_file = Path(
    "reports/execution_report.txt"
)

if report_file.exists():

    report_text = report_file.read_text(
        encoding="utf-8"
    )

    st.text_area(
        "Execution Report",
        report_text,
        height=250
    )

else:

    st.info(
        "No execution report available."
    )

st.divider()

# =====================================================
# PIPELINE LOGS
# =====================================================

st.header("📜 Pipeline Logs")

log_file = Path(
    "logs/pipeline.log"
)

if log_file.exists():

    logs = log_file.read_text(
        encoding="utf-8"
    )

    st.text_area(
        "Logs",
        logs,
        height=350
    )

else:

    st.info(
        "No logs found."
    )

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.caption(
    "ETLGuardian-AI | Phase 11 | LangGraph + SQLite + Ollama + Streamlit"
)