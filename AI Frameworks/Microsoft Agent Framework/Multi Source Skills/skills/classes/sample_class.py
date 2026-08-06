from providers.class_provider import skill_method

class MathSkills:
    """Contains math operation skills."""
    
    @skill_method(
        name="math_subtract",
        description="Subtracts the second number from the first number.",
        parameters={
            "a": {"type": "number", "description": "The first number"},
            "b": {"type": "number", "description": "The number to subtract"}
        }
    )
    def subtract(self, a: float, b: float) -> float:
        return a - b

class EmailSkills:
    """Contains communication skills."""
    
    @skill_method(
        name="send_email",
        description="Sends a simulated email to a recipient.",
        parameters={
            "recipient": {"type": "string", "description": "Email address of the recipient"},
            "subject": {"type": "string", "description": "Subject of the email"},
            "body": {"type": "string", "description": "Body content of the email"}
        }
    )
    def send(self, recipient: str, subject: str, body: str) -> str:
        return f"Email successfully sent to {recipient} with subject '{subject}'. Body bytes: {len(body)}"

class SearchSkills:
    """Contains query and lookup skills."""
    
    @skill_method(
        name="search_skill",
        description="Search database/web (Class-based implementation)",
        parameters={
            "query": {"type": "string", "description": "Query string"}
        }
    )
    def query(self, query: str) -> str:
        return f"Class-based search results for query: '{query}' [Highly structured]"
