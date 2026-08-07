from agents.llm_client import LLMClient

class IntentClassifierAgent:
    def __init__(self):
        self.llm = LLMClient()

    def process(self, query: str) -> dict:
        system_instruction = (
            "You are the Intent Classifier Agent of a Governed Banking Platform.\n"
            "Your task is to analyze the user query and classify it into one of these intents:\n"
            "  - loan_application (e.g. applying for a loan, borrowing money, starting a loan request)\n"
            "  - loan_inquiry (e.g. asking about interest rates, options, terms, repayment calculation)\n"
            "  - general_support (e.g. support ticket inquiry, app issues, technical bugs, general customer care)\n"
            "\n"
            "Respond in this exact format:\n"
            "INTENT: <intent_name>\n"
            "AGENT: <loan_agent|support_agent>"
        )
        
        response = self.llm.generate(system_instruction, query)
        
        # Parse the intent and agent handoff targets
        intent = "general_support"
        target_agent = "support_agent"
        for line in response.split("\n"):
            if "INTENT:" in line:
                intent = line.split("INTENT:")[1].strip()
            if "AGENT:" in line:
                target_agent = line.split("AGENT:")[1].strip()
                
        return {
            "classified_intent": intent,
            "target_agent": target_agent
        }
