import re
import requests
import json
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LM_STUDIO_API = "http://localhost:1234/v1/chat/completions"
JSON_OUTPUT = "metadata_output.json"

with open("config.json", "r") as f:
    config = json.load(f)

FOLDER_PATH = config["MY_PATH"]
print(f"Working in path: {FOLDER_PATH}")

prompts = {
    "category": "Read the text below and return only one simple category label. Do not add emphasis or extra formatting. Example: personal, ideas, technology, nature, health, daily. Only write the label:",
    "title": "Write a short, clear, and meaningful title for the text below. Do not use quotes or formatting. Only write the title:",
    "summary": "Summarize the text in 1–2 plain sentences. Do not use double quotes, bold, or any special formatting. Use single quotes if needed. Keep it factual and clear. Only write the summary:",
    "tags": "Suggest 3 to 5 plain keywords for the text below. Do not use any formatting. Separate words with commas in one line. Example: technology, artificial intelligence, coding:"
}

def query_lmstudio(prompt, context):
    payload = {
        "messages": [
            {"role": "system", "content": "You are an assistant that suggests concise, structured, and accurate metadata."},
            {"role": "user", "content": f"{prompt}\n\nText:\n{context}"}
        ],
        "temperature": 0.5
    }
    try:
        print(f"[DEBUG] Sending request to LM Studio API. Prompt type: '{prompt.split()[0]}'", flush=True)
        res = requests.post(LM_STUDIO_API, json=payload)
        res.raise_for_status()
        answer = res.json()["choices"][0]["message"]["content"].strip()
        print(f"[DEBUG] Response received from LM Studio: {answer[:60]}{'...' if len(answer)>60 else ''}", flush=True)
        return answer
    except Exception as e:
        print(f"[!] Error: {e}", flush=True)
        return ""

def remove_think_sections(text):
    print("[DEBUG] Removing <think> sections if present...", flush=True)
    return re.sub(r"\n?\s*<think>.*?</think>\s*\n?", "", text, flags=re.DOTALL)

def parse_content(filename):
    print(f"[DEBUG] Reading file: {filename}", flush=True)
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        raise ValueError("Frontmatter (---) not found.")
    frontmatter_raw = match.group(1)
    body = match.group(2).strip()

    metadata = {}
    for line in frontmatter_raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            metadata[key] = value.strip('"').strip("'")

    print(f"[DEBUG] Frontmatter parsed: {filename}", flush=True)
    return body, metadata

def generate_metadata(content, prompts, existing_meta):
    print("[DEBUG] Generating metadata...", flush=True)
    clean_content = remove_think_sections(content)
    metadata = {}

    for key, prompt in prompts.items():
        if key in existing_meta and existing_meta[key].strip():
            print(f"[=] '{key}' already exists. Skipping LLM query.", flush=True)
            metadata[key] = existing_meta[key].strip()
        else:
            print(f"[+] '{key}' missing. Querying LLM...", flush=True)
            result = query_lmstudio(prompt, clean_content)
            cleaned = result.strip()

            if cleaned.startswith('"') and cleaned.endswith('"'):
                cleaned = cleaned[1:-1]

            if key == "tags":
                cleaned = [tag.strip() for tag in cleaned.strip("[]").split(",") if tag.strip()]

            metadata[key] = cleaned
    print("[DEBUG] Metadata generation completed.", flush=True)
    return metadata

def process_folder(folder_path, prompts):
    all_metadata = []
    print(f"[INFO] Scanning folder: {folder_path}", flush=True)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".md"):
                filepath = os.path.join(root, file)
                print(f"[i] Processing: {filepath}", flush=True)
                try:
                    content, existing_meta = parse_content(filepath)
                    metadata = generate_metadata(content, prompts, existing_meta)
                    metadata["filename"] = file
                    metadata["filepath"] = filepath
                    all_metadata.append(metadata)
                except Exception as e:
                    print(f"[!] Error while processing {filepath}: {e}", flush=True)
    print(f"[INFO] Folder scan completed. Total files: {len(all_metadata)}", flush=True)
    return all_metadata

def save_metadata_to_json(metadata_list, output_file):
    print(f"[INFO] Saving metadata to JSON file: {output_file}", flush=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2, ensure_ascii=False)
    print(f"[✓] Metadata saved to JSON file: {output_file}", flush=True)

# Run
metadata_list = process_folder(FOLDER_PATH, prompts)
save_metadata_to_json(metadata_list, JSON_OUTPUT)
