import re
import json


def extract_questions(content: str):
    content = content.replace("\f", "")
    # Regular expression to match question blocks
    question_pattern = r"(\d+\.\d+)\s*\)?\s*(.*?)(?=\n\d+\.\d+\s*\)|$)"

    # Find all matches
    matches = re.finditer(question_pattern, content, re.DOTALL)

    questions = []
    for match in matches:
        question_number = match.group(1)
        question_text = match.group(2).strip()

        # Split the question text into question and answers
        parts = re.split(r"\n([a-z])\)", question_text)
        question = parts[0].replace("\n", " ").strip()

        answers = []
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                answer = f"{parts[i]}) {parts[i+1].strip()}"
                answers.append(answer)

        # Remove page numbers and other extraneous text
        answers = [re.sub(r"\d+$", "", answer).strip() for answer in answers]
        answers = [re.sub(r"^[a-e]\)\s*", "", answer.strip()) for answer in answers]
        answers = [answer for answer in answers if not re.match(r"^\d+\.\d+\)", answer)]

        # Create a dictionary for the question
        question_dict = {
            "question_number": question_number,
            "question": question,
            "answers": answers,
        }

        questions.append(question_dict)

    return questions


def clean_content(content):
    # Remove headers and footers
    content = re.sub(r"Rule \d+\n", "", content)
    content = re.sub(r"\n\d+\n", "\n", content)
    return content


def write_jsonl(questions, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for question in questions:
            json.dump(question, f, ensure_ascii=False)
            f.write("\n")


# Read the content from the file
with open("handball_questions.txt", "r", encoding="utf-8") as file:
    content = file.read()

# Clean the content
cleaned_content = clean_content(content)

# Extract questions
extracted_questions = extract_questions(cleaned_content)

# Write to JSONL file
write_jsonl(extracted_questions, "questions.jsonl")

print(f"Extracted {len(extracted_questions)} questions and saved to questions.jsonl")
