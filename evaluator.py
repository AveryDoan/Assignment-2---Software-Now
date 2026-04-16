

import os
# Tokeniser 

def tokenize(expr: str):
    tokens = []
    i = 0
    while i < len(expr):
        ch = expr[i]

        if ch.isspace():
            i += 1

        elif ch.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append({'type': 'NUM', 'value': int(expr[i:j])})
            i = j

        elif ch in '+-*/':
            tokens.append({'type': 'OP', 'value': ch})
            i += 1

        elif ch == '(':
            tokens.append({'type': 'LPAREN', 'value': '('})
            i += 1

        elif ch == ')':
            tokens.append({'type': 'RPAREN', 'value': ')'})
            i += 1

        else:
            return None 

    tokens.append({'type': 'END', 'value': None})
    return tokens


def format_tokens(tokens: list) -> str:
    parts = []
    for tok in tokens:
        t = tok['type']
        if t == 'END':
            parts.append('[END]')
        elif t == 'NUM':
            parts.append(f"[NUM:{tok['value']}]")
        elif t == 'OP':
            parts.append(f"[OP:{tok['value']}]")
        elif t == 'LPAREN':
            parts.append('[LPAREN:(]')
        elif t == 'RPAREN':
            parts.append('[RPAREN:)]')
    return ' '.join(parts)


# Recursive Descent Parser

def parse(tokens: list):

    pos = [0] 
    def current():
        return tokens[pos[0]]

    def consume():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    # -- Grammar rules

    def parse_expr():
        left = parse_term()
        while current()['type'] == 'OP' and current()['value'] in ('+', '-'):
            op = consume()['value']
            right = parse_term()
            left = {'type': 'binop', 'op': op, 'left': left, 'right': right}
        return left

    def parse_term():
        left = parse_unary()
        while True:
            cur = current()
            if cur['type'] == 'OP' and cur['value'] in ('*', '/'):
                op = consume()['value']
                right = parse_unary()
                left = {'type': 'binop', 'op': op, 'left': left, 'right': right}
            elif cur['type'] in ('NUM', 'LPAREN'):
                # Implicit multiplication: e.g. 2(3+4) or (2)(3)
                right = parse_unary()
                left = {'type': 'binop', 'op': '*', 'left': left, 'right': right}
            else:
                break
        return left

    def parse_unary():
        cur = current()
        if cur['type'] == 'OP' and cur['value'] == '-':
            consume()
            operand = parse_unary()
            return {'type': 'neg', 'operand': operand}
        if cur['type'] == 'OP' and cur['value'] == '+':
            raise ValueError("Unary '+' is not supported")
        return parse_primary()

    def parse_primary():
        cur = current()
        if cur['type'] == 'NUM':
            consume()
            return {'type': 'num', 'value': cur['value']}
        if cur['type'] == 'LPAREN':
            consume()
            node = parse_expr()
            if current()['type'] != 'RPAREN':
                raise ValueError("Expected closing parenthesis ')'")
            consume()
            return node
        if cur['type'] == 'END':
            raise ValueError("Unexpected end of expression")
        if cur['type'] == 'RPAREN':
            raise ValueError("Unexpected closing parenthesis ')'")
        raise ValueError(f"Unexpected token: {cur['type']}")

    # Entry point
    try:
        tree = parse_expr()
        if current()['type'] != 'END':
            raise ValueError(f"Unexpected token after expression: {current()['type']}")
        return tree, None
    except ValueError as exc:
        return None, str(exc)


# Tree formatter

def format_tree(node: dict) -> str:
    t = node['type']
    if t == 'num':
        return str(node['value'])             # integer literal, display as int
    if t == 'neg':
        return f"(neg {format_tree(node['operand'])})"
    if t == 'binop':
        return f"({node['op']} {format_tree(node['left'])} {format_tree(node['right'])})"
    return 'ERROR'


# Evaluator

def evaluate_node(node: dict) -> float:
    t = node['type']
    if t == 'num':
        return float(node['value'])
    if t == 'neg':
        return -evaluate_node(node['operand'])
    if t == 'binop':
        left  = evaluate_node(node['left'])
        right = evaluate_node(node['right'])
        op    = node['op']
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


def format_result_str(value: float) -> str:
    rounded = round(value, 4)
    if rounded == int(rounded):
        return str(int(rounded))
    return f'{rounded:.4f}'


# Main interface

def evaluate_file(input_path: str) -> list:
    abs_input  = os.path.abspath(input_path)
    output_dir = os.path.dirname(abs_input)
    output_path = os.path.join(output_dir, 'output.txt')

    with open(abs_input, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    results      = []
    output_blocks = []

    for line in lines:
        expr = line.rstrip('\n')

        # Step 1: Tokenise
        tokens = tokenize(expr)

        if tokens is None:
            # all fields are ERROR
            entry = {'input': expr, 'tree': 'ERROR', 'tokens': 'ERROR', 'result': 'ERROR'}
            results.append(entry)
            output_blocks.append(
                f'Input: {expr}\nTree: ERROR\nTokens: ERROR\nResult: ERROR'
            )
            continue

        tokens_str = format_tokens(tokens)

        # Step 2: Parse
        tree_node, parse_error = parse(tokens)

        if tree_node is None:
            # Parse failed – tokens are shown but tree and result are ERROR
            entry = {'input': expr, 'tree': 'ERROR', 'tokens': tokens_str, 'result': 'ERROR'}
            results.append(entry)
            output_blocks.append(
                f'Input: {expr}\nTree: ERROR\nTokens: {tokens_str}\nResult: ERROR'
            )
            continue

        tree_str = format_tree(tree_node)

        # Step 3: Evaluate
        try:
            value        = evaluate_node(tree_node)
            result_disp  = format_result_str(value)
            entry = {'input': expr, 'tree': tree_str, 'tokens': tokens_str, 'result': value}
        except (ZeroDivisionError, ValueError, OverflowError):
            result_disp = 'ERROR'
            entry = {'input': expr, 'tree': tree_str, 'tokens': tokens_str, 'result': 'ERROR'}

        results.append(entry)
        output_blocks.append(
            f'Input: {expr}\nTree: {tree_str}\nTokens: {tokens_str}\nResult: {result_disp}'
        )

    # Step 4: Write output file
    output_content = '\n\n'.join(output_blocks) + '\n'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)


# Main
if __name__ == "__main__":
    evaluate_file("sample_input.txt")