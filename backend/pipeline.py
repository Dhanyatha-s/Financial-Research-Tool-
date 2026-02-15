# main.py

# import os
# import pandas as pd
# from .pdf_to_img import PDFToImage
# from unstructured_loader import UnstructuredLoader
# from financial_extrcator import FinancialProcessor
# from semantic_classifier import StatementClassifier
# from llm_mapper import LLMMapper
# from table_merger import TableMerger
# from validator import FinancialValidator
# from openpyxl import load_workbook
# from openpyxl.styles import PatternFill, Font

# # -----------------------------
# # Step 0: Helper - Export to Excel with highlights
# # -----------------------------
# def export_financial_excel(df: pd.DataFrame, output_path="financial_report.xlsx"):
#     df_filled = df.copy()

#     # Replace missing numeric values
#     year_cols = [c for c in df.columns if c.startswith("FY")]
#     for col in year_cols:
#         df_filled[col] = pd.to_numeric(df[col], errors="coerce")
#         df_filled[col] = df_filled[col].fillna("MISSING")

#     df_filled.to_excel(output_path, index=False, sheet_name="Financials")

#     # Conditional formatting
#     from openpyxl import load_workbook
#     wb = load_workbook(output_path)
#     ws = wb["Financials"]

#     missing_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#     negative_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
#     bold_font = Font(bold=True)

#     # Identify FY columns
#     col_indices = {cell.value: cell.column for cell in ws[1] if str(cell.value).startswith("FY")}

#     for col_name, col_idx in col_indices.items():
#         for row in range(2, ws.max_row + 1):
#             cell = ws.cell(row=row, column=col_idx)
#             if cell.value == "MISSING":
#                 cell.fill = missing_fill
#                 cell.font = bold_font
#             elif isinstance(cell.value, (int, float)):
#                 if cell.value < 0:
#                     cell.fill = negative_fill

#     wb.save(output_path)
#     print(f"✅ Excel exported with highlights: {output_path}")


# # -----------------------------
# # Main Pipeline
# # -----------------------------
# def main():
#     print("=== Research Tool: Financial Statement Extraction ===")
#     pdf_path = input("Enter PDF file path: ").strip()

#     if not os.path.exists(pdf_path):
#         print("❌ File not found. Please check path.")
#         return

#     # Step 1: Extract tables from PDF
#     print("\n📥 Extracting tables from PDF...")
#     loader = UnstructuredLoader(pdf_path)
#     raw_tables = loader.extract_tables()

#     if not raw_tables:
#         print("❌ No tables found in PDF.")
#         return

#     # Step 2: Process each table into structured data
#     print("\n🔧 Processing tables...")
#     structured_tables = []
#     for i, table in enumerate(raw_tables):
#         print(f"Processing Table {i+1}")
#         processor = FinancialProcessor(table)
#         structured = processor.build_structure()
#         if structured is not None and not structured.empty:
#             structured_tables.append(structured)

#     if not structured_tables:
#         print("❌ No structured data extracted.")
#         return

#     # Step 3: Classify statements
#     print("\n🧾 Classifying statements...")
#     classifier = StatementClassifier()
#     grouped = classifier.classify_all(structured_tables)

#     # Step 4: LLM-based mapping
#     print("\n🤖 Mapping line items via LLM...")
#     mapper = LLMMapper()
#     mapped_tables = []
#     for stmt_type, tables in grouped.items():
#         if tables:
#             mapped = mapper.process_and_map(tables)
#             mapped_tables.extend(mapped)

#     if not mapped_tables:
#         print("❌ No mapped tables found.")
#         return

#     # Step 5: Merge all mapped tables
#     print("\n🔗 Merging tables...")
#     merger = TableMerger()
#     merged_df = merger.merge_tables(mapped_tables)

#     if merged_df.empty:
#         print("❌ Merged DataFrame is empty.")
#         return

#     # Step 6: Validation
#     print("\n🔍 Validating financial data...")
#     year_cols = [c for c in merged_df.columns if str(c).startswith("FY")]
#     validator = FinancialValidator(merged_df, year_cols)
#     validation_result = validator.validate()
#     print("\n💡 Validation Alerts:")
#     for alert in validation_result["alerts"]:
#         print(f"- {alert}")

#     # Step 7: Export to Excel with highlights
#     print("\n📊 Exporting to Excel...")
#     export_financial_excel(merged_df, "financial_report.xlsx")

#     print("\n✅ Pipeline completed successfully!")


# if __name__ == "__main__":
#     main()

# WORKING=========================================
# main.py

# import os
# import pandas as pd
# from pdf_to_img import PDFToImage
# from unstructured_loader import UnstructuredLoader
# from financial_extrcator import extract_financial_data
# from semantic_classifier import StatementClassifier
# from llm_mapper import LLMMapper
# from table_merger import TableMerger
# from validator import FinancialValidator
# from openpyxl import Workbook
# from openpyxl.styles import PatternFill

# # -----------------------------
# # Step 1: User Upload PDF
# # -----------------------------
# pdf_path = input("Enter path to PDF: ").strip()

# if not os.path.exists(pdf_path):
#     print("❌ PDF file not found. Exiting.")
#     exit()

