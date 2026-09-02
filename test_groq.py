from app.ui.backend import generate_mindmap

try:
    print("Generating...")
    mindmap_code = generate_mindmap(topic="TCP/IP Model")
    print("SUCCESS")
    print(mindmap_code)
except Exception as e:
    print(f"FAILED: {e}")
