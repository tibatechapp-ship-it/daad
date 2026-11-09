"""Tests for daad.emitter."""
from __future__ import annotations

from daad import ast_nodes as ast
from daad.emitter import emit_expr, emit_module, emit_stmt


def test_emit_name():
    assert emit_expr(ast.Name("x")) == "x"


def test_emit_binop_wrapped():
    expr = ast.BinOp(ast.Name("a"), "+", ast.Name("b"))
    assert emit_expr(expr) == "(a + b)"


def test_emit_call():
    expr = ast.Call(ast.Name("f"), [ast.Number("1"), ast.Number("2")])
    assert emit_expr(expr) == "f(1, 2)"


def test_emit_assign():
    lines = emit_stmt(ast.Assign("x", ast.Number("5")), 0)
    assert lines == ["x = 5"]


def test_emit_function():
    fn = ast.FunctionDef("f", ["x"], [ast.Return(ast.Name("x"))])
    lines = emit_stmt(fn, 0)
    assert lines == ["def f(x):", "    return x"]


def test_emit_if_else():
    node = ast.If(
        ast.Name("x"),
        [ast.Pass()],
        [ast.Pass()],
    )
    lines = emit_stmt(node, 0)
    assert lines[0] == "if x:"
    assert "else:" in lines


def test_emit_module_prelude():
    out = emit_module(ast.Module([]))
    assert "اطبع = print" in out
    assert "مدى = range" in out


def test_emit_empty_block_gets_pass():
    fn = ast.FunctionDef("f", [], [])
    lines = emit_stmt(fn, 0)
    assert lines[1] == "    pass"
