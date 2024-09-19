import faiss
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModel

# Initialize HuggingFaceEmbeddings
model_name = 'sentence-transformers/all-mpnet-base-v2'  # You can replace it with any HuggingFace-supported model
hf_embedder = HuggingFaceEmbeddings(model_name=model_name)


def create_embeddings_for_faiss(code_dict):
    """
    Create embeddings for cleaned code and its components using HuggingFaceEmbeddings.

    Args:
        code_dict (dict): Dictionary containing cleaned code and components.

    Returns:
        list: Embeddings list and corresponding metadata list for FAISS.
    """
    embeddings = []
    metadata = []

    # Create embeddings for cleaned code
    cleaned_code_embedding = hf_embedder.embed_query(code_dict['cleaned_code'])
    embeddings.append(cleaned_code_embedding)
    metadata.append("cleaned_code")

    # Embeddings for function definitions
    for func_name, func_code in code_dict['function_definitions']:
        func_embedding = hf_embedder.embed_query(func_code)
        embeddings.append(func_embedding)
        metadata.append(f"function_definition: {func_name}")

    # Embeddings for function calls
    for call_name, call_code in code_dict['function_calls']:
        call_embedding = hf_embedder.embed_query(call_code)
        embeddings.append(call_embedding)
        metadata.append(f"function_call: {call_name}")

    # Embeddings for external dependencies
    for i, dep_code in enumerate(code_dict['external_dependencies']):
        dep_embedding = hf_embedder.embed_query(dep_code)
        embeddings.append(dep_embedding)
        metadata.append(f"external_dependency: {i + 1}")

    return np.array(embeddings), metadata


# Step 1: Create FAISS index
def create_faiss_index(embeddings, dimension=384):
    """
    Create and return a FAISS index for the given embeddings.

    Args:
        embeddings (np.array): The array of embeddings to store in FAISS.
        dimension (int): Dimensionality of the embeddings (default is 384 for MiniLM).

    Returns:
        FAISS index
    """
    index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
    index.add(embeddings)
    return index


# Step 2: Perform search in FAISS
def search_faiss(query, index, metadata, top_k=3):
    """
    Search FAISS index for the closest matches to the query.

    Args:
        query (str): Input query string to search for.
        index (faiss.Index): FAISS index object.
        metadata (list): Metadata list corresponding to the embeddings in the index.
        top_k (int): Number of top matches to return (default is 3).

    Returns:
        list: Top k matches with their metadata and distances.
    """
    query_embedding = hf_embedder.embed_query(query)
    query_embedding = np.array(query_embedding).reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)  # Search FAISS index

    # Get the corresponding metadata and distances for the top-k results
    results = [(metadata[i], distances[0][idx]) for idx, i in enumerate(indices[0])]
    return results


# Example usage:

# Assuming `code_dict` is the dictionary with cleaned code and extracted components
code_dict = {
    "cleaned_code": "def add(a, b):\n    return a + b",
    "function_definitions": [("add", "def add(a, b):\n    return a + b")],
    "function_calls": [("add", "add(5, 3)")],
    "external_dependencies": ["import numpy as np"]
}

# Step 1: Create embeddings and corresponding metadata
embeddings, metadata = create_embeddings_for_faiss(code_dict)

# Step 2: Create a FAISS index for the embeddings
dimension = len(embeddings[0])  # Get the dimensionality from the embeddings
index = create_faiss_index(embeddings, dimension)

# Step 3: Perform a search using FAISS
query = "function to add two numbers"
top_k_results = search_faiss(query, index, metadata, top_k=3)

# Print out the results
print("Top matches:")
for match, distance in top_k_results:
    print(f"{match} with distance: {distance:.4f}")
