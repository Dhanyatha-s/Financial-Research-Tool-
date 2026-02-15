# import pandas as pd
# import re
# from rapidfuzz import process, fuzz

# try:
#     from mappings import STANDARD_LINE_ITEMS
# except ImportError:
#     STANDARD_LINE_ITEMS = {}

# class FinancialProcessor:

#     def __init__(self, df, metadata=None):

#         if df is None or df.empty:
#             raise ValueError("Input DataFrame is empty")

#         self.df = df.copy()
#         self.metadata = metadata or {}

#         # Drop empty columns
#         self.df = self.df.loc[:, ~self.df.columns.astype(str).str.contains('^Unnamed')]

#         # Remove serial number column
#         first_col = str(self.df.columns[0]).lower()
#         if any(term in first_col for term in ["si", "sl", "no", "s.no"]):
#             self.df.drop(self.df.columns[0], axis=1, inplace=True)

#         # Rename first column as Particulars
#         cols = list(self.df.columns)
#         cols[0] = "Particulars"
#         self.df.columns = cols

#         self.year_columns = []
#         self.structured_df = None

#         # Fuzzy match cache (performance boost)
#         self._fuzzy_cache = {}

#     # ------------------------------------------------
#     # FAST NUMBER CLEANING (vectorized friendly)
#     # ------------------------------------------------
#     def clean_number(self, value):

#         if pd.isna(value):
#             return None

#         val = str(value).strip()

#         is_negative = "(" in val and ")" in val

#         clean = re.sub(r'[^0-9.\-]', '', val)

#         if clean == "":
#             return None

#         try:
#             num = float(clean)
#             return -num if is_negative else num
#         except:
#             return None

#     # ------------------------------------------------
#     # YEAR NORMALIZATION
#     # ------------------------------------------------
#     def normalize_year_columns(self):

#         new_cols = []
#         year_cols = []

#         for i, col in enumerate(self.df.columns):

#             if i == 0:
#                 new_cols.append("Particulars")
#                 continue

#             col_str = str(col).lower()
#             match = re.search(r'20(\d{2})', col_str)

#             if match:
#                 fy = f"FY{match.group(1)}"
#                 new_cols.append(fy)
#                 year_cols.append(fy)
#             else:
#                 new_cols.append(col)

#         self.df.columns = new_cols
#         self.year_columns = year_cols

#     # ------------------------------------------------
#     # NORMALIZE TEXT
#     # ------------------------------------------------
#     def normalize_text(self, text):

#         if pd.isna(text):
#             return ""

#         text = str(text).lower().strip()
#         text = re.sub(r'[^a-z0-9\s]', '', text)

#         return text

#     # ------------------------------------------------
#     # FUZZY MATCH (CACHED)
#     # ------------------------------------------------
#     def fuzzy_map_line_item(self, name):

#         if not STANDARD_LINE_ITEMS:
#             return name

#         name_clean = self.normalize_text(name)

#         if name_clean in self._fuzzy_cache:
#             return self._fuzzy_cache[name_clean]

#         match = process.extractOne(
#             name_clean,
#             STANDARD_LINE_ITEMS.keys(),
#             scorer=fuzz.token_sort_ratio,
#             score_cutoff=85
#         )

#         mapped = STANDARD_LINE_ITEMS[match[0]] if match else name

#         self._fuzzy_cache[name_clean] = mapped
#         return mapped

#     # ------------------------------------------------
#     # DETECT CURRENCY & UNITS
#     # ------------------------------------------------
#     def detect_currency_units(self):

#         text_blob = " ".join(self.df["Particulars"].astype(str).tolist()).lower()

#         currency = "Unknown"
#         if "rs" in text_blob or "₹" in text_blob:
#             currency = "INR"
#         elif "$" in text_blob:
#             currency = "USD"
#         elif "€" in text_blob:
#             currency = "EUR"

#         unit = "Units"
#         if "lakhs" in text_blob:
#             unit = "Lakhs"
#         elif "crores" in text_blob:
#             unit = "Crores"
#         elif "million" in text_blob:
#             unit = "Million"

#         return currency, unit

#     # ------------------------------------------------
#     # BUILD STRUCTURE
#     # ------------------------------------------------
#     def build_structure(self):

#         self.normalize_year_columns()

#         currency, unit = self.detect_currency_units()

