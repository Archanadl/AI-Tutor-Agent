# test_flashcards.py
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure Python can find your 'app' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ui.backend import get_flashcards, submit_flashcard_answer

def run_test():
    print("⏳ Testing Flashcard Generation (Calling LLM)...")
    
    # Generate 2 cards about Machine Learning
    cards = get_flashcards(topic="Machine Learning basics", count=2)
    
    if not cards:
        print("❌ Failed to generate cards. Check your LLM connection or prompt formatting.")
        return

    print("\n✅ Success! Here are your generated cards:")
    for i, card in enumerate(cards, 1):
        print(f"\n--- Card {i} ---")
        print(f"Front: {card.get('front')}")
        print(f"Back:  {card.get('back')}")

    print("\n------------------------------------------------")
    print("⏳ Testing SM-2 Algorithm...")
    print("Simulating a user rating the first card as 'Hard' (quality = 3)")
    
    # Simulating the first time a user sees a card and scores it a 3
    result = submit_flashcard_answer(
        quality=3, 
        previous_interval=0, 
        previous_repetitions=0, 
        previous_ease_factor=2.5
    )
    
    print(f"✅ Next SM-2 state calculated: {result}")

if __name__ == "__main__":
    run_test()