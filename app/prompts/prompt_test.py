from app.prompts.grader_prompt import GRADER_PROMPT
from app.prompts.generator_prompt import GENERATOR_PROMPT


def test_prompts():

    test_cases = [
        {
            "name": "Relevant Context",
            "question": "What is a Binary Search Tree?",
            "context": """
            A Binary Search Tree (BST) is a binary tree in which
            the left subtree contains values smaller than the root
            and the right subtree contains values greater than the root.
            """
        },

        {
            "name": "Irrelevant Context",
            "question": "What is a Binary Search Tree?",
            "context": """
            CPU scheduling is the process of selecting a process
            from the ready queue and allocating the CPU to it.
            """
        },

        {
            "name": "Partially Relevant Context",
            "question": "What are the advantages of a Binary Search Tree?",
            "context": """
            A Binary Search Tree is a binary tree in which
            the left subtree contains values smaller than the root
            and the right subtree contains values greater than the root.
            """
        },

        {
            "name": "Empty Context",
            "question": "What is a Binary Search Tree?",
            "context": ""
        }
    ]

    for test in test_cases:

        print("\n" + "=" * 60)
        print(test["name"])
        print("=" * 60)

        print(
            GRADER_PROMPT.format(
                question=test["question"],
                context=test["context"]
            )
        )

    print("\n" + "=" * 60)
    print("GENERATOR PROMPT TEST")
    print("=" * 60)

    question = "What is a Binary Search Tree?"

    context = """
    The Binary Search Tree (BST) is a binary tree in which
    the left subtree contains values smaller than the root
    and the right subtree contains values greater than the root.
    """

    print(
        GENERATOR_PROMPT.format(
            question=question,
            context=context
        )
    )


if __name__ == "__main__":
    test_prompts()