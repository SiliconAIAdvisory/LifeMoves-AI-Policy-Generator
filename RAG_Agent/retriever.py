from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
import os
from dotenv import load_dotenv

# Load environment variables (API keys, index name, etc.)
load_dotenv()

# Initialize Pinecone and create a retriever for the vector store
def get_retriever():
    # Set up Pinecone client with API key and environment
    pc = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")  # e.g., "us-west4-gcp" or similar
    )
    # Connect to the existing Pinecone index
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))  # make sure this env var is set
    # Create a LangChain vector store using the Pinecone index and OpenAI embeddings for queries
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024),  # uses OpenAI API for embedding the query
        text_key="text"               # the field name in the index that stores document text
    )
    # Return a retriever interface for similarity search
    return vectorstore.as_retriever()
