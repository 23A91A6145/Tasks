"""
ultimate_chatbot.py
═══════════════════════════════════════════════════════════
🔥 FIREWORKS AI — ULTIMATE CHATBOT
All 7 modes in one program. No GPU needed.
Model: accounts/fireworks/models/kimi-k2p5

MODES:
  1. Streaming Chatbot   — words appear in real-time
  2. Voice Chatbot       — speak & hear responses
  3. PDF Chatbot         — chat with any PDF
  4. Memory Database     — remembers across sessions
  5. Web UI Chatbot      — browser interface
  6. AI Agent            — multi-step tool use
  7. RAG Chatbot         — retrieval-augmented generation
═══════════════════════════════════════════════════════════
"""

import os, sys, json, re, datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════
MODEL   = "accounts/fireworks/models/kimi-k2p5"
API_KEY = os.getenv("FIREWORKS_API_KEY")

PERSONA = """
You are Spark — a smart, friendly AI assistant.
You are concise, helpful, and slightly witty.
Always answer clearly. If you don't know, say so.
"""

Path("memory").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)
Path("pdfs").mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════
# FIREWORKS CLIENT
# ═══════════════════════════════════════════════════════════
from fireworks.client import Fireworks
client = Fireworks(api_key=API_KEY)

# ═══════════════════════════════════════════════════════════
# UTILS
# ═══════════════════════════════════════════════════════════
def divider(char="═", n=54):
    print(char * n)

def header(title):
    divider()
    print(f"  🔥  {title}")
    divider()
    print()

def save_chat(history: list, mode: str):
    """Save conversation to outputs/ as JSON."""
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path("outputs") / f"{mode}_{ts}.json"
    path.write_text(json.dumps(history, indent=2, ensure_ascii=False))
    print(f"\n  💾 Chat saved → {path}")

# ═══════════════════════════════════════════════════════════
# MODE 1 — STREAMING CHATBOT
# ═══════════════════════════════════════════════════════════
def mode_streaming():
    header("MODE 1 — STREAMING CHATBOT")
    print("  Words appear in real-time as AI generates them.")
    print("  Commands: 'clear' 'save' 'quit'\n")

    history = [{"role": "system", "content": PERSONA}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "clear":
            history = [history[0]]
            print("  🗑️  History cleared.\n")
            continue
        if user_input.lower() == "save":
            save_chat(history, "streaming")
            continue

        history.append({"role": "user", "content": user_input})

        # ── STREAM ──
        print("\n🔥 Spark: ", end="", flush=True)
        full_reply = ""

        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=history,
                max_tokens=600,
                temperature=0.7,
                stream=True          # ← KEY: streaming enabled
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                print(delta, end="", flush=True)
                full_reply += delta
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

        print("\n")
        history.append({"role": "assistant", "content": full_reply})


# ═══════════════════════════════════════════════════════════
# MODE 2 — VOICE CHATBOT
# ═══════════════════════════════════════════════════════════
def mode_voice():
    header("MODE 2 — VOICE CHATBOT")

    # Lazy imports so missing libs don't break other modes
    try:
        import speech_recognition as sr
        import pyttsx3
    except ImportError:
        print("  ❌ Install required: pip install SpeechRecognition pyttsx3 pyaudio")
        return

    recognizer = sr.Recognizer()
    engine     = pyttsx3.init()

    # Voice settings (works on low-end laptops)
    engine.setProperty("rate",   160)   # words per minute
    engine.setProperty("volume", 0.9)

    # Pick a voice (index 0 = default; try 1 for female on Windows)
    voices = engine.getProperty("voices")
    if len(voices) > 1:
        engine.setProperty("voice", voices[1].id)  # female
    else:
        engine.setProperty("voice", voices[0].id)

    history = [{"role": "system", "content": PERSONA}]

    print("  🎙️  Say something — or say 'quit' to exit.\n")

    def speak(text: str):
        """Text-to-speech."""
        # Strip markdown so it reads naturally
        clean = re.sub(r"[*_`#]", "", text)
        engine.say(clean)
        engine.runAndWait()

    def listen() -> str | None:
        """Listen from mic, return transcript or None."""
        with sr.Microphone() as source:
            print("  🎙️  Listening …", end="", flush=True)
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
                text  = recognizer.recognize_google(audio)
                print(f"\r  🎙️  You said: {text}")
                return text
            except sr.WaitTimeoutError:
                print("\r  ⏱️  No speech detected.")
                return None
            except sr.UnknownValueError:
                print("\r  ❓ Could not understand.")
                return None
            except sr.RequestError as e:
                print(f"\r  ❌ Recognition error: {e}")
                return None

    while True:
        user_text = listen()
        if not user_text:
            continue
        if "quit" in user_text.lower():
            speak("Goodbye!")
            break

        history.append({"role": "user", "content": user_text})

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=history,
                max_tokens=300,     # shorter = faster speech
                temperature=0.7
            )
            reply = response.choices[0].message.content
        except Exception as e:
            print(f"  ❌ API Error: {e}")
            continue

        history.append({"role": "assistant", "content": reply})
        print(f"\n  🔥 Spark: {reply}\n")
        speak(reply)