#         structured_rows = []

#         for _, row in self.df.iterrows():

#             particulars = row["Particulars"]

#             if pd.isna(particulars) or str(particulars).strip() == "":
#                 continue

#             row_data = {
#                 "Original Label": particulars,
#                 "Normalized Label": self.fuzzy_map_line_item(particulars),
#                 "Currency": currency,
#                 "Unit": unit
#             }

#             for col in self.year_columns:
#                 row_data[col] = self.clean_number(row.get(col))

#             structured_rows.append(row_data)

#         self.structured_df = pd.DataFrame(structured_rows)

#         return self.structured_df





# import pandas as pd
# import re
# from rapidfuzz import process, fuzz

# try:
#     from mapping import STANDARD_LINE_ITEMS
# except ImportError:
#     STANDARD_LINE_ITEMS = {}


# class FinancialProcessor:

#     def __init__(self, df, metadata=None):

#         if df is None or df.empty:
#             raise ValueError("Input DataFrame is empty")

#         self.df = df.copy()
#         self.metadata = metadata or {}

#         # Drop empty columns
#         self.df = self.df.loc[:, ~self.df.columns.astype(str).str.contains('^Unnamed')]

#         # 🔥 Detect header row first
#         self.detect_and_set_header()
#         self.detect_and_set_date_row()

#         # Remove serial number column if exists
#         first_col = str(self.df.columns[0]).lower()
#         if any(term in first_col for term in ["si", "sl", "no", "s.no"]):
#             self.df.drop(self.df.columns[0], axis=1, inplace=True)

#         # Rename first column as Particulars
#         cols = list(self.df.columns)
#         cols[0] = "Particulars"
#         self.df.columns = cols

#         self.year_columns = []
#         self.structured_df = None

#         self._fuzzy_cache = {}

#     # ------------------------------------------------
#     # HEADER DETECTION
#     # ------------------------------------------------
#     def detect_and_set_header(self):
#         for idx, row in self.df.iterrows():

#             # Convert entire row safely to string first
#             row_values = [str(x) for x in row.tolist()]
#             row_text = " ".join(row_values).lower()

#             if "particulars" in row_text and ("quarter" in row_text or "ended" in row_text):
#                 self.df.columns = self.df.iloc[idx]
#                 self.df = self.df.iloc[idx + 1:]
#                 self.df.reset_index(drop=True, inplace=True)
#                 print("✅ Header row detected and set.")
#                 return

#         print("⚠ Header row not clearly detected.")

#     def detect_and_set_date_row(self):

#         for idx in range(len(self.df) - 1):

#             row_text = " ".join(str(x) for x in self.df.iloc[idx].tolist())
#             next_row_text = " ".join(str(x) for x in self.df.iloc[idx + 1].tolist())

#             # Look for date pattern in next row
#             if re.search(r'\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{4}', next_row_text):

#                 print("✅ Multi-row header detected and merged.")

#                 header_row = self.df.iloc[idx]
#                 date_row = self.df.iloc[idx + 1]

#                 new_cols = ["Particulars"]

#                 for h, d in zip(header_row.tolist()[1:], date_row.tolist()[1:]):
#                     new_cols.append(str(d))

#                 self.df.columns = new_cols
#                 self.df = self.df.iloc[idx + 2:]
#                 self.df.reset_index(drop=True, inplace=True)
#                 return
#         print("Header row used:", header_row.tolist())
#         print("Date row used:", date_row.tolist())
#         print("⚠ No proper date row found.")


#         # ------------------------------------------------
#     # FAST NUMBER CLEANING
#     # ------------------------------------------------
#     def clean_number(self, value):

#         if pd.isna(value):
#             return None

#         val = str(value).strip()

#         is_negative = "(" in val and ")" in val

#         clean = re.sub(r'[^0-9.\-]', '', val)

#         if clean == "":
#             return None

#         try:
#             num = float(clean)
#             return -num if is_negative else num
#         except:
#             return None

#     # ------------------------------------------------
#     # PERIOD NORMALIZATION (Quarter + FY logic)
#     # ------------------------------------------------
#     def normalize_year_columns(self):

#         new_cols = []
#         year_cols = []

#         for i, col in enumerate(self.df.columns):

#             if i == 0:
#                 new_cols.append("Particulars")
#                 continue

