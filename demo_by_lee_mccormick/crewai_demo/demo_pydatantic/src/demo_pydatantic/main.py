import sys
from demo_pydatantic.crew import DemoCrew
from datetime import datetime

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI Agents in 2025',
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    DemoCrew().crew().kickoff(inputs=inputs)