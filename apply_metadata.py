import re
import json
import sys
import io
import os
import shutil

# Ensure UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def archive_original_file(filename):
    archive_dir = "archive"
    os.makedirs(archive_dir, exist_ok=True)

    base_name = os.path.basename(filename)
    name, ext = os.path.splitext(base_name)
    archive_path = os.path.join(archive_dir, f"{name}_original{ext}")

    try:
        shutil.copy2(filename, archive_path)
        print(f"[→] Original file archived as '{archive_path}'.")
    except Exception as e:
        print(f"[!] Archiving error: {e}")

def parse_frontmatter(text):
    match = re.search(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not match:
        raise ValueError("Frontmatter section (---) not found.")
    metadata_text, content = match.group(1), match.group(2)
    metadata_lines = metadata_text.strip().splitlines()
    metadata = {}
    for line in metadata_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            val = value.strip()

            # Remove surrounding quotes
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]

            # Convert tags to list if formatted as [item1, item2]
            if key.strip() == "tags":
                if val.startswith("[") and val.endswith("]"):
                    try:
                        items = [item.strip().strip('"').strip("'") for item in val[1:-1].split(",") if item.strip()]
                        metadata[key.strip()] = items
                        continue
                    except Exception:
                        pass

            metadata[key.strip()] = val

    return metadata, content

def needs_quotes(s):
    if s == "":
        return True
    special_chars = [' ', ':', '#', '-', '{', '}', '[', ']', ',', '&', '*', '?', '|', '>', '\'', '"', '%', '@', '`', '!']
    return any(c in s for c in special_chars)

def format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        formatted_items = []
        for item in value:
            if isinstance(item, str):
                item = item.strip()
                if needs_quotes(item):
                    formatted_items.append(f'"{item}"')
                else:
                    formatted_items.append(item)
            else:
                formatted_items.append(str(item))
        return "[" + ", ".join(formatted_items) + "]"
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return '""'
        if needs_quotes(value):
            return f'"{value}"'
        else:
            return value
    return str(value)

def build_frontmatter(metadata):
    lines = []
    for key, value in metadata.items():
        if is_empty_value(value):
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {format_value(value)}")
    return "\n".join(lines)

def is_empty_value(val):
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip() == "" or val.strip().lower() == "null" or val.strip() == '""'
    if isinstance(val, list):
        return len(val) == 0
    return False

def apply_metadata_to_file(filename, new_metadata):
    if not os.path.exists(filename):
        print(f"[!] File not found: {filename}")
        return

    archive_original_file(filename)

    with open(filename, "r", encoding="utf-8") as f:
        full_text = f.read()

    metadata, content = parse_frontmatter(full_text)

    # Normalize 'tags': convert string to list and replace spaces with underscores
    if "tags" in new_metadata:
        if isinstance(new_metadata["tags"], str):
            new_metadata["tags"] = [tag.strip().replace(" ", "_") for tag in new_metadata["tags"].split(",") if tag.strip()]
        elif isinstance(new_metadata["tags"], list):
            new_metadata["tags"] = [tag.strip().replace(" ", "_") if isinstance(tag, str) else tag for tag in new_metadata["tags"]]

    # Update only existing and empty keys in the original metadata
    for key in metadata.keys():
        if key in new_metadata and not is_empty_value(new_metadata[key]):
            if is_empty_value(metadata.get(key)):
                metadata[key] = new_metadata[key]

    final_text = f"---\n{build_frontmatter(metadata)}\n---\n{content}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"[✓] Metadata updated: {filename}")

def process_all_from_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        entries = json.load(f)

    for entry in entries:
        if "filepath" not in entry:
            print("[!] Entry skipped: missing 'filepath'.")
            continue
        filename = entry["filepath"]
        metadata = {k: v for k, v in entry.items() if k not in ("filepath", "filename")}
        apply_metadata_to_file(filename, metadata)

# Run
process_all_from_json("metadata_output.json")
