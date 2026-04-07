# HIT137 Assignment 2 (S1 2026)

GitHub repository: https://github.com/AveryDoan/Assignment-2---Software-Now

## Project Contents

- `assignment2.ipynb`: Complete worked solutions for Question 1 and Question 2 with explanation.
- `evaluator.py`: Required interface for Question 2 (`evaluate_file(input_path: str) -> list[dict]`).
- `sample_input.txt`: Provided sample expressions.
- `sample_output.txt`: Provided expected output.
- `github_link.txt`: Repository link for submission package.

## Question 1 Summary

Implements file-based encryption and decryption for `raw_text.txt` using user-provided `shift1` and `shift2`, then verifies that decrypted output matches the original text.

## Question 2 Summary

Implements a recursive descent parser and evaluator with:

- tokenization (`NUM`, `OP`, `LPAREN`, `RPAREN`, `END`)
- precedence-aware parsing for `+`, `-`, `*`, `/`
- nested parentheses
- unary negation (`-`) and rejection of unary plus (`+`)
- implicit multiplication (e.g., `2(3+4)`)

Writes `output.txt` in the input file directory and returns a list of result dictionaries.

## Run Notes

Use the notebook for explanation and demonstrations. For Question 2 module use:

```python
from evaluator import evaluate_file
results = evaluate_file("sample_input.txt")
```
