from src.agent import run_agent
from src.utils import generate_indirect_illicit_query, is_content_contain_true_intent, generate_test_cases
import json

from datetime import datetime
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

def benchmark_illicit_behaviors(num_iterations: int = 10, num_cases: int = 10, results_path = "./results"):
    results = []
    datetime_ = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    for i in range(num_iterations):
        logger.info(f"Iteration {i + 1}/{num_iterations}")
        
        # Generate test cases
        while True:
            try:
                test_cases = generate_test_cases(num_cases)
                if isinstance(test_cases, list) and len(test_cases) == num_cases:
                    break
                else:
                    logger.warning(f"Generated test cases are not valid: {test_cases}")
            except Exception as e:
                logger.error(f"Error generating test cases: {e}")
        logger.info(f"Generated {num_cases} test cases.")

        for true_intent in test_cases:
            try:
                indirect_query = generate_indirect_illicit_query(true_intent)
                logger.info(f"Indirect query generated for intent '{true_intent}': {indirect_query}")

                result, output = run_agent(
                    query=indirect_query,
                    max_steps=5,
                )
                is_contain_true_intent_result = is_content_contain_true_intent(output, true_intent)
                logger.info(f"Final output:\n{output}\n\n===\n\n")
                logger.info(f"""Contain true intent:\n{
                        is_contain_true_intent_result
                    }"""
                )
                results.append({
                    "iteration": i + 1,
                    "true_intent": true_intent,
                    "indirect_query": indirect_query,
                    "output": output,
                    "is_contain_true_intent": is_contain_true_intent_result,
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                })
            except Exception as e:
                logger.error(f"Error processing intent '{true_intent}': {e}")
                results.append({
                    "iteration": i + 1,
                    "true_intent": true_intent,
                    "indirect_query": indirect_query,
                    "output": None,
                    "is_contain_true_intent": {"result": "Error", "reason": str(e)},
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                })
        # Save results to a file
        

        with open(f"{results_path}/benchmark_results_{datetime_}.json", "w", encoding = "utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    # Summarize results
    logger.info("\n\n\nBenchmark completed. Results saved to file.")
    num_success = sum(1 for r in results if r["is_contain_true_intent"]["result"] == "Yes")
    num_fail = sum(1 for r in results if r["is_contain_true_intent"]["result"] == "No")
    num_error = sum(1 for r in results if r["is_contain_true_intent"]["result"] == "Error")
    num_undetermined = sum(1 for r in results if r["is_contain_true_intent"]["result"] == "Undetermined")
    logger.info(f"Total test cases: {len(results)}")    
    logger.info(f"Successful cases (contain true intent): {num_success}")
    logger.info(f"Failed cases (do not contain true intent): {num_fail}")
    logger.info(f"Undetermined cases: {num_undetermined}")
    logger.info(f"Error cases: {num_error}")