import json
import os

from dotenv import load_dotenv
from fireworks.client import Fireworks

# =========================================
# LOAD ENV VARIABLES
# =========================================

load_dotenv()

# =========================================
# INITIALIZE CLIENT
# =========================================

client = Fireworks(
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# =========================================
# TOOLS
# =========================================

tools = [

    {
        "type": "function",

        "function": {

            "name": "get_weather",

            "description":
            "Get weather information for a city.",

            "parameters": {

                "type": "object",

                "properties": {

                    "city": {
                        "type": "string"
                    },

                    "unit": {
                        "type": "string",
                        "enum": [
                            "celsius",
                            "fahrenheit"
                        ]
                    }
                },

                "required": ["city"]
            }
        }
    },

    {
        "type": "function",

        "function": {

            "name": "search_products",

            "description":
            "Search products database.",

            "parameters": {

                "type": "object",

                "properties": {

                    "query": {
                        "type": "string"
                    }
                },

                "required": ["query"]
            }
        }
    }
]
# =========================================
# PYTHON FUNCTIONS
# =========================================
def get_weather(city, unit="celsius"):

    return {
        "city": city,
        "temperature": 32,
        "unit": unit,
        "condition": "Partly Cloudy"
    }
def search_products(query):
    return {
        "results": [
            f"Gaming Laptop for '{query}'",
            f"Budget Laptop for '{query}'"
        ]
    }

# =========================================
# FUNCTION MAP
# =========================================

function_map = {

    "get_weather": get_weather,

    "search_products": search_products
}

# =========================================
# MAIN AGENT FUNCTION
# =========================================

def run_agent(user_question):

    try:

        messages = [

            {
                "role": "system",

                "content": """
You are an AI assistant with tools.

IMPORTANT:
- Use tools when needed
- Use weather tool for weather
- Use product tool for products
"""
            },

            {
                "role": "user",

                "content": user_question
            }
        ]

        # =================================
        # FIRST AI RESPONSE
        # =================================

        response = client.chat.completions.create(

            model="accounts/fireworks/models/qwen3-8b",

            messages=messages,

            tools=tools,

            tool_choice="auto",

            temperature=0.1,

            max_tokens=400
        )

        ai_message = response.choices[0].message

        print("\n==============================")
        print("AI RESPONSE")
        print("==============================\n")

        print(ai_message)

        # =================================
        # CHECK TOOL CALLS
        # =================================

        if ai_message.tool_calls:

            messages.append(ai_message)

            for tool_call in ai_message.tool_calls:

                function_name = (
                    tool_call.function.name
                )

                function_args = json.loads(
                    tool_call.function.arguments
                )

                print("\nTOOL CALLED:")
                print(function_name)

                print("\nARGUMENTS:")
                print(function_args)

                # =========================
                # EXECUTE FUNCTION
                # =========================

                result = function_map[
                    function_name
                ](**function_args)

                print("\nTOOL RESULT:")
                print(result)

                # =========================
                # ADD TOOL RESULT
                # =========================

                messages.append({

                    "role": "tool",

                    "tool_call_id": tool_call.id,

                    "content": json.dumps(result)
                })

            # =================================
            # FINAL RESPONSE
            # =================================

            final_response = (
                client.chat.completions.create(

                    model="accounts/fireworks/models/qwen3-8b",

                    messages=messages,

                    temperature=0.1,

                    max_tokens=300
                )
            )

            return final_response.choices[
                0
            ].message.content

        else:

            return ai_message.content

    except Exception as e:

        print("\nERROR:\n")

        print(e)

# =========================================
# TESTS
# =========================================

print("\n==============================")
print("FINAL ANSWER")
print("==============================")

# WEATHER TEST
print("\nWEATHER TEST:\n")

print(
    run_agent(
        "What's the weather in Hyderabad?"
    )
)

print("\n--------------------------------")

# PRODUCT TEST
print("\nPRODUCT TEST:\n")

print(
    run_agent(
        "Find gaming laptops"
    )
)

print("\n--------------------------------")

# NORMAL CHAT TEST
print("\nNORMAL CHAT TEST:\n")

print(
    run_agent(
        "What is 2 + 2?"
    )
)