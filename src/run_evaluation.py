from src.evaluation.red_team_evaluator import RedTeamEvaluator
from src.main import MissionControl
from src.observability import logger

if __name__ == "__main__":
    # Specify the adversarial mission to run
    adversarial_mission_id = "red_team_scenario_001"
    llm_provider = "google_gemini"

    logger.info(f"Initializing red team evaluation for mission: {adversarial_mission_id}")

    # Initialize the control plane for that mission
    control_plane = MissionControl(adversarial_mission_id, llm_provider)

    # Initialize the evaluator with the control plane
    evaluator = RedTeamEvaluator(control_plane)

    # Run the evaluation
    evaluator.run_and_evaluate()
