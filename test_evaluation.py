from app.rag.retriever import run_rag_query


test_cases = [
    {
        "question": "What is quantum computing?",
        "expected_source": "document"
    },
    {
        "question": "What are the challenges of quantum computing?",
        "expected_source": "document"
    },
    {
        "question": "What is the latest version of Java?",
        "expected_source": "web_search"
    },
    {
        "question": "Who is the current Prime Minister of Japan?",
        "expected_source": "web_search"
    }
]


for i, test in enumerate(test_cases, start=1):

    print("\n" + "=" * 60)
    print(f"TEST {i}")
    print("=" * 60)

    print("Question:", test["question"])
    print("Expected source:", test["expected_source"])

    result = run_rag_query(
        question=test["question"],
        document_id="test-document-001"
    )

    print("\nActual source:", result.get("source_type"))
    print("Answer:", result.get("answer"))

    if result.get("source_type") == test["expected_source"]:
        print("PASS")
    else:
        print("FAIL")