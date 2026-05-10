import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "❌ GROQ_API_KEY not found in .env file"
    )

# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="AI Translator API",
    description="Groq Powered Translator",
    version="1.0"
)

# =========================
# GROQ CLIENT
# =========================

client = Groq(
    api_key=GROQ_API_KEY
)

# =========================
# SUPPORTED LANGUAGES
# =========================

LANGUAGES = {
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese"
}

# =========================
# REQUEST MODEL
# =========================

class TranslateRequest(BaseModel):

    text: str
    target_language: str
    source_language: str = "auto"

# =========================
# HOME ROUTE
# =========================

@app.get("/")
async def home():

    return {
        "status": "running",
        "message": "🚀 AI Translator API Running Successfully"
    }

# =========================
# GET LANGUAGES
# =========================

@app.get("/languages")
async def get_languages():

    return LANGUAGES

# =========================
# TRANSLATE ROUTE
# =========================

@app.post("/translate")
async def translate(req: TranslateRequest):

    start = time.time()

    # Validate language
    if req.target_language not in LANGUAGES:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Use: {list(LANGUAGES.keys())}"
        )

    target_name = LANGUAGES[req.target_language]

    prompt = f"""
    Translate this into {target_name}.

    Return ONLY translated text.

    Text:
    {req.text}
    """

    try:

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.1,
            max_tokens=500
        )

        translated_text = (
            response
            .choices[0]
            .message
            .content
        )

        elapsed = round(
            time.time() - start,
            2
        )

        return {

            "success": True,

            "original_text": req.text,

            "translated_text": translated_text,

            "target_language": target_name,

            "response_time_sec": elapsed,

            "tokens_used": response.usage.total_tokens
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================
# RUN SERVER DIRECTLY
# =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "P4_Translator:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )