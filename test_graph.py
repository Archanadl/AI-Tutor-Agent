from app.graph.graph import tutor_graph

def run_graph_test():
    print("--- STARTING LANGGRAPH TEST ---")
    
    # 1. Define the initial state (what the user asks)
    initial_state = {
        "student_question": "What is a Binary Search Tree?",
        "student_answer": "It is a tree where everything is sorted.",
        # We leave the other fields empty for the nodes to fill in
    }
    
    print("\nStarting Graph Execution...\n")
    
    # 2. Run the graph and print the output at each step
    for event in tutor_graph.stream(initial_state):
        for node_name, state_update in event.items():
            print(f"--- Just finished node: '{node_name}' ---")
            print(f"State Update: {state_update}\n")

if __name__ == "__main__":
    run_graph_test()