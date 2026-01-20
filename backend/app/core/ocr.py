import fitz
import pytesseract
from PIL import Image
import io


def extract_text(path:str):
    doc = fitz.open(path)
    pages = []
    for i,page in enumerate(doc):
        text = page.get_text().strip()
        if len(text)<50:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)

        pages.append({"page": i+1,"text":text})

    return pages

