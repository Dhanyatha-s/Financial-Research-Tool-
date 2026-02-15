from pdf2image import convert_from_path

class PDFToImage:

    def __init__(self, pdf_path,
                 poppler_path=r"C:\Program Files\poppler-25.12.0\Library\bin"):

        self.pdf_path = pdf_path
        self.poppler_path = poppler_path

    def convert(self, dpi=200):
        """
        Returns list of PIL images in memory
        """

        try:
            images = convert_from_path(
                self.pdf_path,
                dpi=dpi,
                poppler_path=self.poppler_path
            )

            print(f"Loaded {len(images)} pages into memory.")
            return images

        except Exception as e:
            print(f"PDF conversion error: {e}")
            return []
