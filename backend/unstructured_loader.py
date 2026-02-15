# import os
# import io  # Required to fix the [Errno 2] error
# import pandas as pd
# from unstructured.partition.pdf import partition_pdf

# class ContentExtractor:
#     def __init__(self, pdf_path, poppler_path=r"C:\Program Files\poppler-25.12.0\Library\bin"):
#         self.pdf_path = pdf_path
#         self.poppler_path = poppler_path

#     def clean_extracted_table(self, df):
#         """Removes completely empty rows/columns and fixes headers."""
#         # Drop rows and columns that are entirely NaN
#         df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        
#         # Financial statements often have artifacts like 'Unnamed' or '.'
#         # This replaces them with empty strings for a cleaner look
#         df.columns = ["" if "Unnamed" in str(col) else col for col in df.columns]
#         return df.reset_index(drop=True)

#     def extract(self):
#         if not os.path.exists(self.pdf_path):
#             print(f"Error: File {self.pdf_path} not found.")
#             return []

#         print(f"Processing: {os.path.basename(self.pdf_path)}...")

#         try:
#             elements = partition_pdf(
#                 filename=self.pdf_path,
#                 strategy="hi_res",
#                 infer_table_structure=True,
#                 model_name="yolox",
#                 hi_res_model_name="yolox"
#             )
#         except Exception as e:
#             print(f"Error during partition: {e}")
#             return []

#         all_tables = []
        
#         for element in elements:
#             if element.category == "Table":
#                 html_str = element.metadata.text_as_html
                
#                 if html_str:
#                     try:
#                         # FIX: Use io.StringIO to treat the HTML string as a stream
#                         # This prevents Pandas from mistaking long HTML for a file path
#                         html_io = io.StringIO(html_str)
#                         dfs = pd.read_html(html_io)
                        
#                         if dfs:
#                             # Clean the data before adding to list
#                             cleaned_df = self.clean_extracted_table(dfs[0])
#                             all_tables.append(cleaned_df)
#                     except Exception as e:
#                         print(f"Table parsing error: {e}")

#         return all_tables

# if __name__ == "__main__":
#     pdf_file = "input.pdf" 
    
#     extractor = ContentExtractor(pdf_file)
#     tables = extractor.extract()

#     print(f"\nSuccessfully extracted {len(tables)} tables.")

#     for i, df in enumerate(tables):
#         print(f"\n--- Table {i+1} ---")
#         # Displaying more rows to verify the Dabur financial structure
#         print(df.head(10)) 
        
#         # Save to CSV for inspection
#         df.to_csv(f"extracted_table_{i+1}.csv", index=False)
# #


# import os
# import io
# import pandas as pd
# import re
# from unstructured.partition.pdf import partition_pdf

# class ContentExtractor:
#     def __init__(self, pdf_path):
#         self.pdf_path = pdf_path

#     def clean_financial_table(self, df):
#         """Advanced cleaning for financial statement artifacts."""
#         # 1. Drop totally empty rows/cols
#         df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        
#         # 2. Fix combined numeric columns (e.g., '3,558.65 3,191.32')
#         # This splits cells containing two currency-formatted numbers
#         def split_merged_values(val):
#             if isinstance(val, str):
#                 # Pattern for numbers with commas/dots separated by space
#                 parts = re.findall(r'\(?\d[\d,.]*\)?', val)
#                 if len(parts) >= 2:
#                     return parts[0] # Take first part, adjust logic if you need second
#             return val

#         df = df.map(split_merged_values)
        
#         # 3. Standardize Headers
#         df.columns = ["" if "Unnamed" in str(col) else col for col in df.columns]
#         return df.reset_index(drop=True)

#     def extract(self):
#         print(f"Processing: {os.path.basename(self.pdf_path)}...")
#         try:
#             elements = partition_pdf(
#                 filename=self.pdf_path,
#                 strategy="hi_res",
#                 infer_table_structure=True, # Critical for HTML reconstruction
#                 hi_res_model_name="yolox"   # High accuracy model for layouts
#             )
            
