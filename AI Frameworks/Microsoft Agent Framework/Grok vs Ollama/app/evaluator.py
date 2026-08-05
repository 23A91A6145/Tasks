import re
import json
import ast
from typing import Dict, Any
from app.utils import get_logger

logger = get_logger("evaluator")

class ResponseEvaluator:
    @staticmethod
    def evaluate(prompt: str, category: str, response_text: str, error: str = None) -> float:
        """
        Evaluate LLM response quality on a scale of 1.0 to 10.0 based on 
        category-specific heuristics and strict constraint checks.
        """
        if error:
            logger.info(f"Evaluation: error present. Quality Score: 1.0")
            return 1.0
            
        if not response_text or response_text.strip() == "":
            logger.info(f"Evaluation: empty response. Quality Score: 1.0")
            return 1.0

        score = 10.0
        category = category.lower()
        
        # Helper: Extract markdown code blocks
        def extract_code_blocks(text: str) -> list:
            return re.findall(r"```(?:python)?\s*(.*?)\s*```", text, re.DOTALL)

        # Heuristic 1: Coding Quality Evaluation
        if "coding" in category or "code" in category:
            code_blocks = extract_code_blocks(response_text)
            if not code_blocks:
                score -= 3.0  # Major penalty: missing code block wrapper
                logger.info("Coding Evaluation: Missing markdown code block.")
            else:
                # Syntax validation for python code blocks
                syntax_errors = 0
                for block in code_blocks:
                    try:
                        ast.parse(block)
                    except SyntaxError as se:
                        syntax_errors += 1
                        logger.warning(f"Coding Evaluation: Syntax error in code block: {se}")
                if syntax_errors > 0:
                    score -= 4.0  # Major penalty: invalid python code syntax
                    logger.info("Coding Evaluation: Code contains python syntax errors.")

        # Heuristic 2: Tool Calling & JSON Quality Evaluation
        elif "tool" in category or "json" in category or "structured" in category:
            # Check for JSON structure
            json_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
            if not json_match:
                score -= 4.0
                logger.info("JSON Evaluation: No JSON object found in response.")
            else:
                try:
                    json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    score -= 4.0
                    logger.info("JSON Evaluation: Malformed JSON object (failed decode).")

        # Heuristic 3: Reasoning & Logical Puzzles
        elif "reasoning" in category or "logic" in category or "math" in category:
            # Check for step-by-step thinking indicators
            thinking_connectors = ["step", "therefore", "consequently", "thus", "implies", "because", "so", "conclude", "since"]
            found_connectors = sum(1 for conn in thinking_connectors if conn in response_text.lower())
            if found_connectors < 2:
                score -= 2.0
                logger.info(f"Reasoning Evaluation: Few thinking connector words found ({found_connectors}).")
            
            # Check for numbered lists indicating step-by-step thinking
            has_steps = re.search(r"(\n\s*\d+\.\s+)", response_text)
            if not has_steps:
                score -= 2.0
                logger.info("Reasoning Evaluation: No numbered steps (e.g. 1. 2. 3.) found.")

        # Heuristic 4: Summarization
        elif "summarization" in category or "summary" in category:
            # Check length (summary should be compact but informative)
            word_count = len(response_text.split())
            if word_count > 300:
                score -= 2.0  # Penalty for excessive wordiness
                logger.info(f"Summarization Evaluation: Summary is too long ({word_count} words).")
            elif word_count < 15:
                score -= 3.0  # Penalty for being too short/non-informative
                logger.info(f"Summarization Evaluation: Summary is too short ({word_count} words).")

        # General completion checks (for all categories)
        # 1. Did the agent repeat the prompt word for word or echo excessively?
        if len(response_text) > len(prompt) * 2 and prompt in response_text:
            score -= 1.5
            logger.info("General Evaluation: Response contains high proportion of prompt echoing.")

        # 2. Check for sudden truncations
        last_char = response_text.strip()[-1] if response_text.strip() else ""
        if last_char not in [".", "!", "?", "\"", "}", "]", "`", ")"]:
            score -= 1.5
            logger.info("General Evaluation: Response ends abruptly (possible truncation or missing final punctuation).")

        # Floor score at 1.0 and ceiling at 10.0
        final_score = max(1.0, min(10.0, score))
        logger.info(f"Evaluation complete. Score: {final_score:.1f}")
        return round(final_score, 1)
