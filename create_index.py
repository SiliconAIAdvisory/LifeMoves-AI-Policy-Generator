
import os
from pinecone import Pinecone, ServerlessSpec

# Optional: Store key securely in env
api_key = "pcsk_31RZW6_76S2FLn3YPb7yBVr9WgbvERFGg5TFyzrbWbLowsrxzUL7zJPQbGhSNqXN7o6Cww"
pc = Pinecone(api_key=api_key)

# Define index
index_name = "legislation-index"
dimension = 1024  # for multilingual-e5-large
cloud = "aws"
region = "us-east-1"

# Check & create
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud=cloud, region=region)
    )
    print(f"✅ Created index: {index_name}")
else:
    print(f"ℹ️ Index '{index_name}' already exists.")

