# Avery's part: tree formatter, evaluator, and evaluate_file integration

import os

# 1) TREE FORMATTER
# Converts Jane's parse tree (nested dicts) into prefix notation for output.
# Example: 2 + 3 * 4 -> (+ 2 (* 3 4))


def format_tree(node: dict) -> str:
    """Render a parse-tree node as a prefix-notation string."""
    t = node['type']

    # Number node
    if t == 'num':
        return str(node['value'])

    # Unary negative node
    if t == 'neg':
        return f"(neg {format_tree(node['operand'])})"

    # Binary operator node
    if t == 'binop':
        left_str = format_tree(node['left'])
        right_str = format_tree(node['right'])
        return f"({node['op']} {left_str} {right_str})"

    # Fallback for unexpected node type
    return 'ERROR'

# 2) EVALUATOR
# Walks the parse tree recursively and returns a float result.


def evaluate_node(node: dict) -> float:
    """
    Recursively evaluate a parse-tree node and return the float result.

    Raises ZeroDivisionError if division by zero is encountered.
    """
    t = node['type']

    # Number node
    if t == 'num':
        return float(node['value'])

    # Unary negative node
    if t == 'neg':
        return -evaluate_node(node['operand'])

    # Binary operator node
    if t == 'binop':
        left = evaluate_node(node['left'])
        right = evaluate_node(node['right'])
        op = node['op']

        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right

    raise ValueError(f"Unknown node type: {t}")


# 3) RESULT FORMATTER
# Formats result values for the output file:
# - Whole numbers are shown without decimal places.
# - Non-whole numbers are rounded to 4 decimal places.


def format_result_str(value: float) -> str:
    """
    Format a float result for the output file.

    Whole numbers (e.g. 8.0) -> '8'
    Non-whole numbers -> rounded to 4 decimal places (e.g. '1.2346')
    """
    rounded = round(value, 4)

    if rounded == int(rounded):
        return str(int(rounded))

    return f'{rounded:.4f}'


# 4) MAIN PUBLIC FUNCTION: evaluate_file
# Runs the full pipeline for each input expression:
# 1. tokenize
# 2. parse
# 3. format tree
# 4. evaluate
# 5. format result
# Writes output.txt in the same folder as the input file.


def evaluate_file(input_path: str) -> list:
    """
    Read mathematical expressions from input_path (one per line),
    evaluate each using recursive descent parsing, and write results
    to 'output.txt' in the same directory.

    Returns a list of dicts:
        {
            'input':  str  - the original expression string,
            'tree':   str  - prefix-notation tree string, or 'ERROR',
            'tokens': str  - formatted token string, or 'ERROR',
            'result': float or 'ERROR' - computed value on success
        }
    """
    abs_input = os.path.abspath(input_path)
    output_dir = os.path.dirname(abs_input)
    output_path = os.path.join(output_dir, 'output.txt')

    with open(abs_input, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    results = []
    output_blocks = []

    for line in lines:
        expr = line.rstrip('\n')

        # Step 1: tokenize
        tokens = tokenize(expr)

        if tokens is None:
            entry = {
                'input': expr,
                'tree': 'ERROR',
                'tokens': 'ERROR',
                'result': 'ERROR'
            }
            results.append(entry)
            output_blocks.append(
                f'Input: {expr}\nTree: ERROR\nTokens: ERROR\nResult: ERROR'
            )
            continue

        tokens_str = format_tokens(tokens)

        # Step 2: parse
        tree_node, parse_error = parse(tokens)

        if tree_node is None:
            entry = {
                'input': expr,
                'tree': 'ERROR',
                'tokens': tokens_str,
                'result': 'ERROR'
            }
            results.append(entry)
            output_blocks.append(
                f'Input: {expr}\nTree: ERROR\nTokens: {tokens_str}\nResult: ERROR'
            )
            continue

        tree_str = format_tree(tree_node)

        # Step 3: evaluate
        try:
            value = evaluate_node(tree_node)
            result_disp = format_result_str(value)
            entry = {
                'input': expr,
                'tree': tree_str,
                'tokens': tokens_str,
                'result': value
            }
        except (ZeroDivisionError, ValueError, OverflowError):
            result_disp = 'ERROR'
            entry = {
                'input': expr,
                'tree': tree_str,
                'tokens': tokens_str,
                'result': 'ERROR'
            }

        results.append(entry)
        output_blocks.append(
            f'Input: {expr}\nTree: {tree_str}\nTokens: {tokens_str}\nResult: {result_disp}'
        )

    output_content = '\n\n'.join(output_blocks) + '\n'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

    return results