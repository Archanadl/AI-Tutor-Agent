from app.rag.retriever import retrieve
from app.rag.vector_store import similarity_search


TEST_CASES = [
    {
        "question": "What is quantum computing?",
        "document_id": "test-document-001",
        "keywords": ["quantum", "quantum mechanics"],
        "answerable": True,
    },
    {
        "question": "What are the challenges of quantum computing?",
        "document_id": "test-document-001",
        "keywords": ["error", "scalability", "noise"],
        "answerable": True,
    },
    {
        "question": "What programming language was used to build the quantum computer?",
        "document_id": "test-document-001",
        "keywords": ["programming language"],
        "answerable": False,
    },
]


def evaluate_retrieval():
    total = len(TEST_CASES)
    passed = 0

    for case in TEST_CASES:
        print("\n" + "=" * 60)
        print("QUESTION:", case["question"])
        print("=" * 60)

        documents = retrieve(
            question=case["question"],
            document_id=case["document_id"],
            k=4,
        )

        print(f"Retrieved documents: {len(documents)}")

        found = False

        for i, document in enumerate(documents, start=1):
            text = document.page_content.lower()

            matched = [
                keyword
                for keyword in case["keywords"]
                if keyword.lower() in text
            ]

            print(f"\nDocument {i}")
            print("Source:", document.metadata.get("source"))
            print("Page:", document.metadata.get("page"))
            print("Matched keywords:", matched)

            if matched:
                found = True

        if case["answerable"]:
            if found:
                print("\n✅ RETRIEVAL PASS")
                passed += 1
            else:
                print("\n❌ RETRIEVAL FAIL")
        else:
            if not found:
                print("\n✅ CORRECTLY IDENTIFIED AS UNANSWERABLE")
                passed += 1
            else:
                print("\n❌ RETRIEVAL FAIL - IRRELEVANT CONTENT RETRIEVED")

    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Accuracy: {(passed / total) * 100:.1f}%")

def evaluate_retrieval_scores():
    questions = [
        "What is quantum computing?",
        "What are the challenges of quantum computing?",
        "What programming language was used to build the quantum computer?",
    ]

    for question in questions:
        print("\n" + "=" * 60)
        print("QUESTION:", question)
        print("=" * 60)

        results = similarity_search(
            query=question,
            document_id="test-document-001",
            k=4,
        )

        if not results:
            print("No documents retrieved.")
            continue

        for rank, (document, score) in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(f"Score: {score:.3f}")
            print(f"Source: {document.metadata.get('source')}")
            print(f"Page: {document.metadata.get('page')}")
            print(f"Text: {document.page_content[:200]}...")


if __name__ == "__main__":
    evaluate_retrieval()
    evaluate_retrieval_scores()