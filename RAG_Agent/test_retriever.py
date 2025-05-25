from retriever import get_retriever

def test_retrieval(query="What information do I need to sign up for HABIBMETRO Internet Banking?"):
    retriever = get_retriever()
    try:
        # If using new LangChain retriever API
        result = retriever.invoke(query)
        print("Retrieved using `.invoke()`:\n")
        for i, doc in enumerate(result, 1):
            print(f"\nDocument {i}:\n{'-'*40}\n{doc.page_content[:500]}\n")
    except Exception as e:
        print(f"[!] invoke() failed: {e}")
        print("Trying deprecated `.get_relevant_documents()` as fallback...")
        try:
            fallback = retriever.get_relevant_documents(query)
            for i, doc in enumerate(fallback, 1):
                print(f"\nDocument {i}:\n{'-'*40}\n{doc.page_content[:500]}\n")
        except Exception as fallback_error:
            print(f"[❌] Both methods failed: {fallback_error}")

if __name__ == "__main__":
    test_retrieval()
