import os
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import tiktoken

# Load environment variables
load_dotenv()

# Constants
MAX_TOKENS = 250
OVERLAP_TOKENS = 20
MAX_CHUNK_BYTES = 40000

# Tokenizer initialization
tokenizer = tiktoken.get_encoding("cl100k_base")

# LLM initialization
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Count tokens helper
def count_tokens(text):
    return len(tokenizer.encode(text))

# Proper token chunking function
def chunk_text_by_tokens(text, max_tokens=MAX_TOKENS, overlap_tokens=OVERLAP_TOKENS):
    token_ids = tokenizer.encode(text)
    chunks = []
    i = 0
    while i < len(token_ids):
        chunk_tokens = token_ids[i:i + max_tokens]
        chunk_text = tokenizer.decode(chunk_tokens)

        # Ensure chunk size respects MAX_CHUNK_BYTES
        while len(chunk_text.encode("utf-8")) > MAX_CHUNK_BYTES:
            max_tokens = int(max_tokens * 0.8)
            chunk_tokens = token_ids[i:i + max_tokens]
            chunk_text = tokenizer.decode(chunk_tokens)

        chunks.append(chunk_text)
        i += max_tokens - overlap_tokens
    return chunks

# Extract Title and Chapter metadata from first chunk using LLM
def extract_title_chapter(chunk):
    prompt_template = ChatPromptTemplate.from_template(
        "Analyze the chunk in <chunk> tags, then respond only with the Title, Topic or Refernce : "
        "Example: 'Programs & Services Policy #: GUAD 1'."
        "<chunk>{chunk}</chunk>"
    )
    chain = prompt_template | llm
    response = chain.invoke({"chunk": chunk})
    return response.content.strip()

# Main function
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

                # Step 1: Extract metadata from the first 250-token chunk
                initial_chunk_tokens = tokenizer.encode(text)[:MAX_TOKENS]
                initial_chunk_text = tokenizer.decode(initial_chunk_tokens)

                title_chapter_meta = extract_title_chapter(initial_chunk_text)
                print(f"\n🧾 Metadata extracted for {file.name}: {title_chapter_meta}")

                # Step 2: Chunk entire text explicitly by tokens
                chunks = chunk_text_by_tokens(text)

                # Step 3: Add metadata and save chunks
                for idx, chunk in enumerate(chunks):
                    chunk_with_meta = f"{title_chapter_meta}\n\n{chunk}"
                    chunk_file = output_subfolder_path / f"{file.stem}_chunk_{idx+1}.txt"
                    with open(chunk_file, 'w', encoding='utf-8') as out_f:
                        out_f.write(chunk_with_meta)

                print(f"✅ Processed {len(chunks)} chunks for {file.name}")

# Execute script
if __name__ == "__main__":
    input_dir = "text_data"
    output_dir = "LLM_CHUNKS_text_data"
    process_and_save_chunks_recursive(input_dir, output_dir)