#             col_str = str(col)

#             # More flexible date pattern
#             match = re.search(r'(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})', col_str)

#             if match:

#                 day, month, year = match.groups()
#                 month = int(month)
#                 year = int(year)

#                 # Indian Financial Year Logic
#                 if month in [4, 5, 6]:
#                     quarter = "Q1"
#                 elif month in [7, 8, 9]:
#                     quarter = "Q2"
#                 elif month in [10, 11, 12]:
#                     quarter = "Q3"
#                 else:
#                     quarter = "Q4"

#                 fy = year if month >= 4 else year - 1
#                 fy_col = f"FY{str(fy)[-2:]}_{quarter}"

#                 new_cols.append(fy_col)
#                 year_cols.append(fy_col)

#             else:
#                 new_cols.append(col)

#         self.df.columns = new_cols
#         self.year_columns = year_cols

#         print("Detected Period Columns:", self.year_columns)


#     # ------------------------------------------------
#     # NORMALIZE TEXT
#     # ------------------------------------------------
#     def normalize_text(self, text):

#         if pd.isna(text):
#             return ""

#         text = str(text).lower().strip()
#         text = re.sub(r'[^a-z0-9\s]', '', text)

#         return text

#     # ------------------------------------------------
#     # FUZZY MATCH
#     # ------------------------------------------------
#     def fuzzy_map_line_item(self, name):

#         if not STANDARD_LINE_ITEMS:
#             return name

#         name_clean = self.normalize_text(name)

#         if name_clean in self._fuzzy_cache:
#             return self._fuzzy_cache[name_clean]

#         match = process.extractOne(
#             name_clean,
#             STANDARD_LINE_ITEMS.keys(),
#             scorer=fuzz.token_sort_ratio,
#             score_cutoff=85
#         )

#         mapped = STANDARD_LINE_ITEMS[match[0]] if match else name

#         self._fuzzy_cache[name_clean] = mapped
#         return mapped

#     # ------------------------------------------------
#     # DETECT CURRENCY & UNITS
#     # ------------------------------------------------
#     # def detect_currency_units(self):

#     #     text_blob = " ".join(self.df.astype(str).values.flatten()).lower()

#     #     currency = "Unknown"
#     #     if "₹" in text_blob or "rs" in text_blob:
#     #         currency = "INR"
#     #     elif "$" in text_blob:
#     #         currency = "USD"
#     #     elif "€" in text_blob:
#     #         currency = "EUR"

#     #     unit = "Units"
#     #     if "lakhs" in text_blob:
#     #         unit = "Lakhs"
#     #     elif "crores" in text_blob:
#     #         unit = "Crores"
#     #     elif "million" in text_blob:
#     #         unit = "Million"

#     #     return currency, unit
#     def detect_currency_units(self):

#         # Convert everything safely to string first
#         flat_values = self.df.values.flatten()

#         safe_strings = []
#         for val in flat_values:
#             if pd.isna(val):
#                 continue
#             safe_strings.append(str(val))

#         text_blob = " ".join(safe_strings).lower()

#         currency = "Unknown"
#         if "₹" in text_blob or "rs" in text_blob:
#             currency = "INR"
#         elif "$" in text_blob:
#             currency = "USD"
#         elif "€" in text_blob:
#             currency = "EUR"

#         unit = "Units"
#         if "lakhs" in text_blob:
#             unit = "Lakhs"
#         elif "crores" in text_blob:
#             unit = "Crores"
#         elif "million" in text_blob:
#             unit = "Million"

#         return currency, unit


#     # ------------------------------------------------
#     # BUILD STRUCTURE
#     # ------------------------------------------------
#     def build_structure(self):


#         print("Columns before normalization:", list(self.df.columns))

#         self.normalize_year_columns()
#         if not self.year_columns:
#             print("⚠ Skipping table - no valid period columns detected.")
#             return pd.DataFrame()

#         currency, unit = self.detect_currency_units()

#         structured_rows = []

#         for _, row in self.df.iterrows():

#             particulars = row["Particulars"]

#             if pd.isna(particulars) or str(particulars).strip() == "":
#                 continue

#             # Skip header leftovers
#             if str(particulars).lower() in ["particulars", "quarter ended"]:
#                 continue

