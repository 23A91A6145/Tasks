import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


PDF_FOLDER = "exports/pdfs"


def generate_pdf(topic, report):

    # Create folder if missing
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)

    safe_topic = "".join(
        c for c in topic
        if c.isalnum() or c in (" ", "_", "-")
    )

    filename = (
        safe_topic.replace(" ", "_")
        + ".pdf"
    )

    filepath = os.path.join(
        PDF_FOLDER,
        filename
    )

    document = SimpleDocTemplate(
        filepath
    )

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        topic,
        styles["Title"]
    )

    content.append(title)

    content.append(
        Spacer(1, 20)
    )

    report_text = report.replace(
        "\n",
        "<br/>"
    )

    body = Paragraph(
        report_text,
        styles["BodyText"]
    )

    content.append(body)

    document.build(content)

    return filepath