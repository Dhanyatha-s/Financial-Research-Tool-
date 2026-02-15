# statement_classifier.py

import re
from typing import List, Dict
import pandas as pd


class StatementClassifier:
    """
    Classifies financial tables into statement types:
    - Income Statement
    - Balance Sheet
    - Cash Flow
    - Segment Reporting
    - Ratios
    - Unknown
    """

    INCOME_KEYWORDS = [
        "revenue", "income", "expense", "profit",
        "ebitda", "pbt", "pat", "tax", "finance cost"
    ]

    BALANCE_KEYWORDS = [
        "assets", "liabilities", "equity",
        "reserves", "borrowings", "share capital"
    ]

    CASHFLOW_KEYWORDS = [
        "cash flow", "operating activities",
        "investing activities", "financing activities"
    ]

    SEGMENT_KEYWORDS = [
        "segment", "business segment",
        "consumer care", "industrial care"
    ]

    RATIO_KEYWORDS = [
        "ratio", "%", "eps", "per share",
        "debt equity"
    ]

    def classify_table(self, df: pd.DataFrame) -> Dict:
        """
        Classify a single dataframe.
        Returns dict with statement type + confidence score.
        """

        first_col = df.iloc[:, 0].astype(str).str.lower()

        text_blob = " ".join(first_col.tolist())

        scores = {
            "Income Statement": self._score(text_blob, self.INCOME_KEYWORDS),
            "Balance Sheet": self._score(text_blob, self.BALANCE_KEYWORDS),
            "Cash Flow": self._score(text_blob, self.CASHFLOW_KEYWORDS),
            "Segment Reporting": self._score(text_blob, self.SEGMENT_KEYWORDS),
            "Ratios": self._score(text_blob, self.RATIO_KEYWORDS),
        }

        best_match = max(scores, key=scores.get)
        confidence = scores[best_match]

        if confidence == 0:
            best_match = "Unknown"

        return {
            "statement_type": best_match,
            "confidence": confidence
        }

    def classify_all(self, tables: List[pd.DataFrame]) -> Dict[str, List[pd.DataFrame]]:
        """
        Classify list of tables and group them.
        """

        grouped = {
            "Income Statement": [],
            "Balance Sheet": [],
            "Cash Flow": [],
            "Segment Reporting": [],
            "Ratios": [],
            "Unknown": []
        }

        for df in tables:
            result = self.classify_table(df)
            grouped[result["statement_type"]].append(df)

        return grouped

    def _score(self, text: str, keywords: List[str]) -> int:
        return sum(1 for word in keywords if word in text)
