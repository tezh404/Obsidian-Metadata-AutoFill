# 🧠 AI Metadata Generator & Applier for Markdown Files

This project automates metadata generation and application for Markdown (`.md`) files using a local language model (LM Studio). It first **generates** meaningful metadata (like title, category, summary, and tags), then **safely applies** it back to the files.

---

## 📦 Project Structure

```

.
├── generate\_metadata.py         # Uses LM Studio to extract metadata from Markdown content
├── apply\_metadata.py            # Applies generated metadata to frontmatter of files
├── config.example.json          # Example config file (copy & rename to config.json before use)
├── metadata\_output.json         # Generated metadata (intermediate output)
└── archive/                     # Backup of original Markdown files (created on first run)

````

---

## 🔧 Requirements

* Python 3.x
* [LM Studio](https://lmstudio.ai/) running locally (default API: `http://localhost:1234/v1/chat/completions`)
* No external Python libraries needed (uses standard library only)

---

## ⚙️ Configuration

Before running, **copy** `config.example.json` to `config.json` and edit the path:

```bash
cp config.example.json config.json
````

Edit `config.json`:

```json
{
  "MY_PATH": "path/to/your/markdown/files"
}
```

Replace `"path/to/your/markdown/files"` with the absolute or relative path to your Markdown directory.

---

## 🚀 Usage

### Step 1: Generate Metadata Using LM Studio

```bash
python generate_metadata.py
```

* Scans all `.md` files in the configured folder.
* Uses LM Studio to generate:

  * `title`
  * `summary`
  * `tags`
  * `category`
* Saves results to `metadata_output.json`.

### Step 2: Apply Metadata to Files

```bash
python apply_metadata.py
```

* Reads `metadata_output.json`.
* Updates each file's frontmatter **only if the field exists and is empty**.
* Tags are normalized by replacing spaces with underscores.
* Creates backups of original files in `archive/` folder before applying changes.

---

## 📝 Example: metadata\_output.json

```json
[
  {
    "filepath": "notes/example.md",
    "filename": "example.md",
    "title": "Benefits of Morning Walks",
    "summary": "Walking early in the morning improves mental clarity and physical health.",
    "tags": ["health", "exercise", "morning"],
    "category": "health"
  }
]
```

---

## 🔐 Safe by Design

* Original `.md` files are backed up to `archive/` before changes.
* Only **existing and empty** frontmatter fields are updated.
* Tags are automatically cleaned (`"artificial intelligence"` → `"artificial_intelligence"`).
* `<think>...</think>` blocks (if any) are stripped from input text before analysis.

---

## 📌 Notes

* LM Studio must be running locally and accessible at the defined API port.
* The script reads folder path from `config.json`. Make sure to rename and edit the example config before running.
* This system does **not** add new frontmatter fields if they don't already exist — it fills in missing values only.

---

## 🛠️ Customization

* You can tweak the prompt behavior in `generate_metadata.py`:

```python
prompts = {
    "category": "Return one simple category label...",
    ...
}
```

* You can modify `apply_metadata.py` to allow adding new fields or change archiving behavior.

---

## 📃 License

MIT — Use freely, modify safely.

---
