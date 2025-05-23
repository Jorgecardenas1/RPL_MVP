import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator import Orchestrator


def test_create_and_log_experiment():

    orch = Orchestrator()

    # Step 1: Create project
    result1 = orch.process({
        "intent": "create_project",
        "data": {
            "project_name": "Quantum Sensors",
            "description": "Exploring entangled states."
        }
    })
    assert result1["status"] == "success"

    # Step 2: Log experiment
    result2 = orch.process({
        "intent": "log_experiment",
        "data": {
            "project": "Quantum Sensors",
            "results_file": "s21.csv"
        }
    })
    assert result2["status"] == "success"