#             row_data = {
#                 "Original Label": particulars,
#                 "Normalized Label": self.fuzzy_map_line_item(particulars),
#                 "Currency": currency,
#                 "Unit": unit
#             }

#             for col in self.year_columns:
#                 row_data[col] = self.clean_number(row.get(col))

#             structured_rows.append(row_data)

#         self.structured_df = pd.DataFrame(structured_rows)

#         return self.structured_df



# ===== UNSTRCTURED ========
# financial_extraction.py

import pandas as pd
import re
from rapidfuzz import process, fuzz
from .unstructured_loader import UnstructuredLoader

try:
    from mapping import STANDARD_LINE_ITEMS
except ImportError:
    STANDARD_LINE_ITEMS = {}


class FinancialProcessor:

    def __init__(self, df, metadata=None):

        if df is None or df.empty:
            raise ValueError("Input DataFrame is empty")

        self.df = df.copy()
        self.metadata = metadata or {}

        # Drop unnamed columns
        self.df = self.df.loc[:, ~self.df.columns.astype(str).str.contains('^Unnamed')]

        # Detect header & date rows
        self.detect_and_set_header()
        self.detect_and_set_date_row()

        # Remove serial number column
        first_col = str(self.df.columns[0]).lower()
        if any(term in first_col for term in ["si", "sl", "no", "s.no", "l.no"]):
            self.df.drop(self.df.columns[0], axis=1, inplace=True)

        # Rename first column
        cols = list(self.df.columns)
        cols[0] = "Particulars"
        self.df.columns = cols

        self.year_columns = []
        self.structured_df = None
        self._fuzzy_cache = {}

    # ------------------------------------------------
    # HEADER DETECTION
    # ------------------------------------------------
    def detect_and_set_header(self):
        for idx, row in self.df.iterrows():

            row_values = [str(x) for x in row.tolist()]
            row_text = " ".join(row_values).lower()

            if "particulars" in row_text and ("quarter" in row_text or "ended" in row_text):
                self.df.columns = self.df.iloc[idx]
                self.df = self.df.iloc[idx + 1:]
                self.df.reset_index(drop=True, inplace=True)
                print("✅ Header row detected and set.")
                return

        print("⚠ Header row not clearly detected.")

    # ------------------------------------------------
    # MULTI ROW DATE HEADER
    # ------------------------------------------------
    def detect_and_set_date_row(self):

        for idx in range(len(self.df) - 1):

            row_text = " ".join(str(x) for x in self.df.iloc[idx].tolist())
            next_row_text = " ".join(str(x) for x in self.df.iloc[idx + 1].tolist())

            if re.search(r'\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{4}', next_row_text):

                print("✅ Multi-row header detected and merged.")

                header_row = self.df.iloc[idx]
                date_row = self.df.iloc[idx + 1]

                new_cols = ["Particulars"]

                for h, d in zip(header_row.tolist()[1:], date_row.tolist()[1:]):
                    new_cols.append(str(d))

                self.df.columns = new_cols
                self.df = self.df.iloc[idx + 2:]
                self.df.reset_index(drop=True, inplace=True)
                return

        print("⚠ No proper date row found.")

    # ------------------------------------------------
    # NUMBER CLEANING
    # ------------------------------------------------
    def clean_number(self, value):

        if pd.isna(value):
            return None

        val = str(value).strip()
        is_negative = "(" in val and ")" in val
        clean = re.sub(r'[^0-9.\-]', '', val)

        if clean == "":
            return None

        try:
            num = float(clean)
            return -num if is_negative else num
        except:
            return None

    # ------------------------------------------------
    # PERIOD NORMALIZATION
    # ------------------------------------------------
    def normalize_year_columns(self):

        new_cols = []
        year_cols = []
        seen = {}

        for i, col in enumerate(self.df.columns):

            if i == 0:
                new_cols.append("Particulars")
                continue

            col_str = str(col)

            match = re.search(r'(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})', col_str)

            if match:

                day, month, year = match.groups()
                month = int(month)
                year = int(year)

                if month in [4, 5, 6]:
                    quarter = "Q1"
                elif month in [7, 8, 9]:
                    quarter = "Q2"
                elif month in [10, 11, 12]:
                    quarter = "Q3"
                else:
                    quarter = "Q4"

                fy = year if month >= 4 else year - 1
                base_name = f"FY{str(fy)[-2:]}_{quarter}"

                # 🔥 Handle duplicates
                if base_name in seen:
                    seen[base_name] += 1
                    fy_col = f"{base_name}_{seen[base_name]}"
                else:
                    seen[base_name] = 1
                    fy_col = base_name

                new_cols.append(fy_col)
                year_cols.append(fy_col)

            else:
                new_cols.append(col)

        self.df.columns = new_cols
        self.year_columns = year_cols

        print("Detected Period Columns:", self.year_columns)


    # ------------------------------------------------
    # TEXT NORMALIZATION
    # ------------------------------------------------
    def normalize_text(self, text):

        if pd.isna(text):
            return ""

        text = str(text).lower().strip()
        text = re.sub(r'[^a-z0-9\s]', '', text)

        return text

    # ------------------------------------------------
    # FUZZY MAPPING
    # ------------------------------------------------
    def fuzzy_map_line_item(self, name):

        if not STANDARD_LINE_ITEMS:
            return name

        name_clean = self.normalize_text(name)

        if name_clean in self._fuzzy_cache:
            return self._fuzzy_cache[name_clean]

        match = process.extractOne(
            name_clean,
            STANDARD_LINE_ITEMS.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=85
        )

        mapped = STANDARD_LINE_ITEMS[match[0]] if match else name
        self._fuzzy_cache[name_clean] = mapped

        return mapped

    # ------------------------------------------------
    # CURRENCY + UNIT DETECTION
    # ------------------------------------------------
    def detect_currency_units(self):

        flat_values = self.df.values.flatten()
        safe_strings = [str(v) for v in flat_values if not pd.isna(v)]
        text_blob = " ".join(safe_strings).lower()

        currency = "Unknown"
        if "₹" in text_blob or "rs" in text_blob:
            currency = "INR"
        elif "$" in text_blob:
            currency = "USD"
        elif "€" in text_blob:
            currency = "EUR"

        unit = "Units"
        if "lakhs" in text_blob:
            unit = "Lakhs"
        elif "crores" in text_blob:
            unit = "Crores"
        elif "million" in text_blob:
            unit = "Million"

        return currency, unit

    # ------------------------------------------------
    # BUILD STRUCTURE
    # ------------------------------------------------
    def build_structure(self):

        print("Columns before normalization:", list(self.df.columns))

        self.normalize_year_columns()

        if not self.year_columns:
            print("⚠ Skipping table - no valid period columns detected.")
            return pd.DataFrame()

        currency, unit = self.detect_currency_units()

        structured_rows = []

        for _, row in self.df.iterrows():

            particulars = row["Particulars"]

            # 🔥 Clean OCR noise from labels
            particulars = str(particulars)
            particulars = re.sub(r'^[^a-zA-Z]+', '', particulars)  # remove leading symbols
            particulars = re.sub(r'[\[\]|_]+', '', particulars)    # remove junk characters
            particulars = particulars.strip()
            if particulars.replace('.', '', 1).isdigit():
                continue
            
            if len(particulars) < 3:
                continue

            if pd.isna(particulars) or str(particulars).strip() == "":
                continue

            if str(particulars).lower() in ["particulars", "quarter ended"]:
                continue

            row_data = {
                "Original Label": particulars,
                "Normalized Label": self.fuzzy_map_line_item(particulars),
                "Currency": currency,
                "Unit": unit
            }

            for col in self.year_columns:
                row_data[col] = self.clean_number(row.get(col))

            structured_rows.append(row_data)

        self.structured_df = pd.DataFrame(structured_rows)
        return self.structured_df


# ==========================================================
# MASTER PIPELINE (UNSTRUCTURED → FINANCIAL PROCESSOR)
# ==========================================================

def extract_financial_data(pdf_path):

    loader = UnstructuredLoader(pdf_path)
    raw_tables = loader.extract_tables()

    all_structured = []

    for i, table in enumerate(raw_tables):
        print(f"\nProcessing Table {i+1}")
        try:
            processor = FinancialProcessor(table)
            structured = processor.build_structure()

            if not structured.empty:
                all_structured.append(structured)

        except Exception as e:
            print(f"Error processing table {i+1}: {e}")

    if not all_structured:
        return pd.DataFrame()

    final_df = pd.concat(all_structured, ignore_index=True)

    return all_structured
