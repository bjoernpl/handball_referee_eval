import re
from typing import Any, List

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, json_dataset
from inspect_ai.model import GenerateConfig
from inspect_ai.scorer import Score, Scorer, scorer
from inspect_ai.scorer._metrics import bootstrap_std, mean
from inspect_ai.scorer._target import Target
from inspect_ai.solver import TaskState, multiple_choice, system_message

SYSTEM_MESSAGE = """
You are a Handball referee and have to make a decision based on the following situation / question.
Multiple choices can be correct. Please select all correct answers. Wrongly selected answers will be scored negatively. Give your answer in the format specified below the question and with comma separated letters if multiple answers are correct.
"""


def record_to_sample(record):
    return Sample(
        input=record["question"],
        target=record["correct_answers"],
        choices=record["answers"],
        metadata=dict(
            question_number=record["question_number"],
            rule_references=record["rule_references"],
        ),
    )


def parse_answers(answer_string: str) -> List[str]:
    return [answer.strip().lower() for answer in answer_string.split(",")]


def calculate_score(selected: List[str], correct: List[str]) -> int:
    score = 0
    for answer in selected:
        if answer in correct:
            score += 1
        else:
            score -= 1
    return max(score, 0)  # Ensure the score is not negative


@scorer(metrics=[mean(), bootstrap_std()])
def multi_choice_pattern(pattern: str, ignore_case: bool = True) -> Scorer:
    """Scorer for multiple-choice questions with multiple possible correct answers.

    Args:
       pattern (str): Regular expression for extracting the answer from model output.
       ignore_case (bool): Ignore case when comparing the extracted answer to the targets. (Default: True)
    """

    async def score(state: TaskState, target: Target) -> Score:
        # Extract the answer
        match = re.search(
            pattern, state.output.completion, re.IGNORECASE if ignore_case else 0
        )

        if match:
            extracted_answer = match.group(1)
            selected_answers = parse_answers(extracted_answer)
            correct_answers = target.target

            score_value = calculate_score(selected_answers, correct_answers)
            max_score = len(correct_answers)

            normalized_score = score_value / max_score

            return Score(
                value=normalized_score,
                answer=", ".join(selected_answers),
                explanation=f"Selected: {selected_answers}, Correct: {correct_answers}, Score: {score_value}/{max_score}",
            )
        else:
            # Didn't find the scoring pattern
            return Score(
                value=0,
                explanation="Scoring pattern not matched in output: "
                + f"{state.output.completion}",
            )

    return score


@task
def handball_eval(use_rules: bool = False):
    # dataset
    dataset = json_dataset(
        json_file="merged_data.jsonl", sample_fields=record_to_sample
    )

    if use_rules:
        with open("rules.txt", "r") as f:
            rules = f.read()

        system = f"Handball Rules:\n\n{rules}\n\n{SYSTEM_MESSAGE}"
    else:
        system = SYSTEM_MESSAGE

    # define task
    return Task(
        dataset=dataset,
        plan=[
            system_message(system),
            multiple_choice(multiple_correct=True),
        ],
        scorer=multi_choice_pattern(r"ANSWER: ([\w,\s]+)"),
        config=GenerateConfig(temperature=0, max_tokens=32),
    )
