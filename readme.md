# LifeMoves AI Policy Generator

This repository contains a complete **Retrieval-Augmented Generation (RAG)** pipeline for generating trauma-informed, framework-aligned policies for LifeMoves, a nonprofit organization providing housing and outreach services. The system uses PDF parsing, chunking, vector indexing, and a Claude 3.7–based ReAct agent, exposed via both CLI and Streamlit.

---

## 📁 Repository Structure

```
├── data/                       # Raw input PDFs
│   └── ...                     # Place your LifeMoves policy PDFs here
├── text_data/                  # Extracted .txt files from PDFs
├── LLM_CHUNKS_text_data/       # Token-chunked text files with metadata
├── RAG_Agent/
│   ├── extract_pdf.py          # LlamaParse-based PDF → text extractor
│   ├── chunking_llm.py         # Token-based chunker with semantic metadata via Claude
│   ├── create_metadata.py      # Wrap chunk text into JSON metadata
│   ├── upsert_chunks.py        # Embed and upsert chunks into Pinecone
│   ├── retriever.py            # LangChain/Pinecone retriever factory
│   ├── prompts.py              # System prompt definitions
│   ├── agent.py                # ReAct RAG agent using Claude 3.7
│   └── run.py                  # CLI runner for the agent
├── streamlit_app.py            # Streamlit UI for policy generation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🛠️ Prerequisites

* **Python 3.10+**
* **Virtual environment** (recommended)
* **API keys**:

  * `OPENAI_API_KEY` (for embeddings)
  * `ANTHROPIC_API_KEY` (for Claude 3.7)
  * `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`, `PINECONE_INDEX_NAME`

Place them in a `.env` file at the project root:

```ini
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=api-...
PINECONE_API_KEY=pcsk-...
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=policy-generator
```

Install dependencies:

```bash
python -m venv venv
source venv/bin/activate        # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🔄 1. PDF Extraction → `text_data/`

Use **`extract_pdf.py`** to parse all PDFs in `data/` into plain text:

```bash
python RAG_Agent/extract_pdf.py
```

This populates `text_data/` with one `.txt` file per PDF.

---

## 🔄 2. Chunking → `LLM_CHUNKS_text_data/`

Tokenize and semantically label text chunks using **`chunking_llm.py`**:

```bash
python RAG_Agent/chunking_llm.py
```

* **Chunk size**: \~250 tokens, 20-token overlap
* **Metadata**: Extracted via an LLM prompt
* Output: chunked `.txt` files under `LLM_CHUNKS_text_data/<doc>/`

---

## 🔄 3. Metadata Creation → JSON

Wrap each chunk into JSON with `create_metadata.py`:

```bash
python RAG_Agent/create_metadata.py
```

Generates a `.json` for each chunk file, with format:

```json
[ { "text": "<chunk text>" } ]
```

---

## 🔄 4. Embedding & Upsert → Pinecone

Run **`upsert_chunks.py`** to embed and upload all chunks:

```bash
python RAG_Agent/upsert_chunks.py
```

* Embedding model: `text-embedding-3-large`
* Vector DB: Pinecone serverless index
* Batch size: 50

Once complete, your Pinecone index will contain all LifeMoves policy fragments, ready for retrieval.

---

## 🤖 5. Retriever Setup (`retriever.py`)

Use LangChain’s PineconeVectorStore:

```python
from RAG_Agent.retriever import get_retriever
retriever = get_retriever()
# docs = retriever.invoke("Your query here")
```

This returns the top-k relevant documents for any given query.

---

## 🧠 6. RAG Agent (`agent.py`)

Defines a **ReAct-style** agent using LangGraph and Claude 3.7:

* **Tool**: `policy_rag_search` wraps retrieval
* **LLM**: `langchain_anthropic.ChatAnthropic(model="claude-3-opus-20240229")`
* **Prompt**: `SYSTEM_PROMPT` enforces LifeMoves CEP, readability, and compliance

Invoke via:

```bash
python RAG_Agent/run.py
```

Or programmatically:

```python
from RAG_Agent.agent import ask_agent
print(ask_agent("Create a visitor policy for family shelters"))
```

---

## 🌐 7. Streamlit UI

Launch a web interface:

```bash
streamlit run streamlit_app.py
```

Enter your policy instruction, click **Generate Policy**, and view the AI draft in your browser.

---

## 🚀 Next Steps & Tips

* **Notion Integration**: Auto-save drafts back to Notion workspaces.
* **Validation Agent**: Add a pipeline step for readability checks and framework alignment.
* **Approval Workflow**: Hook into Slack/email APIs for DEIB/legal sign-off.
* **Customization**: Add dropdowns for site and funder contexts in the UI.

**Enjoy building trauma‑informed, evidence‑based policies with AI!**
