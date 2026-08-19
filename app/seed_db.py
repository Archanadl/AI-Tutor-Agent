from app.rag.vector_store import get_vectorstore
from langchain_core.documents import Document

def seed_test_data():
    print("Connecting to vector store...")
    vs = get_vectorstore()
    
    # Create a mock retrieved chunk matching your test question
    test_doc = Document(
        page_content="A Binary Search Tree (BST) is a data structure where each node has at most two children. The left child must be strictly smaller than the parent, and the right child must be strictly greater.",
        metadata={"document_id": "test_doc_1"}
    )
    
    vs.add_documents([test_doc])
    print("✅ Test document successfully added to ChromaDB!")

if __name__ == "__main__":
    seed_test_data()