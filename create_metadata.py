from pathlib import Path
import json
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_metadata_json(base_dir: Path):
    """
    Creates metadata JSON files for each .txt chunk, storing only the full raw text.
    """
    logging.info(f"🔍 Starting metadata creation in {base_dir}")

    for folder in base_dir.iterdir():
        if folder.is_dir():
            logging.info(f"📁 Processing folder: {folder.name}")

            for txt_file in folder.glob("*.txt"):
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        raw_text = f.read().strip()

                    metadata = [{
                        "text": raw_text
                    }]

                    output_file = txt_file.with_suffix(".json")
                    with open(output_file, 'w', encoding='utf-8') as json_out:
                        json.dump(metadata, json_out, indent=2, ensure_ascii=False)

                    logging.info(f"✅ Metadata saved: {output_file}")

                except Exception as e:
                    logging.error(f"❌ Error processing {txt_file}: {e}")

if __name__ == "__main__":
    base_dir = Path("LLM_CHUNKS_text_data")  # Adjust if your directory is different
    create_metadata_json(base_dir)



