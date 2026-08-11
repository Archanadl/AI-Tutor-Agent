# Dummy retriever for testing
def retrieve(question: str, document_id: str):
    print("--- RETRIEVING CONTEXT ---")
    return f"This is a fake retrieved document explaining {question} from {document_id}."