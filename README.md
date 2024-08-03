# Handball Eval

Evaluate LLMs on the 405 handball referee test questions from [the DHB](https://www.dhb.de/de/verband/schiedsrichter/regelwerk/).

Uses [inspect-ai](https://inspect.ai-safety-institute.org.uk/) to run the evaluations.

Install with `pip install -r requirements.txt` or `pip install inspect-ai openai anthropic mistralai`.

## Usage

Using the inspect eval framework, you can run an evaluation with the following command (after setting the respective api key ENV variable):

```bash
inspect eval handball_eval.py --model openai/gpt-4o
# inspect eval handball_eval.py --model mistral/mistral-large-latest
# inspect eval handball_eval.py --model together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
# inspect eval handball_eval.py --model anthropic/claude-3-5-sonnet-20240620
```

Afterwards you can look at the results with `inspect view`.

## Generating the dataset
Both the questions and the answers are from the dhb website and converted to txt. `extract_questions.py` extracts the questions from the txt files and saves them in a jsonl file which is the merged with the answers in `merge.py`. The final dataset is saved in `handball_questions_dataset.jsonl`.