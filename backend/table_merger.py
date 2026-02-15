# import pandas as pd

# class TableMerger:

#     def __init__(self):
#         pass

#     def merge_tables(self, tables: list[pd.DataFrame]) -> pd.DataFrame:
#         """
#         Merge multiple OCR extracted tables into a single structured dataframe.
#         """

#         # 1. Remove empty tables
#         tables = [t for t in tables if not t.empty]

#         # 2. Normalize column names
#         normalized_tables = []
#         for df in tables:
#             df.columns = [str(col).strip().lower() for col in df.columns]
#             normalized_tables.append(df)

#         # 3. Concatenate
#         merged = pd.concat(normalized_tables, ignore_index=True)

#         # 4. Drop duplicate header rows
#         merged = merged[merged.iloc[:, 0].str.lower() != "particulars"]

#         return merged

# # for testing
# import pandas as pd

# class TableMerger:

#     def merge(self, structured_tables):

#         # Remove empty
#         structured_tables = [t for t in structured_tables if not t.empty]

#         if not structured_tables:
#             return pd.DataFrame()

#         merged = pd.concat(structured_tables, ignore_index=True)

#         # Remove duplicate header rows
#         merged = merged.drop_duplicates()

#         return merged

# ====== Unstrctured =====
# import pandas as pd


# class TableMerger:

#     def __init__(self):
#         pass

#     def merge_tables(self, tables: list[pd.DataFrame]) -> pd.DataFrame:
#         """
#         Merge multiple structured financial tables into one consolidated dataframe.
#         """

#         # 1️⃣ Remove empty tables
#         tables = [t for t in tables if t is not None and not t.empty]

#         if not tables:
#             return pd.DataFrame()

#         # 2️⃣ Concatenate all structured tables
#         merged = pd.concat(tables, ignore_index=True)

#         # 3️⃣ Identify financial year columns dynamically
#         fy_columns = [col for col in merged.columns if col.startswith("FY")]

#         base_columns = ["Normalized Label", "Original Label", "Currency", "Unit"]

#         # Ensure consistent ordering
#         merged = merged[base_columns + fy_columns]

#         # 4️⃣ Merge duplicate line items using groupby
#         aggregated = (
#             merged
#             .groupby("Normalized Label", as_index=False)
#             .agg({
#                 "Original Label": "first",
#                 "Currency": "first",
#                 "Unit": "first",
#                 **{col: "first" for col in fy_columns}
#             })
#         )

#         # 5️⃣ Sort FY columns chronologically
#         sorted_fy = sorted(fy_columns)
#         # Rename Normalized Label → Particulars
#         aggregated = aggregated.rename(columns={"Normalized Label": "Particulars"})

#         # Keep only Particulars + FY columns
#         final_df = aggregated[["Particulars"] + sorted_fy]

#         return final_df



# +++=+ New table merger ++++
# table_merger.py

# # table_merger.py

# import pandas as pd
# import re
# from typing import List


# class TableMerger:
#     """
#     Safely merges mapped financial tables.
#     Preserves metadata and prevents silent numeric loss.
#     """

#     def merge_tables(self, tables: List[pd.DataFrame]) -> pd.DataFrame:

#         # 1️⃣ Remove empty tables
#         tables = [t for t in tables if t is not None and not t.empty]

#         if not tables:
#             return pd.DataFrame()

#         # 2️⃣ Concatenate
#         merged = pd.concat(tables, ignore_index=True)

#         # 3️⃣ Detect FY columns
#         fy_columns = [col for col in merged.columns if col.startswith("FY")]

#         required_cols = ["Normalized Label", "Original Label", "Section"]

#         for col in required_cols:
#             if col not in merged.columns:
#                 raise ValueError(f"Missing required column: {col}")

#         # Optional metadata
#         metadata_cols = [c for c in ["Currency", "Unit"] if c in merged.columns]

#         # 4️⃣ Convert numeric columns safely
#         for col in fy_columns:
#             merged[col] = pd.to_numeric(merged[col], errors="coerce")

#         # 5️⃣ Aggregate safely (sum instead of first)
#         aggregation_dict = {
#             "Original Label": "first",
#             "Section": "first",
#         }

#         for col in metadata_cols:
#             aggregation_dict[col] = "first"

#         for col in fy_columns:
#             aggregation_dict[col] = "sum"

#         aggregated = (
#             merged
#             .groupby("Normalized Label", as_index=False)
#             .agg(aggregation_dict)
#         )

#         # 6️⃣ Sort FY columns chronologically
#         sorted_fy = self._sort_fy_columns(fy_columns)

#         # 7️⃣ Rename Normalized Label → Particulars
#         aggregated = aggregated.rename(columns={"Normalized Label": "Particulars"})

#         # 8️⃣ Final column order
#         final_columns = (
#             ["Particulars", "Section"] +
#             metadata_cols +
#             sorted_fy
#         )

#         final_df = aggregated[final_columns]

#         return final_df

#     # --------------------------------------------------
#     # Helper: Proper FY sorting
#     # --------------------------------------------------

#     def _sort_fy_columns(self, fy_columns):

#         def fy_key(col):
#             match = re.match(r"FY(\d+)_Q(\d+)", col)
#             if match:
#                 year = int(match.group(1))
#                 quarter = int(match.group(2))
#                 return (year, quarter)
#             return (9999, 9999)

#         return sorted(fy_columns, key=fy_key)



# table_merger.py

import pandas as pd
import re
from typing import List


class TableMerger:
    """
    Safely merges mapped financial tables into a final analyst-ready format.
    Preserves numeric data and merges duplicates.
    Returns only 'Particulars' + FY columns.
    """

    def merge_tables(self, tables: List[pd.DataFrame]) -> pd.DataFrame:

        # 1️⃣ Remove empty tables
        tables = [t for t in tables if t is not None and not t.empty]

        if not tables:
            return pd.DataFrame()

        # 2️⃣ Concatenate all tables
        merged = pd.concat(tables, ignore_index=True)

        # 3️⃣ Detect FY columns dynamically
        fy_columns = [col for col in merged.columns if col.startswith("FY")]
        if not fy_columns:
            raise ValueError("No FY columns detected in tables.")

        # Ensure 'Normalized Label' exists for grouping
        if "Normalized Label" not in merged.columns:
            raise ValueError("Column 'Normalized Label' missing in tables.")

        # 4️⃣ Convert FY columns to numeric safely
        for col in fy_columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

        # 5️⃣ Merge duplicate line items
        aggregation_dict = {col: "sum" for col in fy_columns}

        aggregated = (
            merged
            .groupby("Normalized Label", as_index=False)
            .agg(aggregation_dict)
        )

        # 6️⃣ Sort FY columns chronologically
        sorted_fy = self._sort_fy_columns(fy_columns)

        # 7️⃣ Rename Normalized Label → Particulars
        aggregated = aggregated.rename(columns={"Normalized Label": "Particulars"})

        # 8️⃣ Keep only Particulars + sorted FY columns
        final_df = aggregated[["Particulars"] + sorted_fy]

        return final_df

    # -------------------------------
    # Helper: Proper FY sorting
    # -------------------------------
    def _sort_fy_columns(self, fy_columns: List[str]) -> List[str]:
        def fy_key(col):
            # Handles FYXX_QX or just FYXX formats
            match = re.match(r"FY(\d+)(?:_Q(\d+))?", col)
            if match:
                year = int(match.group(1))
                quarter = int(match.group(2)) if match.group(2) else 0
                return (year, quarter)
            return (9999, 9999)

        return sorted(fy_columns, key=fy_key)
