# import pandas as pd
# from openpyxl import load_workbook
# from openpyxl.styles import PatternFill, Font, Alignment
# from openpyxl.formatting.rule import CellIsRule, FormulaRule
# from openpyxl.worksheet.table import Table, TableStyleInfo

# def export_financial_excel(df: pd.DataFrame, output_path="financial_output.xlsx"):
#     """
#     Exports structured financial DataFrame to Excel.
#     Highlights:
#     - Missing numeric data (NaN or MISSING) → Yellow
#     - Negative numbers → Red
#     - Zero values → Orange
#     Formats as Excel Table for readability.
#     """

#     # ------------------------------
#     # Step 1: Replace ambiguous/missing values for clarity
#     # ------------------------------
#     df_filled = df.copy()
#     df_filled = df_filled.fillna("MISSING")

#     # Ensure numeric columns remain numeric (except MISSING)
#     year_cols = [c for c in df.columns if str(c).startswith("FY")]
#     for col in year_cols:
#         df_filled[col] = pd.to_numeric(df[col], errors="coerce")
#         df_filled[col] = df_filled[col].fillna("MISSING")

#     # ------------------------------
#     # Step 2: Export base Excel
#     # ------------------------------
#     df_filled.to_excel(output_path, index=False, sheet_name="Financials")
#     print(f"✅ Base Excel exported to {output_path}")

#     # ------------------------------
#     # Step 3: Load workbook and worksheet
#     # ------------------------------
#     wb = load_workbook(output_path)
#     ws = wb["Financials"]

#     # ------------------------------
#     # Step 4: Apply table formatting
#     # ------------------------------
#     table_range = f"A1:{chr(64 + ws.max_column)}{ws.max_row}"
#     tab = Table(displayName="FinancialTable", ref=table_range)

#     style = TableStyleInfo(
#         name="TableStyleMedium9",
#         showFirstColumn=False,
#         showLastColumn=False,
#         showRowStripes=True,
#         showColumnStripes=True
#     )
#     tab.tableStyleInfo = style
#     ws.add_table(tab)

#     # ------------------------------
#     # Step 5: Define fills and fonts
#     # ------------------------------
#     missing_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Yellow
#     negative_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Light Red
#     zero_fill = PatternFill(start_color="FFD966", end_color="FFD966", fill_type="solid")      # Orange
#     bold_font = Font(bold=True)
#     center_align = Alignment(horizontal="center")

#     # ------------------------------
#     # Step 6: Apply conditional formatting for each FY column
#     # ------------------------------
#     col_indices = {cell.value: cell.column for cell in ws[1] if str(cell.value).startswith("FY")}

#     for col_name, col_idx in col_indices.items():
#         col_letter = ws.cell(row=1, column=col_idx).column_letter

#         # Highlight missing or ambiguous values
#         ws.conditional_formatting.add(
#             f"{col_letter}2:{col_letter}{ws.max_row}",
#             FormulaRule(formula=[f'ISERROR({col_letter}2)'], stopIfTrue=True, fill=missing_fill)
#         )

#         # Highlight negative numbers
#         ws.conditional_formatting.add(
#             f"{col_letter}2:{col_letter}{ws.max_row}",
#             CellIsRule(operator='lessThan', formula=['0'], stopIfTrue=True, fill=negative_fill)
#         )

#         # Highlight zeros
#         ws.conditional_formatting.add(
#             f"{col_letter}2:{col_letter}{ws.max_row}",
#             CellIsRule(operator='equal', formula=['0'], stopIfTrue=True, fill=zero_fill)
#         )

#         # Center align numeric columns
#         for row in range(2, ws.max_row + 1):
#             cell = ws.cell(row=row, column=col_idx)
#             cell.alignment = center_align

#     # Bold the header row
#     for cell in ws[1]:
#         cell.font = Font(bold=True)

#     # Save final workbook
#     wb.save(output_path)
#     print(f"✅ Conditional formatting and table formatting applied. Excel saved to {output_path}")

# # ------------------------------
# # Example Usage
# # ------------------------------
# # if __name__ == "__main__":
# #     # Suppose final_df is your merged DataFrame from TableMerger
# #     # Example:
# #     final_df = pd.read_csv("merged_financial.csv")  # replace with your pipeline output
# #     export_financial_excel(final_df, "financial_report.xlsx")



import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
import re

# def export_financial_excel(df: pd.DataFrame, output_path="financial_output.xlsx"):
def export_financial_excel(df: pd.DataFrame, output_path: str):

    """
    Exports financial data with specific formatting: 
    - Bold headers for main sections (A, B, C, D) only.
    - Simple table style.
    - Conditional formatting for Missing (Yellow), Zero (Orange), and Negative (Red).
    """

    # 1. Prepare Data
    df_filled = df.copy()
    year_cols = [c for c in df.columns if str(c).startswith("FY")]
    
    for col in year_cols:
        df_filled[col] = pd.to_numeric(df[col], errors="coerce")

    # Save to Excel
    df_filled.to_excel(output_path, index=False, sheet_name="Financials")
    wb = load_workbook(output_path)
    ws = wb["Financials"]

    # ------------------------------
    # Table & Header Formatting
    # ------------------------------
    table_range = f"A1:{chr(64 + ws.max_column)}{ws.max_row}"
    tab = Table(displayName="FinancialTable", ref=table_range)
    # Using a cleaner, simpler style (Light1)
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(tab)

    header_fill = PatternFill(start_color="4B0082", end_color="4B0082", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # ------------------------------
    # Row-Level Formatting (Bold Main Headers Only)
    # ------------------------------
    # This regex looks for patterns like "A. ", "B. ", etc. at the start of the string
    header_pattern = re.compile(r'^[A-Z]\.\s')

    for row in range(2, ws.max_row + 1):
        particulars_cell = ws.cell(row=row, column=1)
        value = str(particulars_cell.value)

        if header_pattern.match(value):
            # Format ONLY main headers (A, B, C, D) as bold
            particulars_cell.font = Font(bold=True)
            for col in range(1, ws.max_column + 1):
                ws.cell(row=row, column=col).fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        else:
            # Sub-headers remain regular weight
            particulars_cell.font = Font(bold=False)

    # ------------------------------
    # Numeric & Conditional Formatting
    # ------------------------------
    missing_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Yellow
    zero_fill = PatternFill(start_color="FFD966", end_color="FFD966", fill_type="solid")     # Orange
    negative_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid") # Red light

    for col_idx, col_name in enumerate(df_filled.columns, start=1):
        if col_name in year_cols:
            for row in range(2, ws.max_row + 1):
                cell = ws.cell(row=row, column=col_idx)
                cell.alignment = Alignment(horizontal="right")
                
                val = cell.value
                if val is None:
                    cell.fill = missing_fill
                elif isinstance(val, (int, float)):
                    cell.number_format = '#,##0.00'
                    if val < 0:
                        cell.fill = negative_fill
                    elif val == 0:
                        cell.fill = zero_fill

    # Auto-adjust column width for readability
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2

    wb.save(output_path)
    print(f"✅ Success! Simplified table saved to: {output_path}")


