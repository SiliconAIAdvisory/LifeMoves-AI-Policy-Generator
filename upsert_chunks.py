from pathlib import Path
import os
import json
import uuid
from tqdm import tqdm
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
import tiktoken
import logging
import sys
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("upsert_chunks.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Load .env variables
load_dotenv()

# Configuration
BASE_DIR = Path("LLM_CHUNKS_text_data")
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 1024
PINECONE_INDEX_NAME = "policy-generator"
BATCH_SIZE = 50
MAX_TOKENS = 8191
MAX_METADATA_SIZE = 40960  # 40 KB

# Init OpenAI & tokenizer
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tokenizer = tiktoken.get_encoding("cl100k_base")

# Init Pinecone v4
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("policy-generator")
# Text cleaning helper
def strip_special_characters_and_format(text: str) -> str:
    clean = re.sub(r"[^\x00-\x7F]+", "", text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

# Truncate helper
def truncate_to_token_limit(text, max_tokens=MAX_TOKENS):
    tokens = tokenizer.encode(text)
    if len(tokens) > max_tokens:
        return tokenizer.decode(tokens[:max_tokens]), True
    return text, False

# Collect documents
documents = []
metadatas = []

logging.info("🔍 Scanning folders...")

for folder in BASE_DIR.iterdir():
    if folder.is_dir():
        logging.info(f"📂 Processing folder: {folder.name}")
        for json_file in folder.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    chunks = json.load(f)

                for chunk in chunks:
                    raw_text = chunk.get("text", "").strip()
                    if not raw_text:
                        continue

                    safe_text, was_truncated = truncate_to_token_limit(raw_text)
                    formatted_text = strip_special_characters_and_format(raw_text)

                    metadata = {"text": formatted_text}
                    if len(json.dumps(metadata).encode('utf-8')) > MAX_METADATA_SIZE:
                        logging.error(f"🚫 Metadata too large in {json_file.name}. Skipping.")
                        continue

                    documents.append(safe_text)
                    metadatas.append(metadata)

                    if was_truncated:
                        logging.warning(f"[⚠️] Truncated chunk in: {json_file.name}")

            except Exception as e:
                logging.error(f"❌ Failed to process {json_file.name}: {e}")

logging.info(f"✅ {len(documents)} chunks loaded.")

# Embed + upsert
for i in tqdm(range(0, len(documents), BATCH_SIZE), desc="📦 Upserting Batches"):
    batch_texts = documents[i:i + BATCH_SIZE]
    batch_metadatas = metadatas[i:i + BATCH_SIZE]

    logging.info(f"🧠 Embedding batch {i // BATCH_SIZE + 1}...")

    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch_texts,
            dimensions=EMBEDDING_DIM,
            encoding_format="float"
        )
        embeddings = [item.embedding for item in response.data]

        vectors = [
            {"id": uuid.uuid4().hex, "values": vec, "metadata": meta}
            for vec, meta in zip(embeddings, batch_metadatas)
        ]

        index.upsert(vectors=vectors)
        logging.info(f"✅ Upserted batch {i // BATCH_SIZE + 1}.")

    except Exception as e:
        logging.error(f"❌ Error on batch {i // BATCH_SIZE + 1}: {e}")

logging.info("🎉 All chunks embedded and upserted.")
