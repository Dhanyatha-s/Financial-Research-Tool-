# from financial_extrcator import extract_financial_data


# df = extract_financial_data("input.pdf")

# print(df.head())


from financial_extrcator import extract_financial_data
from table_merger import TableMerger
from eda_analsis import EDAAnalyzer

PDF_PATH = "input.pdf"

print("\n=== STEP 1: FINANCIAL EXTRACTION ===")
structured_tables = extract_financial_data(PDF_PATH)

print(f"\nTables returned: {len(structured_tables)}")

for i, table in enumerate(structured_tables):
    print(f"\nTable {i+1} Preview:")
    print(table.head())

# --------------------------------------------------
# STEP 2: TABLE MERGING
# --------------------------------------------------

print("\n=== STEP 2: TABLE MERGING ===")
merger = TableMerger()
merged_df = merger.merge_tables(structured_tables)

print("\nMerged Shape:", merged_df.shape)
print("\nMerged Columns:")
print(list(merged_df.columns))

print("\nMerged Preview:")
print(merged_df.head())

# --------------------------------------------------
# STEP 3: EDA ANALYSIS
# --------------------------------------------------

print("\n=== STEP 3: EDA ANALYSIS ===")

if not merged_df.empty:
    eda = EDAAnalyzer(merged_df)
    report = eda.run_full_eda()
    print(report)
else:
    print("Merged dataframe is empty. Skipping EDA.")
