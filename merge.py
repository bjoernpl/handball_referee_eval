import json


def load_jsonl(file_path):
    with open(file_path, "r") as file:
        return [json.loads(line) for line in file]


def merge_data(questions, answers):
    merged = {}
    for question in questions:
        question_number = question["question_number"]
        merged[question_number] = question

    for answer in answers:
        question_number = answer["question_number"]
        if question_number in merged:
            merged[question_number].update(answer)

    return list(merged.values())


def save_jsonl(data, file_path):
    with open(file_path, "w") as file:
        for item in data:
            json.dump(item, file)
            file.write("\n")


# File paths
questions_file = "questions.jsonl"
answers_file = "answers.jsonl"
output_file = "merged_data.jsonl"

# Load data
questions = load_jsonl(questions_file)
answers = load_jsonl(answers_file)

# Merge data
merged_data = merge_data(questions, answers)

print(f"Merged {len(merged_data)} items")
merged_data = [item for item in merged_data if "correct_answers" in item]
print(f"Merged {len(merged_data)} items")

# Save merged data
save_jsonl(merged_data, output_file)

print(f"Merged data saved to {output_file}")
