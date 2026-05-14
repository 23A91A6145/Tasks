import os
import streamlit as st
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

# Load environment variables
load_dotenv()

# Create Cerebras client
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

# Page title
st.set_page_config(
    page_title="Cerebras AI Chat",
    page_icon="⚡",
    layout="wide"
)

# App title
st.title("⚡ Cerebras Ultra-Fast Chat")

# Sidebar settings
st.sidebar.header("Settings")

# Model selector
model = st.sidebar.selectbox(
    "Choose Model",
    [
        "llama3.1-8b",
        "llama3.3-70b"
    ]
)

# Temperature slider
temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.5,
    value=0.7,
    step=0.1
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear chat button
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Display chat history
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
prompt = st.chat_input("Message Cerebras...")

if prompt:

    # Store user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Assistant response
    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        full_response = ""

        # Streaming response
        stream = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            max_tokens=1024,
            temperature=temperature,
            stream=True
        )

        # Stream tokens
        for chunk in stream:

            if chunk.choices[0].delta.content:

                token = chunk.choices[0].delta.content

                full_response += token

                response_placeholder.markdown(full_response)

        # Save assistant message
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response
            }
        )

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.info(
    f"Messages Stored: {len(st.session_state.messages)}"
)