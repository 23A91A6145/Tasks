import streamlit as st

from chains.tone_chain import tone_chain
from chains.email_chain import email_chain
from chains.reply_chain import reply_chain

from utils.storage import (
    save_email,
    load_history,
    clear_history
)


st.set_page_config(
    page_title="Email Drafter Agent",
    page_icon="📧",
    layout="wide"
)


def main():

    # =====================================
    # SIDEBAR
    # =====================================

    st.sidebar.title("📜 Email History")

    history = load_history()

    st.sidebar.metric(
        "Total Emails",
        len(history)
    )

    st.sidebar.divider()

    if history:

        for item in reversed(history):

            with st.sidebar.expander(
                item["subject"]
            ):

                st.write(
                    f"**Recipient:** {item['recipient']}"
                )

                st.write(
                    f"**Tone:** {item['tone']}"
                )

                st.write(
                    f"**Date:** {item['timestamp']}"
                )

                st.write(item["body"])

    else:

        st.sidebar.info(
            "No email history found."
        )

    st.sidebar.divider()

    if st.sidebar.button(
        "🗑 Clear History",
        use_container_width=True
    ):

        clear_history()

        st.rerun()

    # =====================================
    # MAIN TITLE
    # =====================================

    st.title("📧 AI Email Assistant")

    st.write(
        "Generate emails and reply to emails using AI."
    )

    # =====================================
    # TABS
    # =====================================

    tab1, tab2 = st.tabs(
        [
            "📧 Generate Email",
            "↩️ Reply To Email"
        ]
    )

    # =====================================
    # TAB 1
    # EMAIL GENERATOR
    # =====================================

    with tab1:

        st.subheader(
            "Generate Professional Emails"
        )

        purpose = st.text_input(
            "Purpose",
            placeholder="Example: Leave Request"
        )

        recipient = st.text_input(
            "Recipient",
            placeholder="Example: Manager"
        )

        details = st.text_area(
            "Details",
            placeholder="Explain what you want in the email",
            height=150
        )

        generate = st.button(
            "Generate Email",
            use_container_width=True,
            key="generate_email"
        )

        if generate:

            if (
                not purpose.strip()
                or not recipient.strip()
                or not details.strip()
            ):

                st.warning(
                    "Please fill all fields."
                )

            else:

                with st.spinner(
                    "Detecting Tone..."
                ):

                    tone_response = (
                        tone_chain.invoke(
                            {
                                "details": details
                            }
                        )
                    )

                    detected_tone = (
                        tone_response.content.strip()
                    )

                st.success(
                    f"Detected Tone: {detected_tone}"
                )

                with st.spinner(
                    "Generating Email Variations..."
                ):

                    email = email_chain.invoke(
                        {
                            "purpose": purpose,
                            "recipient": recipient,
                            "details": details,
                            "tone": detected_tone
                        }
                    )

                # Save Version A only
                save_email(
                    recipient=recipient,
                    tone=email.tone,
                    subject=email.email_a.subject,
                    body=email.email_a.body
                )

                st.info(
                    f"Final Tone: {email.tone}"
                )

                # =====================
                # VERSION A
                # =====================

                st.markdown("---")

                st.subheader(
                    "📧 Version A — Professional"
                )

                st.text_input(
                    "Subject A",
                    value=email.email_a.subject,
                    disabled=True,
                    key="subject_a"
                )

                st.text_area(
                    "Body A",
                    value=email.email_a.body,
                    height=250,
                    disabled=True,
                    key="body_a"
                )

                # =====================
                # VERSION B
                # =====================

                st.markdown("---")

                st.subheader(
                    "😊 Version B — Friendly"
                )

                st.text_input(
                    "Subject B",
                    value=email.email_b.subject,
                    disabled=True,
                    key="subject_b"
                )

                st.text_area(
                    "Body B",
                    value=email.email_b.body,
                    height=250,
                    disabled=True,
                    key="body_b"
                )

                # =====================
                # VERSION C
                # =====================

                st.markdown("---")

                st.subheader(
                    "⚡ Version C — Concise"
                )

                st.text_input(
                    "Subject C",
                    value=email.email_c.subject,
                    disabled=True,
                    key="subject_c"
                )

                st.text_area(
                    "Body C",
                    value=email.email_c.body,
                    height=250,
                    disabled=True,
                    key="body_c"
                )

                st.success(
                    "3 Email Variations Generated Successfully!"
                )

    # =====================================
    # TAB 2
    # REPLY GENERATOR
    # =====================================

    with tab2:

        st.subheader(
            "AI Reply Generator"
        )

        received_email = st.text_area(
            "Paste Received Email",
            height=250
        )

        generate_reply = st.button(
            "Generate Reply",
            use_container_width=True,
            key="generate_reply"
        )

        if generate_reply:

            if not received_email.strip():

                st.warning(
                    "Please paste an email first."
                )

            else:

                with st.spinner(
                    "Generating Reply..."
                ):

                    reply = reply_chain.invoke(
                        {
                            "received_email":
                            received_email
                        }
                    )

                st.success(
                    f"Detected Tone: {reply.tone}"
                )

                st.text_input(
                    "Reply Subject",
                    value=reply.subject,
                    disabled=True,
                    key="reply_subject"
                )

                st.text_area(
                    "Reply Email",
                    value=reply.reply,
                    height=300,
                    disabled=True,
                    key="reply_body"
                )


if __name__ == "__main__":
    main()