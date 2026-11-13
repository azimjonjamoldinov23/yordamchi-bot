"""Xavfsiz kalkulyator: eval() ishlatilmaydi, faqat ruxsat etilgan amallar bajariladi."""
from __future__ import annotations

import ast
import math
import operator

from app.utils.formatters import fmt_num


class CalcError(Exception):
    pass


_BIN = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_UN = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {"sqrt": math.sqrt, "abs": abs}
_CONSTS = {"pi": math.pi, "e": math.e}


def _normalize(expr: str) -> str:
    for old, new in (("×", "*"), ("÷", "/"), (":", "/"), ("−", "-"), ("^", "**"), (",", "."), ("x", "*")):
        expr = expr.replace(old, new)
    return expr.strip()


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow):
            if abs(right) > 1000:
                raise CalcError("Daraja juda katta.")
            if isinstance(left, int) and isinstance(right, int) and right > 0:
                if left.bit_length() * right > 20000:
                    raise CalcError("Natija juda katta.")
        try:
            result = _BIN[type(node.op)](left, right)
        except ZeroDivisionError:
            raise CalcError("Nolga bo'lib bo'lmaydi.") from None
        except OverflowError:
            raise CalcError("Natija juda katta.") from None
        if isinstance(result, complex):
            raise CalcError("Natija haqiqiy son emas.")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UN:
        return _UN[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name) and node.id.lower() in _CONSTS:
        return _CONSTS[node.id.lower()]
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id.lower() in _FUNCS
        and len(node.args) == 1
        and not node.keywords
    ):
        try:
            return _FUNCS[node.func.id.lower()](_eval(node.args[0]))
        except ValueError:
            raise CalcError("Bu amalni bajarib bo'lmaydi (masalan, manfiy sonning ildizi).") from None
    raise CalcError("Ifoda tushunarsiz yoki ruxsat etilmagan belgilar bor.")


def evaluate(expression: str):
    if not expression or len(expression) > 200:
        raise CalcError("Ifoda bo'sh yoki juda uzun.")
    try:
        tree = ast.parse(_normalize(expression), mode="eval")
    except (SyntaxError, ValueError):
        raise CalcError("Ifodani o'qib bo'lmadi. Masalan: 12*(3+4)") from None
    value = _eval(tree.body)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise CalcError("Natija juda katta.")
    return value


def format_result(value) -> str:
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        value = int(value)
    if isinstance(value, int):
        return f"{value:,}".replace(",", " ")
    return fmt_num(value, 10)
