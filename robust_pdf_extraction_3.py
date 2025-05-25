# async_llama_parse_pipeline.py

import os
import json
import asyncio
import aiofiles
from pathlib import Path
from llama_parse import LlamaParse
from PyPDF2 import PdfReader
from tqdm.asyncio import tqdm_asyncio
from dotenv import load_dotenv
load_dotenv()
# === Config ===
RESULT_TYPE = "markdown"
LANGUAGE = "en"
OUTPUT_DIR = "parsed_output"
MAX_CONCURRENT_TASKS = 6

parser = LlamaParse(result_type=RESULT_TYPE, language=LANGUAGE, max_pages=None, verbose=True)
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

# === Ensure output directory exists ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Utility functions ===
def is_from_gca(path):
    return "data_garr" not in str(path)

def get_output_paths(pdf_path):
    base = Path(pdf_path).stem
    txt_path = Path(OUTPUT_DIR) / f"{base}.txt"
    meta_path = Path(OUTPUT_DIR) / f"{base}_metadata.json"
    return txt_path, meta_path

def get_source_metadata(pdf_path):
    parts = Path(pdf_path).parts
    title = next((p for p in parts if "Title" in p or "title" in p), "")
    chapter = Path(pdf_path).stem
    source_type = "Guam Code Annotated" if is_from_gca(pdf_path) else "Guam Administrative Rules and Regulations"
    return {
        "title": title,
        "chapter": chapter,
        "source_type": source_type
    }

def is_valid_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            return any(page.extract_text() for page in reader.pages)
    except Exception:
        return False

async def parse_and_save(pdf_path):
    async with semaphore:
        try:
            if not is_valid_pdf(pdf_path):
                print(f"⚠️ Skipping invalid PDF: {pdf_path}")
                return False

            documents = await parser.aload_data(str(pdf_path))
            if not documents:
                print(f"❌ Empty content returned from parser for: {pdf_path}")
                return False

            text_content = "\n\n".join(doc.text for doc in documents)
            metadata = documents[0].metadata or {}
            metadata.update(get_source_metadata(pdf_path))

            txt_path, meta_path = get_output_paths(pdf_path)

            async with aiofiles.open(txt_path, "w", encoding="utf-8") as f_txt:
                await f_txt.write(text_content)

            async with aiofiles.open(meta_path, "w", encoding="utf-8") as f_meta:
                await f_meta.write(json.dumps(metadata, indent=4))

            print(f"✅ Parsed: {pdf_path}")
            return True

        except Exception as e:
            print(f"❌ Error parsing {pdf_path}: {e}")
            return False

async def gather_pdf_paths():
    data_paths = list(Path("data").rglob("*.pdf"))
    garr_paths = list(Path("data_garr").rglob("*.pdf"))
    return data_paths + garr_paths

async def main():
    print("🚀 Starting batch LlamaParse extraction...")
    pdf_paths = await gather_pdf_paths()

    tasks = [parse_and_save(pdf) for pdf in pdf_paths]
    results = await tqdm_asyncio.gather(*tasks)

    failed = [str(pdf_paths[i]) for i, success in enumerate(results) if not success]

    if failed:
        async with aiofiles.open("failed_parsing_log.json", "w", encoding="utf-8") as f:
            await f.write(json.dumps(failed, indent=4))
        print(f"⚠️ {len(failed)} files failed. See failed_parsing_log.json")
    else:
        print("🎉 All files parsed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
