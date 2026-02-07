import requests

NLP_URL = "http://127.0.0.1:9000/process"


def generate_prompts(text_pages: list[str]):
    response = requests.post(NLP_URL, json={"pages": text_pages}, timeout=300)
    response.raise_for_status()
    return response.json()
