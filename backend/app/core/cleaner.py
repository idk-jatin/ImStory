import re

def clean_text(text: str):
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"-\s+", "", text)
    text = re.sub(r"\b[A-Za-z]+\s*:\s*", "", text)
    text = re.sub(r"\b\|\s*", "I ", text)
    text = re.sub(r"\b1\s*", "I ", text)
    text = re.sub(r"[A-Z]{3,}", "", text)
    return text.strip()
