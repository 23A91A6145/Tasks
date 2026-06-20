from pathlib import Path

import ollama

from loguru import logger


logger.add(
    "logs/pipeline.log",
    rotation="1 MB"
)


class AnalystAgent:

    def analyze(self, df):

        logger.info(
            "AI Analysis Started"
        )

        sample = df.head(
            20
        ).to_string()

        prompt = f"""
You are a senior data analyst.

Analyze this dataset.

Dataset Sample:

{sample}

Provide:

1. Summary

2. Insights

3. Data Quality

4. Recommendations

5. Business Interpretation
"""

        response = ollama.chat(

            model="llama3.2:3b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        analysis = response[
            "message"
        ][
            "content"
        ]

        Path(
            "reports"
        ).mkdir(
            exist_ok=True
        )

        with open(
            "reports/ai_analysis.txt",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                analysis
            )

        logger.success(
            "AI Analysis Completed"
        )

        return analysis