# print(f"📄 Processing PDF: {pdf_path}")

# # -----------------------------
# # Step 2: Extract Tables
# # -----------------------------
# raw_tables = extract_financial_data(pdf_path)

# if not raw_tables:
#     print("⚠ No tables extracted from PDF.")
#     exit()

# print(f"✅ Extracted {len(raw_tables)} tables.")

# # -----------------------------
# # Step 3: Classify Tables
# # -----------------------------
# classifier = StatementClassifier()
# grouped_tables = classifier.classify_all(raw_tables)

# # For this example, we focus on Income Statement tables
# income_tables = grouped_tables.get("Income Statement", [])

# if not income_tables:
#     print("⚠ No Income Statement tables detected.")
#     exit()

# print(f"✅ {len(income_tables)} Income Statement tables detected.")

# # -----------------------------
# # Step 4: LLM + Standard Mapping
# # -----------------------------
# mapper = LLMMapper()
# mapped_tables = mapper.process_and_map(income_tables)

# # -----------------------------
# # Step 5: Merge Tables
# # -----------------------------
# merger = TableMerger()
# merged_df = merger.merge_tables(mapped_tables)

# if merged_df.empty:
#     print("⚠ Merged table is empty.")
#     exit()

# print("✅ Tables merged successfully.")

# # -----------------------------
# # Step 6: Validation
# # -----------------------------
# year_cols = [col for col in merged_df.columns if col.startswith("FY")]
# validator = FinancialValidator(merged_df, year_cols)
# validation_result = validator.validate()

# print(f"Validation Score: {validation_result['validation_score']}%")
# print("Alerts:", validation_result['alerts'])

# # -----------------------------
# # Step 7: Export to Excel
# # -----------------------------
# output_file = os.path.splitext(os.path.basename(pdf_path))[0] + "_financial.xlsx"
# merged_df.to_excel(output_file, index=False)
# print(f"✅ Excel saved: {output_file}")

# # -----------------------------
# # Step 8: Conditional Formatting for Missing / Ambiguous Data
# # -----------------------------
# from openpyxl import load_workbook

# wb = load_workbook(output_file)
# ws = wb.active

# # Highlight missing / NaN numbers in yellow
# yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
# # Highlight negative values in red
# red_fill = PatternFill(start_color="FF6666", end_color="FF6666", fill_type="solid")

# for row in range(2, ws.max_row + 1):
#     for col_idx in range(2, ws.max_column + 1):  # Skip 'Particulars' column
#         cell = ws.cell(row=row, column=col_idx)
#         try:
#             val = float(cell.value)
#             if pd.isna(val):
#                 cell.fill = yellow_fill
#             elif val < 0:
#                 cell.fill = red_fill
#         except:
#             # Non-numeric value → highlight yellow as ambiguous
#             cell.fill = yellow_fill

# wb.save(output_file)
# print(f"✅ Conditional formatting applied and saved to: {output_file}")



# pipeline.py

# import os
# import pandas as pd
# from .pdf_to_img import PDFToImage
# from .unstructured_loader import UnstructuredLoader
# from .financial_extrcator import extract_financial_data
# from .semantic_classifier import StatementClassifier
# from .llm_mapper import LLMMapper
# from .table_merger import TableMerger
# from .validator import FinancialValidator

# def mainPipeline(pdf_path):
#     # -----------------------------
#     # Step 1: User Upload PDF
#     # -----------------------------
#     pdf_path = input("Enter path to PDF: ").strip()

#     if not os.path.exists(pdf_path):
#         print("❌ PDF file not found. Exiting.")
#         exit()

#     print(f"📄 Processing PDF: {pdf_path}")

#     # -----------------------------
#     # Step 2: Extract Tables
#     # -----------------------------
#     raw_tables = extract_financial_data(pdf_path)

#     if not raw_tables:
#         print("⚠ No tables extracted from PDF.")
#         exit()

#     print(f"✅ Extracted {len(raw_tables)} tables.")

#     # -----------------------------
#     # Step 3: Classify Tables
#     # -----------------------------
#     classifier = StatementClassifier()
#     grouped_tables = classifier.classify_all(raw_tables)

#     # Focus on Income Statement tables for now
#     income_tables = grouped_tables.get("Income Statement", [])

#     if not income_tables:
#         print("⚠ No Income Statement tables detected.")
#         exit()

#     print(f"✅ {len(income_tables)} Income Statement tables detected.")

#     # -----------------------------
#     # Step 4: LLM + Standard Mapping
#     # -----------------------------
#     mapper = LLMMapper()
#     mapped_tables = mapper.process_and_map(income_tables)

#     # -----------------------------
#     # Step 5: Merge Tables
#     # -----------------------------
#     merger = TableMerger()
#     merged_df = merger.merge_tables(mapped_tables)

#     if merged_df.empty:
#         print("⚠ Merged table is empty.")
#         exit()

#     print("✅ Tables merged successfully.")

#     # -----------------------------
#     # Step 6: Validation
#     # -----------------------------
#     year_cols = [col for col in merged_df.columns if col.startswith("FY")]
#     validator = FinancialValidator(merged_df, year_cols)
#     validation_result = validator.validate()

