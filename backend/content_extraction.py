import os
import cv2
import pytesseract
import pandas as pd
from multiprocessing import Pool, cpu_count
from pdf_to_img import PDFToImage
import numpy as np


class ContentExtractor:

    def __init__(self, images,
                 tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):

        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.images = images

        # Kernels reused (faster)
        self.h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        self.v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

        # Fast config
        self.tess_config = r'--oem 1 --psm 4'


    # -----------------------------------
    # PUBLIC METHOD
    # -----------------------------------
    def extract(self):
        with Pool(cpu_count()) as pool:
            results = pool.map(self.process_single_image, self.images)

        return [df for sublist in results for df in sublist if df is not None]


    # -----------------------------------
    # PROCESS ONE IMAGE
    # -----------------------------------
    def process_single_image(self, image):

        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        if img is None:
            return []

        # Resize large images (speed boost)
        max_width = 2000
        if img.shape[1] > max_width:
            scale = max_width / img.shape[1]
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, self.h_kernel)
        vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, self.v_kernel)

        table_mask = cv2.add(horizontal, vertical)

        contours, _ = cv2.findContours(
            table_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        tables = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            if w > 200 and h > 100:
                padding = 20

                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(img.shape[1], x + w + padding)
                y2 = min(img.shape[0], y + h + padding)

                table_img = img[y1:y2, x1:x2]

                df = self.extract_table_with_data(table_img)

                if df is not None:
                    tables.append(df)

        return tables


    # -----------------------------------
    # FAST TABLE OCR USING image_to_data
    # -----------------------------------
    def extract_table_with_data(self, table_img):

        # Single OCR call for entire table
        data = pytesseract.image_to_data(
            table_img,
            config=self.tess_config,
            output_type=pytesseract.Output.DATAFRAME
        )

        # Remove empty text & low confidence
        data = data[
            (data.conf > 30) &
            (data.text.notna()) &
            (data.text.str.strip() != "")
        ]

        if data.empty:
            return None

        # Sort by vertical position first
        data = data.sort_values(by=["top", "left"])
        print("DATES FOUND:")
        print(data[data.text.str.contains(r'\d{2}/\d{2}/\d{4}', regex=True)])


        # rows = []
        # current_row = []
        # last_top = None
        # row_threshold = 15  # adjust if needed

        # for _, row in data.iterrows():
        #     top = row["top"]
        #     text = row["text"]
        #     left = row["left"]

        #     if last_top is None:
        #         last_top = top

        #     # New row detection
        #     if abs(top - last_top) > row_threshold:
        #         # Save previous row
        #         current_row = sorted(current_row, key=lambda x: x[0])
        #         rows.append([item[1] for item in current_row])
        #         current_row = []
        #         last_top = top

        #     current_row.append((left, text))

        # # Append final row
        # if current_row:
        #     current_row = sorted(current_row, key=lambda x: x[0])
        #     rows.append([item[1] for item in current_row])

        # if not rows:
        #     return None

        # return pd.DataFrame(rows)

        # Cluster rows
        rows = []
        row_threshold = 15
        current_row = []
        last_top = None

        for _, r in data.iterrows():
            top = r["top"]
            left = r["left"]
            text = r["text"]

            if last_top is None:
                last_top = top

            if abs(top - last_top) > row_threshold:
                rows.append(current_row)
                current_row = []
                last_top = top

            current_row.append((left, text))

        if current_row:
            rows.append(current_row)

        # -----------------------------
        # COLUMN ALIGNMENT FIX
        # -----------------------------

        # Collect all column X positions from first few rows
        all_lefts = sorted([item[0] for row in rows[:3] for item in row])

        # Cluster X positions
        col_positions = []
        col_threshold = 40

        for left in all_lefts:
            placed = False
            for i, pos in enumerate(col_positions):
                if abs(left - pos) < col_threshold:
                    col_positions[i] = int((pos + left) / 2)
                    placed = True
                    break
            if not placed:
                col_positions.append(left)

        col_positions = sorted(col_positions)

        # Build table with fixed columns
        structured_rows = []

        for row in rows:
            row_dict = {pos: "" for pos in col_positions}

            for left, text in row:
                closest_col = min(col_positions, key=lambda x: abs(x - left))
                row_dict[closest_col] += " " + text

            structured_rows.append([row_dict[pos].strip() for pos in col_positions])

        return pd.DataFrame(structured_rows)



# -----------------------------------
# USAGE
# -----------------------------------
# if __name__ == "__main__":

#     image_dir = "pdf_images"
#     valid_images = []

#     if os.path.exists(image_dir):
#         for f in os.listdir(image_dir):
#             if f.lower().endswith((".png", ".jpg", ".jpeg")):
#                 valid_images.append(os.path.join(image_dir, f))

#     if not valid_images:
#         print("No images found!")
#     else:
#         extractor = ContentExtractor(valid_images)
#         tables = extractor.extract()

#         print(f"\nExtracted {len(tables)} tables.")
