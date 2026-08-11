from dotenv import load_dotenv
load_dotenv()

from app.graph import tutor_graph
# ... rest of your script
import os
from dotenv import load_dotenv

# 1. Find the exact folder where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Point directly to the .env file in that same folder
ENV_PATH = os.path.join(BASE_DIR, ".env")

# 3. Force load that specific file
load_dotenv(ENV_PATH)

# Now do your imports:
from app.graph import tutor_graph



def run_graph_test():
    print("\n" + "=" * 60)
    print("       AI TUTOR - LANGGRAPH TEST")
    print("=" * 60)

    # --------------------------------------------------
    # Initial state
    # --------------------------------------------------

    initial_state = {
        "student_question": "What is quantum computing?",
        "document_id": "research_report.pdf"
    }

    print("\nQuestion:")
    print(initial_state["student_question"])

    print("\nDocument ID:")
    print(initial_state["document_id"])

    print("\n" + "-" * 60)
    print("STARTING GRAPH")
    print("-" * 60)

    # --------------------------------------------------
    # Run the LangGraph
    # --------------------------------------------------

    final_state = tutor_graph.invoke(initial_state)

    # --------------------------------------------------
    # Display final result
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("              FINAL RESULT")
    print("=" * 60)

    print("\nRelevant:")
    print(final_state.get("relevant"))

    print("\nFinal Answer:")
    print("-" * 60)
    print(final_state.get("student_answer"))

    print("\n" + "=" * 60)
    print("             TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_graph_test()