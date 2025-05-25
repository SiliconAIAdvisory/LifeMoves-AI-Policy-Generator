import os
from dotenv import load_dotenv
from collections import defaultdict
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

# Load environment variables
load_dotenv()

# === Config ===
INPUT_DIR = "data"
OUTPUT_DIR = "text_data"
RESULT_TYPE = "markdown"
LANGUAGE = "en"

# Ensure output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize LlamaParse
parser = LlamaParse(
    result_type=RESULT_TYPE,
    language=LANGUAGE,
    max_pages=None,
    verbose=True
)

# Use SimpleDirectoryReader to load PDFs
file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader(input_dir=INPUT_DIR, file_extractor=file_extractor).load_data()

# === Group documents by file name ===
file_texts = defaultdict(list)
for doc in documents:
    file_path = doc.metadata.get("file_path", "output.pdf")
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    file_texts[base_name].append(doc.text)

# === Save grouped content to .txt files ===
for base_name, text_chunks in file_texts.items():
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(text_chunks))  # Join multiple pages with spacing
    print(f"✅ Merged and saved: {output_path}")

