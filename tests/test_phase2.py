"""Tests for daad Phase 2: f-strings, subscript/attribute assignment, native elif, REPL."""
from __future__ import annotations

import io
import contextlib

import pytest

from daad import ast_nodes as ast
from daad import TokenType, lex
from daad.emitter import emit_expr
from daad.lexer import LexError
from daad.parser import ParseError, parse
from daad.repl import repl
from daad.transpile import transpile


def _run(source: str) -> str:
    py = transpile(source)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(py, "<test>", "exec"), {"__name__": "__main__"})  # nosec B102
    return buf.getvalue()


# ── f-strings ────────────────────────────────────────────────

def test_fstring_lexed_as_fstring_token():
    ts = [t for t in lex('اطبع(f"مرحبا {الاسم}")') if t.type != TokenType.NEWLINE]
    fstr = [t for t in ts if t.type == TokenType.FSTRING]
    assert len(fstr) == 1
    assert fstr[0].value == 'f"مرحبا {الاسم}"'


def test_fstring_unterminated_raises():
    with pytest.raises(LexError, match="نص غير مغلق"):
        lex('اطبع(f"ناقص)')


def test_fstring_runs():
    out = _run('الاسم = "أحمد"\nاطبع(f"مرحبا {الاسم}")\n')
    assert "مرحبا أحمد" in out


def test_fstring_expression_runs():
    out = _run('اطبع(f"{2 + 3}")\n')
    assert "5" in out


def test_fstring_format_spec_runs():
    out = _run('اطبع(f"{3.14159:.2f}")\n')
    assert "3.14" in out


def test_fstring_single_quotes_run():
    out = _run("الاسم = 'سارة'\nاطبع(f'أهلًا {الاسم}')\n")
    assert "أهلًا سارة" in out


def test_emit_fstring_passthrough():
    assert emit_expr(ast.FString('f"س"')) == 'f"س"'


# ── index & attribute assignment ─────────────────────────────

def test_index_assignment_runs():
    out = _run("x = [1, 2, 3]\nx[0] = 9\nاطبع(x[0])\n")
    assert "9" in out


def test_index_augassign_runs():
    out = _run("q = [10]\nq[0] += 5\nاطبع(q[0])\n")
    assert "15" in out


def test_nested_subscript_assignment_runs():
    out = _run('م = {"أ": {"ب": 1}}\nم["أ"]["ب"] = 7\nاطبع(م["أ"]["ب"])\n')
    assert "7" in out


def test_attribute_assignment_runs():
    out = _run(
        "صنف نقطة:\n"
        "    مرر\n"
        "ن = نقطة()\n"
        "ن.س = 5\n"
        "ن.س += 2\n"
        "اطبع(ن.س)\n"
    )
    assert "7" in out


def test_invalid_target_raises():
    with pytest.raises(ParseError, match="هدف إسناد غير صالح"):
        parse(lex("مدى(3) = 5\n"))


# ── native elif ──────────────────────────────────────────────

def test_emit_native_elif():
    src = (
        "إذا x == 1:\n"
        "    اطبع(1)\n"
        "وإلا_إذا x == 2:\n"
        "    اطبع(2)\n"
        "وإلا:\n"
        "    اطبع(3)\n"
    )
    py = transpile(src)
    assert "elif" in py
    assert "وإلا_إذا" not in py


def test_elif_picks_correct_branch():
    out = _run(
        "x = 2\n"
        "إذا x == 1:\n"
        "    اطبع(\"واحد\")\n"
        "وإلا_إذا x == 2:\n"
        "    اطبع(\"اثنان\")\n"
        "وإلا:\n"
        "    اطبع(\"ثلاثة\")\n"
    )
    assert "اثنان" in out
    assert "واحد" not in out


# ── REPL ─────────────────────────────────────────────────────

def _repl(lines: list[str]) -> tuple[int, str]:
    it = iter(lines)
    outs: list[str] = []
    stdout_buf = io.StringIO()
    with contextlib.redirect_stdout(stdout_buf):
        code = repl(
            input_fn=lambda _p: next(it),
            output_fn=outs.append,
            banner=False,
        )
    out = "\n".join(outs)
    if stdout_buf.getvalue():
        out += "\n" + stdout_buf.getvalue()
    return code, out


def test_repl_persists_and_echoes():
    code, out = _repl(["س = 5", "س * 2", 'f"القيمة {س}"', "خروج"])
    assert code == 0
    assert "10" in out
    assert "القيمة 5" in out


def test_repl_block_function():
    code, out = _repl(["دالة ضعف(x):", "    أعد x * 2", "", "اطبع(ضعف(4))", "خروج"])
    assert code == 0
    assert "8" in out


def test_repl_survives_errors():
    code, out = _repl(["س = $", "دالة f(", "قيمة = 1", "خروج"])
    assert code == 0
    assert "خطأ" in out
    assert out.splitlines()[-1] != "خطأ"  # loop kept working afterwards


def test_repl_index_assignment_interactive():
    code, out = _repl(['د = {"ن": 1}', 'د["ن"] += 41', "د[\"ن\"]", "خروج"])
    assert code == 0
    assert "42" in out
