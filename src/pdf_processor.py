import os
from pdf2image import convert_from_path
from typing import List

class PDFProcessor:
    def __init__(self, output_dir: str = "data/images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_images(self, pdf_path: str, fmt: str = "jpeg") -> List[str]:
        """
        Converts PDF pages to images and saves them.
        Returns a list of paths to the generated images.
        """
        print(f"Converting PDF: {pdf_path}...")
        pages = convert_from_path(pdf_path)
        image_paths = []
        
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        for i, page in enumerate(pages):
            image_name = f"{pdf_name}_page_{i+1:03d}.{fmt}"
            image_path = os.path.join(self.output_dir, image_name)
            page.save(image_path, fmt.upper())
            image_paths.append(image_path)
            print(f"Saved: {image_path}")
            
        return image_paths

if __name__ == "__main__":
    # Test block (requires a sample.pdf)
    # processor = PDFProcessor()
    # try:
    #     paths = processor.extract_images("sample.pdf")
    #     print(f"Extracted {len(paths)} images")
    # except Exception as e:
    #     print(f"Error: {e}")
    pass
