from pathlib import Path
from datetime import datetime


REPORT_DIR = Path(
    "reports/generated"
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def generate_reports(
    review,
    ast_data,
    complexity_data
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    md_file = (
        REPORT_DIR /
        f"review_{timestamp}.md"
    )

    html_file = (
        REPORT_DIR /
        f"review_{timestamp}.html"
    )

    markdown_content = f"""
# Code Review Report

Generated:
{timestamp}

---

## AST Analysis

{ast_data}

---

## Complexity

{complexity_data}

---

## Review

{review}
"""

    html_content = f"""
<html>
<head>
<title>Code Review Report</title>
</head>

<body>

<h1>Code Review Report</h1>

<p>{timestamp}</p>

<h2>AST Analysis</h2>

<pre>{ast_data}</pre>

<h2>Complexity</h2>

<pre>{complexity_data}</pre>

<h2>Review</h2>

<pre>{review}</pre>

</body>
</html>
"""

    md_file.write_text(
        markdown_content,
        encoding="utf-8"
    )

    html_file.write_text(
        html_content,
        encoding="utf-8"
    )

    return (
        str(md_file),
        str(html_file)
    )