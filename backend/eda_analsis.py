import pandas as pd


class EDAAnalyzer:

    def __init__(self, df: pd.DataFrame):
        if df is None or df.empty:
            raise ValueError("Input DataFrame for EDA is empty")

        self.df = df.copy()
        self.fy_cols = [col for col in self.df.columns if col.startswith("FY")]

        # 🔥 Force numeric for financial columns
        for col in self.fy_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

    # ------------------------------------------------
    # RUN FULL EDA REPORT
    # ------------------------------------------------
    def run_full_eda(self):

        report = {}

        report["dtypes"] = self.df.dtypes

        report["missing_values"] = (
            self.df[self.fy_cols].isna().sum()
            if self.fy_cols else pd.Series(dtype=int)
        )

        report["summary_statistics"] = (
            self.df[self.fy_cols].describe()
            if self.fy_cols else pd.DataFrame()
        )

        report["rows_all_nan"] = (
            self.df[self.fy_cols].isna().all(axis=1).sum()
            if self.fy_cols else 0
        )

        report["duplicate_line_items"] = (
            self.df["Normalized Label"].duplicated().sum()
            if "Normalized Label" in self.df.columns else 0
        )

        report["zero_rows"] = (
            (self.df[self.fy_cols] == 0).all(axis=1).sum()
            if self.fy_cols else 0
        )

        # Count originally non-numeric (now coerced to NaN)
        non_numeric_report = {}
        for col in self.fy_cols:
            non_numeric_report[col] = self.df[col].isna().sum()

        report["non_numeric_entries"] = non_numeric_report

        return report
