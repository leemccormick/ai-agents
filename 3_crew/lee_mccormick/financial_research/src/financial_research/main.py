#!/usr/bin/env python
import sys
import warnings

from financial_research.crew import FinancialResearch

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'company': 'Apple'
    }
    try:
        result = FinancialResearch().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    
if __name__ == "__main__":
    run()