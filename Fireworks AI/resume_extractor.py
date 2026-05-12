import json
import re
import os
from dotenv import load_dotenv
from fireworks.client import Fireworks

# =========================================
# LOAD ENVIRONMENT VARIABLES
# =========================================

load_dotenv()

# =========================================
# INITIALIZE FIREWORKS CLIENT
# =========================================

client = Fireworks(
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# =========================================
# RESUME EXTRACTION FUNCTION
# =========================================

def extract_resume(resume_text):

    try:

        # -------------------------------
        # AI REQUEST
        # -------------------------------

        response = client.chat.completions.create(

            model="accounts/fireworks/models/qwen3-8b",

            messages=[

                {
                    "role": "system",

                    "content": """
You are a professional AI resume parser.

STRICT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations
- No <think> tags
- No extra text
"""
                },

                {
                    "role": "user",

                    "content": f"""
Extract resume information.

Return JSON with EXACT keys:

{{
    "full_name": "",
    "email": "",
    "phone": "",
    "location": "",
    "years_experience": 0,
    "skills": [],
    "education": [],
    "work_history": [],
    "summary": "",
    "suitable_roles": []
}}

Resume:

{resume_text}
"""
                }
            ],

            temperature=0.1,
            max_tokens=1200
        )

        # -------------------------------
        # RAW RESPONSE
        # -------------------------------

        raw = response.choices[0].message.content

        print("\n==============================")
        print("RAW AI RESPONSE")
        print("==============================\n")

        print(raw)

        # -------------------------------
        # SAFE JSON EXTRACTION
        # -------------------------------

        match = re.search(r'\{.*\}', raw, re.DOTALL)

        if not match:
            raise ValueError("No valid JSON found.")

        json_text = match.group()

        # -------------------------------
        # PARSE JSON
        # -------------------------------

        data = json.loads(json_text)

        return data

    except json.JSONDecodeError as e:

        print("\nJSON PARSE ERROR:")
        print(e)

    except Exception as e:

        print("\nGENERAL ERROR:")
        print(e)

# =========================================
# SAMPLE RESUME INPUT
# =========================================

resume = """
John Smith
john@email.com
+91 9876543210
Bangalore, India

Professional Summary:
Software Developer with 5 years of experience building AI and web applications.

Skills:
Python, React, AWS, Docker, Machine Learning, FastAPI, SQL

Education:
B.Tech Computer Science
IIT Bombay
2019

Experience:
Senior Developer at TechCorp (2021-Present)
Software Engineer at StartupXYZ (2019-2021)

Projects:
AI Chatbot
Resume Parser
Recommendation System
"""

# =========================================
# RUN EXTRACTION
# =========================================

data = extract_resume(resume)

# =========================================
# PRINT CLEAN OUTPUT
# =========================================

if data:

    print("\n==============================")
    print("STRUCTURED JSON OUTPUT")
    print("==============================\n")

    print(json.dumps(data, indent=2))

    # -------------------------------
    # SAVE JSON FILE
    # -------------------------------

    os.makedirs("outputs", exist_ok=True)

    with open(
        "outputs/extracted_resume.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(data, file, indent=2)

    print("\nJSON saved successfully:")
    print("outputs/extracted_resume.json")
    