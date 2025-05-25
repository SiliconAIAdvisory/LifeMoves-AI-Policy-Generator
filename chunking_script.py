import re
from pathlib import Path
import tiktoken

# Constants
MAX_TOKENS = 300
OVERLAP_TOKENS = 20
MAX_CHUNK_BYTES = 40000  # Pinecone metadata limit = 40KB

tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(tokenizer.encode(text))

def chunk_text_by_tokens(text, max_tokens=MAX_TOKENS, overlap_tokens=OVERLAP_TOKENS):
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = ' '.join(tokens[i:i + max_tokens])
        while len(chunk.encode("utf-8")) > MAX_CHUNK_BYTES:
            # Reduce size by removing some tokens
            cutoff = int(len(tokens[i:i + max_tokens]) * 0.8)
            chunk = ' '.join(tokens[i:i + cutoff])
            max_tokens = cutoff
        chunks.append(chunk)
        i += max_tokens - overlap_tokens
    return chunks

def chunk_legislative_text(text):
    chunks = []
    sections = re.split(r"(# § \d+\..*?\n)", text)
    current_chunk = ""

    for sec in sections:
        if sec.startswith("# §"):
            if current_chunk and count_tokens(current_chunk) >= OVERLAP_TOKENS:
                if len(current_chunk.encode("utf-8")) > MAX_CHUNK_BYTES:
                    chunks.extend(chunk_text_by_tokens(current_chunk))
                else:
                    chunks.append(current_chunk.strip())
                current_chunk = ' '.join(current_chunk.split()[-OVERLAP_TOKENS:])
            current_chunk += sec
        else:
            sec_tokens = count_tokens(sec)
            current_tokens = count_tokens(current_chunk)

            if current_tokens + sec_tokens > MAX_TOKENS:
                if len(current_chunk.encode("utf-8")) > MAX_CHUNK_BYTES:
                    chunks.extend(chunk_text_by_tokens(current_chunk))
                else:
                    chunks.append(current_chunk.strip())
                current_chunk = ' '.join(current_chunk.split()[-OVERLAP_TOKENS:])
            current_chunk += sec

    if current_chunk.strip():
        if len(current_chunk.encode("utf-8")) > MAX_CHUNK_BYTES:
            chunks.extend(chunk_text_by_tokens(current_chunk))
        else:
            chunks.append(current_chunk.strip())

    return chunks

def process_and_save_chunks_recursive(root_input_dir: str, root_output_dir: str):
    root_input_path = Path(root_input_dir)
    root_output_path = Path(root_output_dir)
    root_output_path.mkdir(parents=True, exist_ok=True)

    for subfolder in root_input_path.iterdir():
        if subfolder.is_dir():
            output_subfolder_path = root_output_path / subfolder.name
            output_subfolder_path.mkdir(parents=True, exist_ok=True)

            for file in subfolder.glob("*.txt"):
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()

                chunks = chunk_legislative_text(text)

                for idx, chunk in enumerate(chunks):
                    chunk_file = output_subfolder_path / f"{file.stem}_chunk_{idx+1}.txt"
                    with open(chunk_file, 'w', encoding='utf-8') as out_f:
                        out_f.write(chunk)

                print(f"✅ Processed {len(chunks)} chunks for {file.name}")

# Usage
input_dir = "RAG_FILES_GCA"
output_dir = "CHUNKS_GCA"
process_and_save_chunks_recursive(input_dir, output_dir)

