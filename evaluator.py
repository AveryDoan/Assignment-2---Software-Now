"""
HIT137 Assignment 2 - Question 2
Mathematical Expression Evaluator using Recursive Descent Parsing.
"""

from __future__ import annotations

import os


def tokenize(expr: str) -> list[dict] | None:
    """Convert expression text into tokens; return None on invalid character."""
    tokens: list[dict] = []
    i = 0

    while i < len(expr):
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append({"type": "NUM", "value": int(expr[i:j])})
            i = j
            continue

        if ch in "+-*/":
            tokens.append({"type": "OP", "value": ch})
            i += 1
            continue

        if ch == "(":
            tokens.append({"type": "LPAREN", "value": "("})
            i += 1
            continue

        if ch == ")":
            tokens.append({"type": "RPAREN", "value": ")"})
            i += 1
            continue

        return None

    tokens.append({"type": "END", "value": None})
    return tokens


def format_tokens(tokens: list[dict]) -> str:
    """Render tokens in required output format."""
    parts: list[str] = []
    for tok in tokens:
        token_type = tok["type"]
        if token_type == "END":
            parts.append("[END]")
        elif token_type == "NUM":
            parts.append(f"[NUM:{tok['value']}]")
        elif token_type == "OP":
            parts.append(f"[OP:{tok['value']}]")
        elif token_type == "LPAREN":
            parts.append("[LPAREN:(]")
        elif token_type == "RPAREN":
            parts.append("[RPAREN:)]")
    return " ".join(parts)


def parse(tokens: list[dict]) -> tuple[dict | None, str | None]:
    """Parse with recursive descent. Returns (tree, error)."""
    pos = [0]

    def current() -> dict:
        return tokens[pos[0]]

    def consume() -> dict:
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    def parse_expr() -> dict:
        left = parse_term()
        while current()["type"] == "OP" and current()["value"] in ("+", "-"):
            op = consume()["value"]
            right = parse_term()
            left = {"type": "binop", "op": op, "left": left, "right": right}
        return left

    def parse_term() -> dict:
        left = parse_unary()
        while True:
            cur = current()
            if cur["type"] == "OP" and cur["value"] in ("*", "/"):
                op = consume()["value"]
                right = parse_unary()
                left = {"type": "binop", "op": op, "left": left, "right": right}
                continue

            if cur["type"] in ("NUM", "LPAREN"):
                right = parse_unary()
                left = {"type": "binop", "op": "*", "left": left, "right": right}
                continue

            break
        return left

    def parse_unary() -> dict:
        cur = current()
        if cur["type"] == "OP" and cur["value"] == "-":
            consume()
            operand = parse_unary()
            return {"type": "neg", "operand": operand}
        if cur["type"] == "OP" and cur["value"] == "+":
            raise ValueError("Unary '+' is not supported")
        return parse_primary()

    def parse_primary() -> dict:
        cur = current()
        if cur["type"] == "NUM":
            consume()
            return {"type": "num", "value": cur["value"]}
        if cur["type"] == "LPAREN":
            consume()
            node = parse_expr()
            if current()["type"] != "RPAREN":
                raise ValueError("Expected closing parenthesis ')'")
            consume()
            return node
        if cur["type"] == "END":
            raise ValueError("Unexpected end of expression")
        if cur["type"] == "RPAREN":
            raise ValueError("Unexpected closing parenthesis ')'")
        raise ValueError(f"Unexpected token: {cur['type']}")

    try:
        tree = parse_expr()
        if current()["type"] != "END":
            raise ValueError(f"Unexpected token after expression: {current()['type']}")
        return tree, None
    except ValueError as exc:
        return None, str(exc)


def format_tree(node: dict) -> str:
    """Render parse tree in required prefix format."""
    node_type = node["type"]
    if node_type == "num":
        return str(node["value"])
    if node_type == "neg":
        return f"(neg {format_tree(node['operand'])})"
    if node_type == "binop":
        return f"({node['op']} {format_tree(node['left'])} {format_tree(node['right'])})"
    return "ERROR"


def evaluate_node(node: dict) -> float:
    """Recursively evaluate parse tree."""
    node_type = node["type"]
    if node_type == "num":
        return float(node["value"])
    if node_type == "neg":
        return -evaluate_node(node["operand"])
    if node_type == "binop":
        left = evaluate_node(node["left"])
        right = evaluate_node(node["right"])
        op = node["op"]
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
    raise ValueError(f"Unknown node type: {node_type}")


def format_result_str(value: float) -> str:
    """Whole numbers as ints; otherwise 4 d.p."""
    rounded = round(value, 4)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.4f}"


def evaluate_file(input_path: str) -> list[dict]:
    """
    Evaluate expressions from file and write output.txt in same directory.

    Returns a list of dictionaries with keys: input, tree, tokens, result.
    """
    abs_input = os.path.abspath(input_path)
    output_dir = os.path.dirname(abs_input)
    output_path = os.path.join(output_dir, "output.txt")

    with open(abs_input, "r", encoding="utf-8") as file_obj:
        lines = file_obj.readlines()

    results: list[dict] = []
    output_blocks: list[str] = []

    for line in lines:
        expr = line.rstrip("\n")
        tokens = tokenize(expr)

        if tokens is None:
            entry = {"input": expr, "tree": "ERROR", "tokens": "ERROR", "result": "ERROR"}
            results.append(entry)
            output_blocks.append(f"Input: {expr}\nTree: ERROR\nTokens: ERROR\nResult: ERROR")
            continue

        tokens_str = format_tokens(tokens)
        tree_node, _ = parse(tokens)

        if tree_node is None:
            entry = {"input": expr, "tree": "ERROR", "tokens": tokens_str, "result": "ERROR"}
            results.append(entry)
            output_blocks.append(
                f"Input: {expr}\nTree: ERROR\nTokens: {tokens_str}\nResult: ERROR"
            )
            continue

        tree_str = format_tree(tree_node)

        try:
            value = evaluate_node(tree_node)
            result_disp = format_result_str(value)
            entry = {"input": expr, "tree": tree_str, "tokens": tokens_str, "result": value}
        except (ZeroDivisionError, ValueError, OverflowError):
            result_disp = "ERROR"
            entry = {"input": expr, "tree": tree_str, "tokens": tokens_str, "result": "ERROR"}

        results.append(entry)
        output_blocks.append(
            f"Input: {expr}\nTree: {tree_str}\nTokens: {tokens_str}\nResult: {result_disp}"
        )

    with open(output_path, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n\n".join(output_blocks) + "\n")

    return results
