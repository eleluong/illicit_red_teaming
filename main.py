from dotenv import load_dotenv
load_dotenv()

import logging

# from src.agent import run_agent
# from src.utils import generate_indirect_illicit_query, is_content_contain_true_intent, generate_test_cases

from src.bench import benchmark_illicit_behaviors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Run the benchmark for illicit behaviors
    benchmark_illicit_behaviors(
        num_iterations=20,
        num_cases=5,
        results_path="./results"
    )
