"""Tests for daad.parser."""
from __future__ import annotations

import pytest

from daad import ast_nodes as ast
from daad.lexer import lex
from daad.parser import ParseError, parse


def P(src: str) -> ast.Module:
    return parse(lex(src))


def test_empty_module():
    m = P("")
    assert m.body == []


def test_simple_function():
    m = P("دالة احسب(x):\n    أعد x + 1\n")
    assert len(m.body) == 1
    fn = m.body[0]
    assert isinstance(fn, ast.FunctionDef)
    assert fn.name == "احسب"
    assert fn.params == ["x"]
    assert len(fn.body) == 1
    assert isinstance(fn.body[0], ast.Return)


def test_two_statements():
    m = P("x = 5\nاطبع(x)\n")
    assert len(m.body) == 2
    assert isinstance(m.body[0], ast.Assign)
    assert isinstance(m.body[1], ast.ExprStmt)


def test_if_else():
    m = P("إذا x > 0:\n    اطبع(1)\nوإلا:\n    اطبع(2)\n")
    if_stmt = m.body[0]
    assert isinstance(if_stmt, ast.If)
    assert len(if_stmt.body) == 1
    assert len(if_stmt.orelse) == 1


def test_if_elif_else():
    m = P("إذا x == 1:\n    اطبع(1)\nوإلا_إذا x == 2:\n    اطبع(2)\nوإلا:\n    اطبع(3)\n")
    outer = m.body[0]
    assert isinstance(outer, ast.If)
    assert len(outer.orelse) == 1
    nested = outer.orelse[0]
    assert isinstance(nested, ast.If)
    assert len(nested.orelse) == 1


def test_for_loop():
    m = P("لكل i في مدى(3):\n    اطبع(i)\n")
    for_stmt = m.body[0]
    assert isinstance(for_stmt, ast.For)
    assert for_stmt.target == "i"


def test_while_loop():
    m = P("بينما x < 10:\n    x += 1\n")
    assert isinstance(m.body[0], ast.While)


def test_augassign():
    m = P("x += 5\n")
    assert isinstance(m.body[0], ast.AugAssign)
    assert m.body[0].op == "+"


def test_nested_call():
    m = P("اطبع(طول([1, 2, 3]))\n")
    expr = m.body[0].value
    assert isinstance(expr, ast.Call)
    assert isinstance(expr.args[0], ast.Call)


def test_empty_block_raises():
    with pytest.raises(ParseError, match="كتلة"):
        P("دالة f():\n")


def test_wrong_indent_raises():
    with pytest.raises(ParseError, match="محاذاة"):
        P("دالة f():\n    x = 1\n        y = 2\n")


def test_list_literal():
    m = P("x = [1, 2, 3]\n")
    assert isinstance(m.body[0].value, ast.ListLit)


def test_class_def():
    m = P("صنف Foo:\n    مرر\n")
    cls = m.body[0]
    assert isinstance(cls, ast.ClassDef)
    assert cls.name == "Foo"
