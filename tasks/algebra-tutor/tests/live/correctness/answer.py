from pathlib import Path

from rewardkit import criterion
from shared_math import is_correct


@criterion(description="The final_answer and the conclusion in reply solve the original equation")
def correct_solution(workspace: Path) -> bool:
    return is_correct(workspace / "response.json")
