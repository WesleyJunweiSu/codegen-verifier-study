"""Syntactic and public-example checks only; no hidden labels and no code execution."""
from __future__ import annotations

import ast
import re


def parse_assertions(text: str) -> tuple[list[str], list[str]]:
    fence=re.search(r"```(?:python)?\s*(.*?)```",text,re.S|re.I)
    text=(fence.group(1) if fence else text).strip()
    try:
        tree=ast.parse(text)
    except SyntaxError:
        return [],["syntax_error"]
    assertions=[];errors=[]
    for node in tree.body:
        if isinstance(node,ast.Assert):
            assertions.append(ast.unparse(node))
        else:
            errors.append("non_assert_statement:"+type(node).__name__)
    return assertions,errors


def public_assertions(prompt: str) -> list[str]:
    result=[]
    for line in prompt.splitlines():
        if line.strip().startswith("assert "):
            statements,_=parse_assertions(line.strip())
            result.extend(statements)
    return result


def _literal_equality(statement: str):
    expression=ast.parse(statement).body[0].test
    if not isinstance(expression,ast.Compare) or len(expression.ops)!=1 or not isinstance(expression.ops[0],ast.Eq):
        return None
    try:
        expected=ast.literal_eval(expression.comparators[0])
    except (ValueError,TypeError):
        return None
    return ast.dump(expression.left,include_attributes=False),expected


def assess_tests(assertions: list[str],prompt: str,entry_point: str) -> list[dict]:
    known=[pair for statement in public_assertions(prompt) if (pair:=_literal_equality(statement)) is not None]
    seen=set();result=[]
    for index,statement in enumerate(assertions):
        reasons=[]
        tree=ast.parse(statement)
        normalized=ast.dump(tree,include_attributes=False)
        if normalized in seen: reasons.append("duplicate")
        seen.add(normalized)
        expression=tree.body[0].test
        calls=[node for node in ast.walk(expression) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id==entry_point]
        if not calls: reasons.append("no_target_call")
        if isinstance(expression,ast.Compare) and len(expression.ops)==1:
            right=expression.comparators[0]
            if isinstance(expression.ops[0],(ast.Eq,ast.Is,ast.LtE,ast.GtE)) and ast.dump(expression.left)==ast.dump(right):
                reasons.append("tautology")
            if any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id==entry_point for node in ast.walk(right)):
                reasons.append("self_oracle")
        pair=_literal_equality(statement)
        if pair is not None:
            for public_call,public_expected in known:
                if pair[0]==public_call and pair[1]!=public_expected:
                    reasons.append("contradicts_public_example")
        result.append({"test_index":index,"assertion":statement,"keep":not reasons,"reasons":reasons})
    return result
