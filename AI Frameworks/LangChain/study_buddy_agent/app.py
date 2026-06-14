from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from tools import (
    safe_search,
    safe_wiki
)

from memory import (
    load_memory,
    update_name,
    update_goal
)

from notes_generator import save_notes
from quiz_generator import save_quiz
from roadmap_generator import save_roadmap

from prompts import TEACHER_PROMPT


# ==========================================
# ENVIRONMENT
# ==========================================

load_dotenv()


# ==========================================
# LLM
# ==========================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3
)


# ==========================================
# PROMPT
# ==========================================

prompt = ChatPromptTemplate.from_template(
    TEACHER_PROMPT
)


# ==========================================
# CHAIN
# ==========================================

chain = prompt | llm


# ==========================================
# UI
# ==========================================

print("\n======================================")
print("        STUDY BUDDY AGENT")
print("======================================\n")

topic = input("Enter Topic: ").strip()


# ==========================================
# MEMORY : NAME
# ==========================================

if topic.lower().startswith("my name is"):

    name = topic[11:].strip()

    update_name(name)

    print(f"\nNice to meet you, {name}!")

    exit()


# ==========================================
# MEMORY : GOAL
# ==========================================

if topic.lower().startswith("my goal is"):

    goal = topic[11:].strip()

    update_goal(goal)

    print(f"\nGoal Saved: {goal}")

    exit()


# ==========================================
# NOTES GENERATOR
# ==========================================

if topic.lower().startswith("notes:"):

    note_topic = topic[6:].strip()

    print(f"\nGenerating Notes for: {note_topic}\n")

    search_result = safe_search(note_topic)

    wiki_result = safe_wiki(note_topic)

    memory = load_memory()

    response = chain.invoke(
        {
            "name": memory["name"],
            "goal": memory["goal"],
            "search_result": search_result,
            "wiki_result": wiki_result,
            "topic": note_topic,
            "task": "STUDY"
        }
    )

    filename = save_notes(
        note_topic,
        response.content
    )

    print("\n======================================")
    print("NOTES GENERATED SUCCESSFULLY")
    print("======================================")

    print(f"\nSaved File: {filename}")

    exit()


# ==========================================
# QUIZ GENERATOR
# ==========================================

if topic.lower().startswith("quiz:"):

    quiz_topic = topic[5:].strip()

    print(f"\nGenerating Quiz for: {quiz_topic}\n")

    search_result = safe_search(quiz_topic)

    wiki_result = safe_wiki(quiz_topic)

    memory = load_memory()

    response = chain.invoke(
        {
            "name": memory["name"],
            "goal": memory["goal"],
            "search_result": search_result,
            "wiki_result": wiki_result,
            "topic": quiz_topic,
            "task": "QUIZ"
        }
    )

    filename = save_quiz(
        quiz_topic,
        response.content
    )

    print("\n======================================")
    print("QUIZ GENERATED SUCCESSFULLY")
    print("======================================")

    print(f"\nSaved File: {filename}")

    exit()


# ==========================================
# ROADMAP GENERATOR
# ==========================================

if topic.lower().startswith("roadmap:"):

    roadmap_topic = topic[8:].strip()

    print(f"\nGenerating Roadmap for: {roadmap_topic}\n")

    search_result = safe_search(roadmap_topic)

    wiki_result = safe_wiki(roadmap_topic)

    memory = load_memory()

    response = chain.invoke(
        {
            "name": memory["name"],
            "goal": memory["goal"],
            "search_result": search_result,
            "wiki_result": wiki_result,
            "topic": roadmap_topic,
            "task": "ROADMAP"
        }
    )

    filename = save_roadmap(
        roadmap_topic,
        response.content
    )

    print("\n======================================")
    print("ROADMAP GENERATED SUCCESSFULLY")
    print("======================================")

    print(f"\nSaved File: {filename}")

    exit()


# ==========================================
# NORMAL STUDY MODE
# ==========================================

print("\nSearching...\n")

search_result = safe_search(topic)

wiki_result = safe_wiki(topic)

memory = load_memory()

response = chain.invoke(
    {
        "name": memory["name"],
        "goal": memory["goal"],
        "search_result": search_result,
        "wiki_result": wiki_result,
        "topic": topic,
        "task": "STUDY"
    }
)

print("\n======================================")
print("ANSWER")
print("======================================\n")

print(response.content)