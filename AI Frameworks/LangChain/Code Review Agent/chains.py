from agent.prompts import REVIEW_PROMPT
from agent.reviewer import review_code

from analysis.ast_parser import analyze_code_structure
from analysis.pylint_runner import run_pylint
from analysis.flake8_runner import run_flake8
from analysis.bandit_runner import run_bandit
from analysis.complexity import analyze_complexity


def run_review(code):

    ast_data = analyze_code_structure(code)

    pylint_data = run_pylint(code)

    flake8_data = run_flake8(code)

    bandit_data = run_bandit(code)

    complexity_data = analyze_complexity(code)

    prompt = REVIEW_PROMPT.format(
        code=code,
        ast_data=ast_data,
        pylint_report=pylint_data,
        flake8_report=flake8_data,
        bandit_report=bandit_data,
        complexity_report=complexity_data
    )

    review = review_code(prompt)

    return (
        review,
        ast_data,
        pylint_data,
        flake8_data,
        bandit_data,
        complexity_data
    )