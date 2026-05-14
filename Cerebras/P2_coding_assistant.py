import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

# ======================================================
# LOAD ENV VARIABLES
# ======================================================

load_dotenv()

# ======================================================
# CREATE CEREBRAS CLIENT
# ======================================================

client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

# ======================================================
# WATCH FOLDER
# ======================================================

WATCH_FOLDER = r"D:\Tasks\Cerebras"

# ======================================================
# MODES
# ======================================================

MODE = "/fix"

PROMPTS = {

    "/fix": """
Review this code carefully.

Find:
- bugs
- syntax issues
- logic problems
- runtime errors

Explain fixes clearly.

Code:
""",

    "/explain": """
Explain this code simply for a beginner.

Include:
- what it does
- how it works
- important concepts

Code:
""",

    "/optimize": """
Optimize and improve this code.

Focus on:
- readability
- performance
- best practices

Code:
""",

    "/docstring": """
Write professional docstrings for this code.

Code:
"""
}

# ======================================================
# FILE WATCHER
# ======================================================

class CodeHandler(FileSystemEventHandler):

    def on_any_event(self, event):

        # Ignore folders
        if event.is_directory:
            return

        # Only process modified/created files
        if event.event_type not in ["modified", "created"]:
            return

        # Supported extensions
        valid_extensions = (
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp"
        )

        # Ignore unsupported files
        if not event.src_path.endswith(valid_extensions):
            return

        # Ignore unnecessary folders/files
        ignored = [
            "__pycache__",
            ".git",
            ".vscode",
            "venv"
        ]

        for item in ignored:

            if item in event.src_path:
                return

        print("\n" + "=" * 60)
        print("⚡ FILE DETECTED")
        print("=" * 60)

        print(f"\n📄 File: {event.src_path}")

        try:

            # Prevent duplicate instant triggers
            time.sleep(1)

            # Read file
            with open(
                event.src_path,
                "r",
                encoding="utf-8"
            ) as file:

                code = file.read()

            # Ignore empty files
            if not code.strip():

                print("⚠ Empty file.")
                return

            # Create prompt
            prompt = PROMPTS[MODE] + "\n\n" + code

            print(f"\n🛠 Mode: {MODE}")
            print("\n🤖 Cerebras Review:\n")

            # STREAM RESPONSE
            stream = client.chat.completions.create(
                model="llama3.1-8b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1200,
                temperature=0.3,
                stream=True
            )

            # Print streamed output
            for chunk in stream:

                if chunk.choices[0].delta.content:

                    token = chunk.choices[0].delta.content

                    print(token, end="", flush=True)

            print("\n")

        except Exception as e:

            print(f"\n❌ ERROR: {e}")

# ======================================================
# START OBSERVER
# ======================================================

observer = Observer()

handler = CodeHandler()

observer.schedule(
    handler,
    path=WATCH_FOLDER,
    recursive=False
)

observer.start()

# ======================================================
# START MESSAGE
# ======================================================

print("\n" + "=" * 60)
print("⚡ REAL-TIME AI CODING ASSISTANT")
print("=" * 60)

print(f"\n📂 Watching Folder:")
print(WATCH_FOLDER)

print(f"\n🛠 Active Mode:")
print(MODE)

print("\n📌 Supported Files:")
print(".py  .js  .ts  .java  .cpp")

print("\n🚀 Assistant is now running...")
print("💡 Edit and SAVE files to trigger AI review.")
print("\n🛑 Press CTRL + C to stop.\n")

# ======================================================
# KEEP RUNNING
# ======================================================

try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print("\n🛑 Assistant stopped.")

    observer.stop()

observer.join()