#             all_tables = []
#             for el in elements:
#                 if el.category == "Table" and el.metadata.text_as_html:
#                     try:
#                         # Use StringIO to avoid [Errno 2] path errors
#                         html_io = io.StringIO(el.metadata.text_as_html)
#                         dfs = pd.read_html(html_io)
#                         if dfs:
#                             cleaned = self.clean_financial_table(dfs[0])
#                             all_tables.append(cleaned)
#                     except Exception as e:
#                         print(f"Parsing error: {e}")
#             return all_tables
#         except Exception as e:
#             print(f"Extraction error: {e}")
#             return []

# if __name__ == "__main__":
#     extractor = ContentExtractor("input.pdf")
#     tables = extractor.extract()
#     # Save the best quality results
#     for i, df in enumerate(tables):
#         df.to_csv(f"table_{i+1}_cleaned.csv", index=False)



# unstructured_loader.py

# import io
# import re
# import pandas as pd
# from unstructured.partition.pdf import partition_pdf


# class UnstructuredLoader:
#     def __init__(self, pdf_path):
#         self.pdf_path = pdf_path

#     def clean_table(self, df):
#         """
#         Cleans financial table artifacts
#         """

#         # Drop fully empty rows/cols
#         df = df.dropna(how="all").dropna(how="all", axis=1)

#         # Fix merged numeric cells
#         def split_values(val):
#             if isinstance(val, str):
#                 parts = re.findall(r'\(?\d[\d,\.]*\)?', val)
#                 if len(parts) >= 2:
#                     return parts[0]
#             return val

#         df = df.map(split_values)

#         # Clean column names
#         df.columns = [
#             "" if "Unnamed" in str(c) else str(c)
#             for c in df.columns
#         ]

#         return df.reset_index(drop=True)

#     def extract_tables(self):
#         elements = partition_pdf(
#             filename=self.pdf_path,
#             strategy="hi_res",
#             infer_table_structure=True,
#             hi_res_model_name="yolox"
#         )

#         tables = []

#         for el in elements:
#             if el.category == "Table" and el.metadata.text_as_html:
#                 html_io = io.StringIO(el.metadata.text_as_html)
#                 dfs = pd.read_html(html_io)

#                 if dfs:
#                     cleaned = self.clean_table(dfs[0])
#                     tables.append(cleaned)

#         print(f"Extracted {len(tables)} tables.")
#         return tables


import io
import re
import pandas as pd
from unstructured.partition.pdf import partition_pdf

class UnstructuredLoader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def clean_table(self, df):
        # Optimization: Use vectorized pandas operations instead of element-wise map
        df = df.dropna(how="all").dropna(how="all", axis=1)
        
        # Regex cleanup for merged numeric cells
        def split_values(val):
            if isinstance(val, str):
                parts = re.findall(r'\(?\d[\d,\.]*\)?', val)
                if len(parts) >= 2: return parts[0]
            return val
            
        df = df.map(split_values)
        df.columns = ["" if "Unnamed" in str(c) else str(c) for c in df.columns]
        return df.reset_index(drop=True)

    def extract_tables(self):
        # SPEED OPTIMIZATIONS:
        # 1. strategy="auto": Switches between 'fast' and 'hi_res' per page.
        # 2. split_pdf_page=True: Enables multi-threading/parallelism.
        # 3. split_pdf_concurrency_level=10: Process 10 pages at once (Max: 15).
        elements = partition_pdf(
            filename=self.pdf_path,
            strategy="auto", 
            infer_table_structure=True,
            split_pdf_page=True,
            split_pdf_concurrency_level=10,
            hi_res_model_name="yolox"
        )

        tables = []
        for el in elements:
            # Only process if table structure was successfully inferred
            if el.category == "Table" and getattr(el.metadata, "text_as_html", None):
                html_io = io.StringIO(el.metadata.text_as_html)
                dfs = pd.read_html(html_io)

                if dfs:
                    tables.append(self.clean_table(dfs[0]))

        print(f"Extracted {len(tables)} tables.")
        return tables
