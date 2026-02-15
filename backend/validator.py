# validator.py

import pandas as pd
from typing import List, Dict


class FinancialValidator:
    """
    AI-Governed Financial Validator

    Validates:
    - Semantic correctness of LLM decisions
    - Income statement equation integrity
    - Section consistency
    - Totals
    - Data sparsity
    """

    TOLERANCE_PERCENT = 0.05

    def __init__(self, df: pd.DataFrame, year_columns: List[str]):
        self.df = df.copy()
        self.year_columns = year_columns
        self.alerts = []
        self.score = 1.0

        self.label_col = "Particulars" if "Particulars" in df.columns else df.columns[0]

    # ==================================================
    # SEMANTIC VALIDATION (LLM CONFIRMATION)
    # ==================================================

    def _validate_section_logic(self):
        """
        Ensure LLM did not misclassify obvious keywords.
        """

        if "Section" not in self.df.columns:
            return

        for _, row in self.df.iterrows():
            label = str(row[self.label_col]).lower()
            section = str(row["Section"]).lower()

            if "revenue" in label and section != "revenue":
                self._flag(f"Revenue misclassified: {label}")

            if "tax" in label and section not in ["tax", "expenses"]:
                self._flag(f"Tax misclassified: {label}")

            if "profit" in label and section != "profit":
                self._flag(f"Profit misclassified: {label}")

            if "cost" in label and section == "revenue":
                self._flag(f"Cost wrongly placed in Revenue: {label}")

    # ==================================================
    # ACCOUNTING EQUATION VALIDATION
    # ==================================================

    def _validate_income_equation(self):

        for year in self.year_columns:

            revenue = self._get_value("Total Revenue", year)
            expenses = self._get_value("Total Expenses", year)
            pbt = self._get_value("Profit Before Tax", year)
            tax = self._get_value("Tax Expense", year)
            pat = self._get_value("Profit After Tax", year)

            if revenue and expenses and pbt:
                expected = revenue - expenses
                if not self._within_tolerance(expected, pbt):
                    self._flag(f"{year}: Revenue - Expenses ≠ PBT")

            if pbt and tax and pat:
                expected = pbt - tax
                if not self._within_tolerance(expected, pat):
                    self._flag(f"{year}: PBT - Tax ≠ PAT")

    # ==================================================
    # TOTAL VALIDATION
    # ==================================================

    def _validate_totals(self):

        if "Section" not in self.df.columns:
            return

        for year in self.year_columns:

            grouped = self.df.groupby("Section")

            for section, group in grouped:

                total_rows = group[group[self.label_col].str.contains("Total", case=False, na=False)]

                if total_rows.empty:
                    continue

                total_val = pd.to_numeric(total_rows.iloc[0][year], errors="coerce")
                non_total_sum = pd.to_numeric(
                    group[~group[self.label_col].str.contains("Total", case=False, na=False)][year],
                    errors="coerce"
                ).sum()

                if pd.notna(total_val) and not self._within_tolerance(total_val, non_total_sum):
                    self._flag(f"{year}: Total mismatch in section '{section}'")

    # ==================================================
    # UTILITIES
    # ==================================================

    def _get_value(self, label, year):

        if year not in self.df.columns:
            return None

        rows = self.df[self.df[self.label_col] == label]
        if rows.empty:
            return None

        return pd.to_numeric(rows.iloc[0][year], errors="coerce")

    def _within_tolerance(self, expected, actual):
        tolerance = max(abs(expected) * self.TOLERANCE_PERCENT, 5)
        return abs(expected - actual) <= tolerance

    def _flag(self, message):
        self.alerts.append(message)
        self.score -= 0.1

    # ==================================================
    # PUBLIC
    # ==================================================

    def validate(self) -> Dict:

        print("🔍 Validating LLM decisions + financial logic...")

        self._validate_section_logic()
        self._validate_income_equation()
        self._validate_totals()

        self.score = max(min(self.score, 1.0), 0.0)

        result = {
            "is_valid": len(self.alerts) == 0,
            "validation_score": round(self.score * 100, 1),
            "alerts": self.alerts if self.alerts else ["No issues found"]
        }

        print(f"✅ Final Validation Score: {result['validation_score']}%")
        return result
