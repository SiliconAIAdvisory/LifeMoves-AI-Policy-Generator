# agent.py
import os
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from retriever import get_retriever
from prompts import SYSTEM_PROMPT
from memory import memory
from langchain_anthropic import ChatAnthropic  # ✅ Claude wrapper for LangChain

# Initialize Claude 3.7 (Opus) via Anthropic's LangChain wrapper
llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",  
    temperature=0,
    max_tokens=64000,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

# Setup retriever using your Pinecone-based vector store
retriever = get_retriever()

# Tool function: vector search + metadata
def pinecone_search(query: str) -> str:
    """Retrieve LifeMoves policy answers from vector store."""
    print(f"[pinecone_rag_tool] called with query={query!r}")
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant policy documents found for that question."

    output = []
    for idx, doc in enumerate(docs[:3], start=1):
        # You can include metadata if needed (e.g., site, document type)
        answer = doc.page_content.strip()
        output.append(f"Result {idx}:\n{answer}")
    return "\n\n".join(output)

# Tool definition for the agent
pinecone_rag_tool = Tool.from_function(
    func=pinecone_search,
    name="policy_rag_search",
    description="Use this tool to retrieve LifeMoves policies and framework-aligned answers from the vector store."
)

# Create the ReAct agent graph using LangGraph
graph = create_react_agent(
    llm,
    tools=[pinecone_rag_tool],
    prompt=SYSTEM_PROMPT,
    checkpointer=memory,
)

# CLI or API-friendly sync call
def ask_agent(question: str, thread_id: str = "1") -> str:
    state = {
        "messages": [
            {"role": "user", "content": question}
        ]
    }
    result = graph.invoke(state, config={"configurable": {"thread_id": thread_id}})
    final = result["messages"][-1]
    return final[1] if isinstance(final, tuple) else getattr(final, "content", str(final))
