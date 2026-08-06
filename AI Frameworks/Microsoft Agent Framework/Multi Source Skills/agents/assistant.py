import re
import logging
from typing import Dict, Any, Tuple, Optional
from agents.manager import SkillManager

logger = logging.getLogger("AssistantAgent")

class AssistantAgent:
    """
    An illustrative agent that interacts with the SkillRegistry.
    Simulates an LLM reasoning loop (Thought -> Action -> Observation -> Final Answer)
    by parsing natural language and executing corresponding skills.
    """
    
    def __init__(self, manager: SkillManager):
        self.manager = manager

    def _reason(self, query: str) -> Tuple[Optional[str], Dict[str, Any], str]:
        """
        Parses intent from query and maps it to a skill with arguments.
        Returns Tuple: (skill_name, arguments, thought_process)
        """
        q = query.lower()
        
        # 1. math_add
        if "add" in q or "sum" in q or "plus" in q:
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', q)
            if len(numbers) >= 2:
                a, b = float(numbers[0]), float(numbers[1])
                return "math_add", {"a": a, "b": b}, f"Thought: User wants to add two numbers ({a} and {b}). I will use the math_add skill."
                
        # 2. math_subtract
        if "subtract" in q or "minus" in q or "difference" in q:
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', q)
            if len(numbers) >= 2:
                a, b = float(numbers[0]), float(numbers[1])
                return "math_subtract", {"a": a, "b": b}, f"Thought: User wants to subtract {b} from {a}. I will use the math_subtract skill."

        # 3. math_factorial
        if "factorial" in q:
            numbers = re.findall(r'\b\d+\b', q)
            if numbers:
                n = int(numbers[0])
                return "math_factorial", {"n": n}, f"Thought: User is asking for the factorial of {n}. I will use the math_factorial skill."

        # 4. translate
        if "translate" in q:
            # e.g., "translate Hello World to Spanish"
            match = re.search(r"translate\s+(.+?)\s+to\s+(\w+)", query, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                lang = match.group(2).strip()
                return "translate", {"text": text, "language": lang}, f"Thought: User needs a translation for '{text}' to '{lang}'. I will use the translate skill."
            else:
                return "translate", {"text": query, "language": "Spanish"}, "Thought: Translation requested but details ambiguous. Defaulting to Spanish translation."

        # 5. send_email
        if "email" in q or "send mail" in q:
            # e.g. "email support@example.com about Server Error body System is down"
            recipient_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)
            recipient = recipient_match.group(0) if recipient_match else "admin@example.com"
            
            subject_match = re.search(r'subject\s+([^\n,]+)', query, re.IGNORECASE) or re.search(r'about\s+([^\n,]+)', query, re.IGNORECASE)
            subject = subject_match.group(1).strip() if subject_match else "Automated Alert"
            
            body_match = re.search(r'body\s+([^\n,]+)', query, re.IGNORECASE) or re.search(r'saying\s+([^\n,]+)', query, re.IGNORECASE)
            body = body_match.group(1).strip() if body_match else "Hello from Agentic System."
            
            return "send_email", {"recipient": recipient, "subject": subject, "body": body}, f"Thought: Sending email to {recipient} with subject '{subject}'. I will use the send_email skill."

        # 6. system_info
        if "system" in q or "kernel" in q or "uname" in q or "os info" in q:
            return "system_info", {}, "Thought: User wants system and host information. I will run the system_info skill."

        # 7. markdown_greet
        if "greet" in q or "say hello" in q:
            name_match = re.search(r"(?:greet|hello)\s+([\w\s]+)", query, re.IGNORECASE)
            name = name_match.group(1).strip() if name_match else "User"
            # Strip helper verbs
            name = re.sub(r'^(?:to|for|me)\s+', '', name, flags=re.IGNORECASE)
            return "markdown_greet", {"name": name}, f"Thought: User wants to say hello or greet someone named '{name}'. I will use the markdown_greet skill."

        # 8. search_skill
        if "search" in q or "query" in q or "find" in q:
            # Extract query, e.g. "search for AI agent skills"
            search_query = re.sub(r'.*?search(?:\s+for)?\s+', '', query, flags=re.IGNORECASE).strip()
            if not search_query:
                search_query = "latest agent frameworks"
            return "search_skill", {"query": search_query}, f"Thought: User is asking to search for '{search_query}'. I will use the active search_skill."

        return None, {}, "Thought: I could not map the user query to any registered skill. I will explain my capabilities."

    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Runs the agent loop on a user query.
        Returns a structured dictionary showing the thought trace and results.
        """
        registry = self.manager.get_registry()
        skill_name, args, thought = self._reason(query)
        
        logger.info(f"Agent prompt: '{query}'")
        logger.info(thought)

        if not skill_name:
            available = [s.name for s in registry.list_skills()]
            answer = (
                f"I'm sorry, I couldn't understand your request. "
                f"Here are the skills I currently have available: {', '.join(available)}"
            )
            return {
                "thought": thought,
                "action": "none",
                "arguments": {},
                "observation": "intent not matching any tool",
                "answer": answer,
                "success": False
            }

        if not registry.get_skill(skill_name):
            answer = f"The skill '{skill_name}' was selected, but it is not active in the registry."
            return {
                "thought": thought,
                "action": skill_name,
                "arguments": args,
                "observation": "skill not registered",
                "answer": answer,
                "success": False
            }

        try:
            # Execute skill
            result = registry.execute(skill_name, **args)
            answer = f"The task completed successfully. Result: {result}"
            return {
                "thought": thought,
                "action": skill_name,
                "arguments": args,
                "observation": str(result),
                "answer": answer,
                "success": True
            }
        except Exception as e:
            answer = f"An error occurred while executing skill '{skill_name}': {e}"
            return {
                "thought": thought,
                "action": skill_name,
                "arguments": args,
                "observation": f"Error: {e}",
                "answer": answer,
                "success": False
            }
