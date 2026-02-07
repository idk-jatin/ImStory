import json
import os
import time
import uuid
import shutil
import requests
import logging
from concurrent.futures import ThreadPoolExecutor

COMFY_URL = "http://127.0.0.1:8188"
WORKFLOW_FILE = os.path.join(os.path.dirname(__file__), "workflows", "txt2img.json")

BASE_STORAGE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage")
)
IMAGES_DIR = os.path.join(BASE_STORAGE, "images")
PROMPTS_DIR = os.path.join(BASE_STORAGE, "prompts")
TEMP_DIR = os.path.join(BASE_STORAGE, "temp")
OUTPUT_DIR = os.path.join(
    BASE_STORAGE, "output"
)

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)


NEGATIVE_PROMPT = """
low quality, worst quality, blurry,
motion blur, out of focus, fuzzy, hazy,
extra fingers, extra limbs,
deformed face, distorted anatomy,
watermark, text artifacts,
oversharpened, jpeg artifacts,
cropped, duplicate,
ugly, poorly drawn hands,
mutation, bad proportions
"""

executor = ThreadPoolExecutor(max_workers=1)


def load_workflow():
    if not os.path.exists(WORKFLOW_FILE):
        raise FileNotFoundError(f"Workflow file not found: {WORKFLOW_FILE}")
    with open(WORKFLOW_FILE, "r") as f:
        return json.load(f)


def check_server():
    try:
        response = requests.get(f"{COMFY_URL}/object_info", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _process_generation(uid: str, prompts_data: list[dict]):
    results = []

    user_img_dir = os.path.join(IMAGES_DIR, uid)
    os.makedirs(user_img_dir, exist_ok=True)

    workflow_template = load_workflow()

    for item in prompts_data:
        page_num = item["page"]
        prompt_text = item["prompt"]

        workflow = json.loads(json.dumps(workflow_template))  # Deep copy
        base_seed = abs(hash(uid)) % (10**9)
        seed = base_seed + page_num

        filename_prefix = f"{uid}_page_{page_num}"

        workflow["3"]["inputs"]["text"] = prompt_text

        workflow["4"]["inputs"]["text"] = NEGATIVE_PROMPT

        workflow["6"]["inputs"]["seed"] = seed

        workflow["8"]["inputs"]["filename_prefix"] = filename_prefix

        try:
            p = {"prompt": workflow}
            response = requests.post(f"{COMFY_URL}/prompt", json=p, timeout=10)
            response.raise_for_status()
            prompt_id = response.json()["prompt_id"]

            start_time = time.time()
            max_wait = 120

            image_filename = None

            while True:
                if time.time() - start_time > max_wait:
                    raise TimeoutError("Generation timed out.")

                history_resp = requests.get(
                    f"{COMFY_URL}/history/{prompt_id}", timeout=5
                )
                history_data = history_resp.json()

                if prompt_id in history_data:
                    outputs = history_data[prompt_id]["outputs"]
                    if "8" in outputs:
                        images = outputs["8"]["images"]
                        if images:
                            image_filename = images[0]["filename"]
                    break

                time.sleep(1)

            if image_filename:
                view_resp = requests.get(
                    f"{COMFY_URL}/view",
                    params={"filename": image_filename, "type": "output"},
                    timeout=30,
                )
                if view_resp.status_code == 200:
                    dest_path = os.path.join(user_img_dir, f"page_{page_num}.png")
                    with open(dest_path, "wb") as f:
                        f.write(view_resp.content)

                    results.append(
                        {"page": page_num, "status": "success", "image_path": dest_path}
                    )
                else:
                    results.append(
                        {
                            "page": page_num,
                            "status": "failed",
                            "error": "Could not retrieve image",
                        }
                    )
            else:
                results.append(
                    {
                        "page": page_num,
                        "status": "failed",
                        "error": "No image in output",
                    }
                )

        except Exception as e:
            results.append({"page": page_num, "status": "failed", "error": str(e)})

        try:
            requests.post(
                f"{COMFY_URL}/free",
                json={"unload_models": False, "free_memory": True},
                timeout=2,
            )
        except:
            pass

    # SAVE PROMPT LOG
    try:
        log_path = os.path.join(PROMPTS_DIR, f"{uid}.json")
        log_data = {
            "uid": uid,
            "timestamp": time.time(),
            "generations": results,
            "inputs": prompts_data,
        }
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)
    except Exception as e:
        print(f"Failed to save prompt log: {e}")

    return results


def generate_images(uid: str, prompts_data: list[dict]):
    if not check_server():
        return [{"error": "ComfyUI server not available"}]

    future = executor.submit(_process_generation, uid, prompts_data)
    return future.result()