#     print(f"Validation Score: {validation_result['validation_score']}%")
#     print("Alerts:", validation_result['alerts'])

#     # -----------------------------
#     # Step 7: Export to Excel with Advanced Formatting
#     # -----------------------------
#     # -----------------------------
#     # Step 7: Export to Excel (Imported from excel_sheet.py)
#     # -----------------------------
#     from excel_sheet import export_financial_excel

#     # Create filename based on PDF name
#     # output_file = os.path.splitext(os.path.basename(pdf_path))[0] + "New_financial.xlsx"

#     # # Call the imported function
#     # export_financial_excel(merged_df, output_file)

#     # print(f"Process Complete! Final file: {output_file}")
#     output_file = os.path.splitext(os.path.basename(pdf_path))[0] + "_financial.xlsx"
#     export_financial_excel(merged_df, output_file)
#     print(f"Excel generated: {output_file}")
#     return output_file  

# # if __name__ == "__main__":
# #     # pdf_path = input("Enter path to PDF: ").strip()
# #     # mainPipeline(pdf_path)


# pipeline.py

# 



# pipeline.py

import os
import pandas as pd
from .pdf_to_img import PDFToImage
from .unstructured_loader import UnstructuredLoader
from .financial_extrcator import extract_financial_data
from .semantic_classifier import StatementClassifier
from .llm_mapper import LLMMapper
from .table_merger import TableMerger
from .validator import FinancialValidator

# Default output directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# os.makedirs(OUTPUT_DIR, exist_ok=True)

def mainPipeline(pdf_path: str, status_callback=None, filename=None):
    """
    Full financial PDF processing pipeline with status updates
    """

    # -----------------------------
    # Step 1: Check PDF
    # -----------------------------
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ PDF file not found: {pdf_path}")

    print(f"📄 Processing PDF: {pdf_path}")
    if status_callback and filename:
        status_callback(filename, "extracting", "📄 Validating PDF file...", 35)

    # -----------------------------
    # Step 2: Extract Tables
    # -----------------------------
    if status_callback and filename:
        status_callback(filename, "extracting", "📊 Extracting tables from PDF...", 40)
    
    raw_tables = extract_financial_data(pdf_path)
    if raw_tables is None or len(raw_tables) == 0:
        raise ValueError("⚠ No tables extracted from PDF.")


    print(f"✅ Extracted {len(raw_tables)} tables.")
    if status_callback and filename:
        status_callback(filename, "extracting", f"✅ Extracted {len(raw_tables)} tables", 45)

    # -----------------------------
    # Step 3: Classify Tables
    # -----------------------------
    if status_callback and filename:
        status_callback(filename, "classifying", "🔍 Classifying financial statements...", 50)
    
    classifier = StatementClassifier()
    grouped_tables = classifier.classify_all(raw_tables)

    income_tables = grouped_tables.get("Income Statement", [])
    if income_tables is None or len(income_tables) == 0:
        raise ValueError("⚠ No Income Statement tables detected.")


    print(f"✅ {len(income_tables)} Income Statement tables detected.")
    if status_callback and filename:
        status_callback(filename, "classifying", f"✅ Found {len(income_tables)} Income Statement tables", 55)

    # -----------------------------
    # Step 4: LLM + Standard Mapping
    # -----------------------------
    if status_callback and filename:
        status_callback(filename, "mapping", "🤖 Mapping financial data with AI...", 60)
    
    mapper = LLMMapper()
    mapped_tables = mapper.process_and_map(income_tables)
    
    if status_callback and filename:
        status_callback(filename, "mapping", "✅ Data mapping complete", 62)

    # -----------------------------
    # Step 5: Merge Tables
    # -----------------------------
    if status_callback and filename:
        status_callback(filename, "merging", "🔗 Merging tables...", 64)
    
    merger = TableMerger()
    merged_df = merger.merge_tables(mapped_tables)
    if merged_df is None or merged_df.empty:
        raise ValueError("⚠ Merged table is empty.")


    print("✅ Tables merged successfully.")
    if status_callback and filename:
        status_callback(filename, "merging", "✅ Tables merged successfully", 66)

    # -----------------------------
    # Step 6: Validation
    # -----------------------------
    if status_callback and filename:
        status_callback(filename, "validating", "✔️ Validating financial data...", 68)
    
    year_cols = [col for col in merged_df.columns if col.startswith("FY")]
    validator = FinancialValidator(merged_df, year_cols)
    validation_result = validator.validate()

    print(f"Validation Score: {validation_result['validation_score']}%")
    print("Alerts:", validation_result['alerts'])

    # -----------------------------
    # Step 7: Export to Excel
    # -----------------------------
    if status_callback and filename:
        status_callback(filename, "exporting", "📝 Generating Excel file...", 70)
    
    from .excel_sheet import export_financial_excel

    output_file_name = os.path.splitext(os.path.basename(pdf_path))[0] + "_financial.xlsx"
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    export_financial_excel(merged_df, output_file_path)
    print(f"✅ Excel generated: {output_file_path}")

    return output_file_path