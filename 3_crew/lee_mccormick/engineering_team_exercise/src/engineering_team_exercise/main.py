#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from engineering_team_exercise.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

business_idea = """
A simple Point-of-Sale (POS) system designed for small to mid-sized restaurants.

The system should allow a staff member to:
- View and search a digital menu.
- Add menu items (with quantity) to a customer’s order/cart.
- Remove or update items in the cart.
- Automatically calculate subtotal, tax, and total.
- Submit the order to the kitchen or mark it as paid.

Additional features:
- Apply discounts or promo codes.
- Track item availability (e.g., out-of-stock).
- Generate digital or printable receipts.

The system will be single-user and optimized for tablet use in demo environments.
"""

def run():
    """
    Run the research crew.
    """
    inputs = {
        'business_idea': business_idea,
    }

    # Create and run the crew
    result = EngineeringTeam().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()