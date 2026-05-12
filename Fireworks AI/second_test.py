import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("FIREWORKS_API_KEY")
if not api_key:
    raise SystemExit("[ERROR] FIREWORKS_API_KEY not found in .env")

print(f"[OK] Key loaded: {api_key[:8]}{'*' * 10}")

# ── CONFIG — change these to adjust behavior ───────────────────────────────────
YOUR_QUESTION = "Explain AI agents briefly."  # ← change your prompt here
MAX_TOKENS    = 200                           # ← change response length here
TEMPERATURE   = 0.7                           # ← 0.0 = precise, 1.0 = creative

# ── CONFIRMED SERVERLESS MODELS (as of May 2026) — all have live pricing ──────
# Swap MODEL to any of these. Cost shown per 1M tokens.
#
#   "accounts/fireworks/models/qwen3-8b"              ← 8B  | $0.20/M  ✅ RECOMMENDED
#   "accounts/fireworks/models/qwen3-4b"              ← 4B  | $0.10/M
#   "accounts/fireworks/models/qwen3-1p7b"            ← 1.7B| $0.10/M
#   "accounts/fireworks/models/qwen3-0p6b"            ← 0.6B| $0.10/M  (cheapest)
#   "accounts/fireworks/models/llama-v3p3-70b-instruct" ← 70B| $0.90/M (large)
#
MODEL = "accounts/fireworks/models/qwen3-8b"

# ── Try native Fireworks SDK first, fall back to OpenAI-compat ────────────────
response_text = None

# Method 1: Native fireworks-ai SDK (pip install fireworks-ai)
try:
    from fireworks.client import Fireworks
    client = Fireworks(api_key=api_key)
    print(f"[...] Calling {MODEL} via native SDK...")
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user",   "content": YOUR_QUESTION}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    response_text = resp.choices[0].message.content

except ImportError:
    print("[WARN] fireworks-ai not installed. Run: pip install fireworks-ai")
    print("[...] Falling back to OpenAI-compat client...")

except Exception as e:
    print(f"[FAIL] Native SDK error: {e}")
    print("[...] Falling back to OpenAI-compat client...")

# Method 2: OpenAI-compat fallback
if response_text is None:
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=api_key
        )
        print(f"[...] Calling {MODEL} via OpenAI-compat...")
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user",   "content": YOUR_QUESTION}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        response_text = resp.choices[0].message.content

    except Exception as e:
        print(f"[FAIL] OpenAI-compat error: {e}")

# ── Output ─────────────────────────────────────────────────────────────────────
if response_text:
    print(f"\n{'='*50}")
    print(f"Model : {MODEL}")
    print(f"Prompt: {YOUR_QUESTION}")
    print(f"{'='*50}")
    print(response_text)
else:
    print("\n[ERROR] Both methods failed. Check these:")
    print("  1. fireworks.ai → top-right avatar → Billing → confirm $1 credit shows")
    print("  2. Check email inbox for a Fireworks verification email")
    print("  3. Try logging into app.fireworks.ai and running a model in the playground")
    print("  4. If playground works but API doesn't → contact support@fireworks.ai")