# ═══════════════════════════════════════════════════════════
# MODE 3 — PDF CHATBOT
# ═══════════════════════════════════════════════════════════
def mode_pdf():
    header("MODE 3 — PDF CHATBOT")

    try:
        from pypdf import PdfReader
    except ImportError:
        print("  ❌ Install required: pip install pypdf")
        return

    # ── Pick PDF ────────────────────────────────────────────
    pdfs = list(Path("pdfs").glob("*.pdf"))
    if not pdfs:
        print("  ❌ No PDFs found in pdfs/ folder.")
        print("     Drop a .pdf file into the pdfs/ folder and re-run.\n")
        return

    print("  📄 Available PDFs:")
    for i, p in enumerate(pdfs):
        size = p.stat().st_size // 1024
        print(f"     [{i+1}] {p.name}  ({size} KB)")

    try:
        idx = int(input("\n  Choose PDF number: ").strip()) - 1
        pdf_path = pdfs[idx]
    except (ValueError, IndexError):
        print("  ❌ Invalid choice.")
        return

    # ── Extract text ────────────────────────────────────────
    print(f"\n  📖 Reading: {pdf_path.name} …")
    reader = PdfReader(str(pdf_path))
    pages  = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {i+1}]\n{text.strip()}")

    full_text = "\n\n".join(pages)

    # Truncate to ~8000 chars to stay within context
    MAX_CHARS = 8000
    if len(full_text) > MAX_CHARS:
        full_text = full_text[:MAX_CHARS]
        print(f"  ⚠️  PDF truncated to {MAX_CHARS} chars (too large).")

    print(f"  ✅ Loaded {len(reader.pages)} pages, {len(full_text)} chars.\n")
    print(f"  Commands: 'quit' 'save'\n")

    pdf_system = (
        f"{PERSONA}\n\n"
        f"You have been given the content of '{pdf_path.name}'.\n"
        f"Answer questions ONLY based on this document.\n"
        f"If the answer isn't in the document, say so clearly.\n\n"
        f"DOCUMENT CONTENT:\n{full_text}"
    )

    history = [{"role": "system", "content": pdf_system}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "save":
            save_chat(history, "pdf")
            continue

        history.append({"role": "user", "content": user_input})

        print("\n🔥 Spark: ", end="", flush=True)
        full_reply = ""
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=history,
                max_tokens=600,
                temperature=0.2,    # low temp = stick to document facts
                stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                print(delta, end="", flush=True)
                full_reply += delta
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

        print("\n")
        history.append({"role": "assistant", "content": full_reply})


# ═══════════════════════════════════════════════════════════
# MODE 4 — MEMORY DATABASE CHATBOT
# ═══════════════════════════════════════════════════════════
def mode_memory():
    header("MODE 4 — MEMORY DATABASE CHATBOT")

    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("  ❌ Install required: pip install chromadb sentence-transformers")
        return

    print("  🧠 Loading memory model (first run takes ~30 sec) …")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")   # tiny & fast, no GPU
    chroma   = chromadb.PersistentClient(path="./memory")

    try:
        mem_col = chroma.get_collection("spark_memory")
        print(f"  ✅ Loaded existing memory ({mem_col.count()} facts stored).")
    except Exception:
        mem_col = chroma.create_collection("spark_memory")
        print("  ✅ Created new memory database.")

    history = [{"role": "system", "content": PERSONA}]
    print("\n  Commands: 'remember X' · 'recall X' · 'clear memory' · 'save' · 'quit'\n")

    def store_memory(fact: str):
        emb = embedder.encode([fact]).tolist()
        doc_id = f"mem_{datetime.datetime.now().timestamp()}"
        mem_col.add(embeddings=emb, documents=[fact], ids=[doc_id])
        print(f"  🧠 Stored: \"{fact}\"")

    def recall_memory(query: str, top_k: int = 3) -> list[str]:
        if mem_col.count() == 0:
            return []
        emb     = embedder.encode([query]).tolist()
        results = mem_col.query(query_embeddings=emb, n_results=min(top_k, mem_col.count()))
        return results["documents"][0] if results["documents"] else []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "save":
            save_chat(history, "memory")
            continue
        if user_input.lower() == "clear memory":
            chroma.delete_collection("spark_memory")
            mem_col = chroma.create_collection("spark_memory")
            print("  🗑️  Memory cleared.\n")
            continue

        # Manual remember command
        if user_input.lower().startswith("remember "):
            fact = user_input[9:].strip()
            store_memory(fact)
            print()
            continue

        # Manual recall command
        if user_input.lower().startswith("recall "):
            query   = user_input[7:].strip()
            results = recall_memory(query)
            if results:
                print("  🧠 Recalled memories:")
                for m in results:
                    print(f"     • {m}")
            else:
                print("  🧠 No relevant memories found.")
            print()
            continue

        # Auto-recall relevant memories and inject into context
        memories = recall_memory(user_input)
        mem_context = ""
        if memories:
            mem_context = (
                "\n\n[RELEVANT MEMORIES FROM DATABASE]\n"
                + "\n".join(f"• {m}" for m in memories)
                + "\nUse these facts to personalise your response.\n"
            )

        augmented_input = user_input + mem_context
        history.append({"role": "user", "content": augmented_input})

        print("\n🔥 Spark: ", end="", flush=True)
        full_reply = ""
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=history,
                max_tokens=500,
                temperature=0.7,
                stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                print(delta, end="", flush=True)
                full_reply += delta
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

        print("\n")
        history.append({"role": "assistant", "content": full_reply})

        # Auto-detect and store key facts the user shares
        fact_triggers = ["my name is", "i am", "i work", "i like", "i live", "i have"]
        if any(t in user_input.lower() for t in fact_triggers):
            store_memory(f"User said: {user_input}")


# ═══════════════════════════════════════════════════════════
# MODE 5 — WEB UI CHATBOT
# ═══════════════════════════════════════════════════════════
def mode_webui():
    header("MODE 5 — WEB UI CHATBOT")

    try:
        import gradio as gr
    except ImportError:
        print("  ❌ Install required: pip install gradio")
        return

    print("  🌐 Starting web server …")
    print("  📌 Open your browser at: http://localhost:7860\n")

    def chat_fn(message: str, history: list) -> str:
        """Gradio calls this for each message."""
        messages = [{"role": "system", "content": PERSONA}]

        for user_msg, bot_msg in history:
            messages.append({"role": "user",      "content": user_msg})
            messages.append({"role": "assistant",  "content": bot_msg})

        messages.append({"role": "user", "content": message})

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=600,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {e}"

    demo = gr.ChatInterface(
        fn          = chat_fn,
        title       = "🔥 Spark — Fireworks AI Chatbot",
        description = "Powered by Kimi K2.5 via Fireworks AI · No GPU needed",
        theme       = gr.themes.Soft(),
        examples    = [
            "Explain machine learning in simple terms.",
            "Write a Python function to reverse a string.",
            "What are the top 5 productivity tips?",
        ],
        retry_btn   = None,
        undo_btn    = "↩ Undo",
        clear_btn   = "🗑️ Clear",
    )

    demo.launch(
        server_name = "localhost",
        server_port = 7860,
        share       = False,     # True = public URL (requires internet)
        inbrowser   = True       # auto-opens browser tab
    )


# ═══════════════════════════════════════════════════════════
# MODE 6 — AI AGENT (Function Calling)
# ═══════════════════════════════════════════════════════════
def mode_agent():
    header("MODE 6 — AI AGENT")
    print("  The AI can use tools: calculator, web search sim,")
    print("  date/time, file writer, word counter.\n")
    print("  Commands: 'quit'\n")

    # ── TOOL DEFINITIONS ────────────────────────────────────
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluate a mathematical expression. Use for any arithmetic.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Math expression e.g. '(12 * 4) / 2 + 100'"
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_datetime",
                "description": "Get the current date and time.",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "word_counter",
                "description": "Count words and characters in a piece of text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to count"}
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "save_to_file",
                "description": "Save text content to a file in the outputs folder.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Filename without path"},
                        "content":  {"type": "string", "description": "Text to save"}
                    },
                    "required": ["filename", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_search_sim",
                "description": "Simulate a web search result for a query topic.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    # ── TOOL EXECUTOR ────────────────────────────────────────
    def run_tool(name: str, args: dict) -> str:
        if name == "calculator":
            try:
                # Safe eval: only numbers and operators
                expr   = re.sub(r"[^0-9+\-*/().% ]", "", args["expression"])
                result = eval(expr)
                return f"Result: {result}"
            except Exception as e:
                return f"Calculation error: {e}"

        elif name == "get_datetime":
            now = datetime.datetime.now()
            return (f"Current date: {now.strftime('%A, %d %B %Y')}\n"
                    f"Current time: {now.strftime('%I:%M %p')}")

        elif name == "word_counter":
            text  = args["text"]
            words = len(text.split())
            chars = len(text)
            return f"Words: {words} | Characters: {chars}"

        elif name == "save_to_file":
            path = Path("outputs") / args["filename"]
            path.write_text(args["content"], encoding="utf-8")
            return f"Saved to: {path.resolve()}"

        elif name == "web_search_sim":
            # Simulated — in production, plug in a real search API
            return (f"[Simulated search results for '{args['query']}']\n"
                    f"Top result: Wikipedia article on {args['query']}.\n"
                    f"Note: In production, connect a real search API here.")
        else:
            return f"Unknown tool: {name}"

    # ── AGENT LOOP ───────────────────────────────────────────
    history = [{"role": "system", "content": PERSONA + "\nYou have tools available. Use them when helpful."}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input or user_input.lower() == "quit":
            break

        history.append({"role": "user", "content": user_input})

        # Agentic loop — model may call multiple tools in sequence
        max_steps = 5
        for step in range(max_steps):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=history,
                    tools=TOOLS,
                    tool_choice="auto",
                    max_tokens=600,
                    temperature=0.3
                )
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                break

            msg           = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            # Model wants to call a tool
            if finish_reason == "tool_calls" and msg.tool_calls:
                history.append({
                    "role":       "assistant",
                    "content":    msg.content or "",
                    "tool_calls": [
                        {
                            "id":       tc.id,
                            "type":     "function",
                            "function": {
                                "name":      tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                })

                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments)
                    except Exception:
                        fn_args = {}

                    print(f"\n  🔧 Tool: {fn_name}({fn_args})")
                    tool_result = run_tool(fn_name, fn_args)
                    print(f"  ✅ Result: {tool_result}")

                    history.append({
                        "role":        "tool",
                        "tool_call_id": tc.id,
                        "content":     tool_result
                    })

                # Continue loop → model processes tool results
                continue

            # Model has a final text answer
            reply = msg.content or ""
            print(f"\n🔥 Spark: {reply}\n")
            history.append({"role": "assistant", "content": reply})
            break


# ═══════════════════════════════════════════════════════════
# MODE 7 — RAG CHATBOT (Retrieval-Augmented Generation)
# ═══════════════════════════════════════════════════════════
def mode_rag():
    header("MODE 7 — RAG CHATBOT")

    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        from pypdf import PdfReader
    except ImportError:
        print("  ❌ Install required: pip install chromadb sentence-transformers pypdf")
        return

    print("  🧠 Loading embedding model (first run ~30 sec) …")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    chroma   = chromadb.Client()   # in-memory (resets each run)
    rag_col  = chroma.create_collection("rag_docs")

    # ── Load documents from pdfs/ folder ────────────────────
    pdfs = list(Path("pdfs").glob("*.pdf"))
    txts = list(Path("pdfs").glob("*.txt"))

    if not pdfs and not txts:
        print("  ❌ No files in pdfs/ folder.")
        print("     Add .pdf or .txt files to pdfs/ and re-run.\n")
        return

    print(f"\n  📂 Found {len(pdfs)} PDFs and {len(txts)} TXTs. Indexing …")

    doc_id = 0

    def chunk_text(text: str, size: int = 400, overlap: int = 50) -> list[str]:
        """Split text into overlapping chunks for better retrieval."""
        words  = text.split()
        chunks = []
        i      = 0
        while i < len(words):
            chunk = " ".join(words[i : i + size])
            chunks.append(chunk)
            i += size - overlap
        return chunks

    # Index PDFs
    for pdf_path in pdfs:
        reader = PdfReader(str(pdf_path))
        text   = " ".join(
            (p.extract_text() or "") for p in reader.pages
        )
        chunks = chunk_text(text)
        for chunk in chunks:
            if not chunk.strip():
                continue
            emb = embedder.encode([chunk]).tolist()
            rag_col.add(
                embeddings=emb,
                documents=[chunk],
                ids=[f"doc_{doc_id}"],
                metadatas=[{"source": pdf_path.name}]
            )
            doc_id += 1
        print(f"  ✅ Indexed: {pdf_path.name} ({len(chunks)} chunks)")

    # Index TXTs
    for txt_path in txts:
        text   = txt_path.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text)
        for chunk in chunks:
            if not chunk.strip():
                continue
            emb = embedder.encode([chunk]).tolist()
            rag_col.add(
                embeddings=emb,
                documents=[chunk],
                ids=[f"doc_{doc_id}"],
                metadatas=[{"source": txt_path.name}]
            )
            doc_id += 1
        print(f"  ✅ Indexed: {txt_path.name} ({len(chunks)} chunks)")

    print(f"\n  ✅ Total chunks in index: {rag_col.count()}")
    print(f"  Commands: 'quit' 'save'\n")

    history = [{"role": "system", "content": PERSONA}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "save":
            save_chat(history, "rag")
            continue

        # ── RETRIEVE relevant chunks ─────────────────────────
        q_emb    = embedder.encode([user_input]).tolist()
        n        = min(4, rag_col.count())
        results  = rag_col.query(query_embeddings=q_emb, n_results=n)
        chunks   = results["documents"][0] if results["documents"] else []
        sources  = [m["source"] for m in results["metadatas"][0]] if results["metadatas"] else []

        context = ""
        if chunks:
            context = (
                "\n\n[RETRIEVED CONTEXT FROM DOCUMENTS]\n"
                + "\n\n---\n".join(
                    f"Source: {src}\n{chunk}"
                    for chunk, src in zip(chunks, sources)
                )
                + "\n\nAnswer using the retrieved context. "
                  "If the answer isn't there, say so clearly."
            )
            unique_sources = list(dict.fromkeys(sources))
            print(f"  📚 Sources: {', '.join(unique_sources)}")

        augmented = user_input + context
        history.append({"role": "user", "content": augmented})

        print("\n🔥 Spark: ", end="", flush=True)
        full_reply = ""
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=history,
                max_tokens=600,
                temperature=0.2,    # low = factual
                stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                print(delta, end="", flush=True)
                full_reply += delta
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

        print("\n")
        # Store only the original question (not the context blob) in history
        history[-1] = {"role": "user",      "content": user_input}
        history.append({"role": "assistant", "content": full_reply})


# ═══════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════
MODES = {
    "1": ("Streaming Chatbot",    mode_streaming),
    "2": ("Voice Chatbot",        mode_voice),
    "3": ("PDF Chatbot",          mode_pdf),
    "4": ("Memory Database",      mode_memory),
    "5": ("Web UI Chatbot",       mode_webui),
    "6": ("AI Agent",             mode_agent),
    "7": ("RAG Chatbot",          mode_rag),
}

def main_menu():
    while True:
        print()
        divider("═")
        print("   🔥  FIREWORKS AI — ULTIMATE CHATBOT")
        print(f"   Model: {MODEL.split('/')[-1]}")
        divider("═")
        print()
        for key, (name, _) in MODES.items():
            print(f"   [{key}]  {name}")
        print()
        print("   [q]  Quit")
        print()
        divider("─")

        choice = input("  Select mode: ").strip().lower()
        print()

        if choice == "q":
            print("  👋 Goodbye!\n")
            break
        elif choice in MODES:
            _, fn = MODES[choice]
            try:
                fn()
            except KeyboardInterrupt:
                print("\n  ⏹️  Mode exited.\n")
        else:
            print("  ❌ Invalid choice. Enter 1-7 or q.\n")


if __name__ == "__main__":
    if not API_KEY:
        print("\n❌ FIREWORKS_API_KEY not found in .env file.")
        print("   Create a .env file with: FIREWORKS_API_KEY=fw-your-key\n")
        sys.exit(1)
    main_menu()