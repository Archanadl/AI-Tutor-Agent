from app.rag.retriever import retrieve


TEST_CASES = [
    {
        "question": "What is quantum computing?",
        "expected_answerable": True,
    },
    {
        "question": "What are the challenges of quantum computing?",
        "expected_answerable": True,
    },
    {
        "question": "What programming language was used to build the quantum computer?",
        "expected_answerable": False,
    },
]

DOCUMENT_ID = "research_report.pdf"


passed = 0


for test in TEST_CASES:

    question = test["question"]
    expected_answerable = test["expected_answerable"]

    print("\n" + "=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)

    documents = retrieve(
        question=question,
        document_id=DOCUMENT_ID,
    )

    print(f"Retrieved documents: {len(documents)}")

    for i, document in enumerate(documents, start=1):
        print(f"\nDocument {i}")
        print(f"Source: {document.metadata.get('source')}")
        print(f"Page: {document.metadata.get('page')}")
        print(
            f"Score: "
            f"{document.metadata.get('relevance_score', 'N/A'):.3f}"
        )
        print(f"Text: {document.page_content[:300]}")

    actual_answerable = len(documents) > 0

    # For an unanswerable question, we expect retrieval
    # not to return useful documents.
    if actual_answerable == expected_answerable:
        print("\n✅ PASS")
        passed += 1
    else:
        print("\n❌ FAIL")


print("\n" + "=" * 60)
print("RETRIEVAL EVALUATION")
print("=" * 60)

print(f"Passed: {passed}/{len(TEST_CASES)}")
print(f"Accuracy: {(passed / len(TEST_CASES)) * 100:.1f}%")