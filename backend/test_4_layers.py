import time
import pandas as pd

from backend.pdf_to_img import PDFToImage
from app.content_extraction import ContentExtractor
from financial_extrcator import FinancialProcessor
from table_merger import TableMerger
from eda_analsis import EDAAnalyzer



def main():

    pdf_path = "input.pdf"

    print("\n=== LAYER 1: PDF → IMAGES ===")
    start = time.time()

    pdf_converter = PDFToImage(pdf_path)
    images = pdf_converter.convert()

    print("Time:", round(time.time() - start, 2), "sec")
    print("Pages:", len(images))


    print("\n=== LAYER 2: OCR + TABLE EXTRACTION ===")
    start = time.time()

    extractor = ContentExtractor(images)
    raw_tables = extractor.extract()

    print("Time:", round(time.time() - start, 2), "sec")
    print("Tables extracted:", len(raw_tables))


    print("\n=== LAYER 3: FINANCIAL STRUCTURING ===")
    structured_tables = []

    for i, table in enumerate(raw_tables):
        try:
            processor = FinancialProcessor(df=table)
            structured = processor.build_structure()

            if not structured.empty:
                structured_tables.append(structured)

        except Exception as e:
            print(f"Error in table {i}: {e}")

    print("Structured tables:", len(structured_tables))


    print("\n=== LAYER 4: TABLE MERGING ===")

    merger = TableMerger()
    merged_df = merger.merge(structured_tables)

    print("\nMerged Shape:", merged_df.shape)
    print("\nColumns:", list(merged_df.columns))
    print("\nSample Output:\n")
    print(merged_df.head(20))


    # print("\n=== QUICK EDA READINESS CHECK ===")

    # # Check numeric columns
    # # numeric_cols = merged_df.columns[3:]
    # numeric_cols = [col for col in merged_df.columns if col.startswith("FY")]


    # print("Numeric Columns:", numeric_cols)

    # print("\nNull Summary:")
    # print(merged_df[numeric_cols].isna().sum())

    # if not merged_df.empty and "Normalized Label" in merged_df.columns:
    #     print("\nUnique Line Items:", merged_df["Normalized Label"].nunique())
    # else:
        # print("\nNo structured data available.")

    print("\n=== LAYER 5: EDA ANALYSIS ===")

    if not merged_df.empty:
        eda = EDAAnalyzer(merged_df)
        eda.print_report()
    else:
        print("No structured data available.")



if __name__ == "__main__":
    main()
