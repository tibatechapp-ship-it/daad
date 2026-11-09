"""End-to-end tests: source .daad → Python that runs."""
from __future__ import annotations

import pytest

from daad.transpile import TranspileError, transpile


def _run(source: str) -> str:
    """Transpile + exec, capturing stdout."""
    import io
    import contextlib

    py = transpile(source)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(py, "<test>", "exec"), {"__name__": "__main__"})  # nosec B102
    return buf.getvalue()


def test_hello():
    out = _run('اطبع("مرحبا")\n')
    assert "مرحبا" in out


def test_arithmetic():
    out = _run('اطبع(2 + 3 * 4)\n')
    assert "14" in out


def test_function_call():
    out = _run(
        "دالة جمع(a, b):\n"
        "    أعد a + b\n"
        "اطبع(جمع(3, 4))\n"
    )
    assert "7" in out


def test_if_else():
    out = _run(
        "x = 5\n"
        "إذا x > 0:\n"
        "    اطبع(\"موجب\")\n"
        "وإلا:\n"
        "    اطبع(\"سالب\")\n"
    )
    assert "موجب" in out


def test_for_loop():
    out = _run(
        "لكل i في مدى(3):\n"
        "    اطبع(i)\n"
    )
    assert "0" in out and "2" in out


def test_while_loop():
    out = _run(
        "x = 0\n"
        "بينما x < 3:\n"
        "    اطبع(x)\n"
        "    x += 1\n"
    )
    assert "0" in out and "2" in out


def test_recursive_fib():
    out = _run(
        "دالة فيب(n):\n"
        "    إذا n <= 1:\n"
        "        أعد n\n"
        "    أعد فيب(n - 1) + فيب(n - 2)\n"
        "اطبع(فيب(7))\n"
    )
    assert "13" in out


def test_arabic_digits():
    out = _run("اطبع(٢ + ٣)\n")
    assert "5" in out


def test_syntax_error():
    with pytest.raises(TranspileError):
        transpile("دالة f(:\n    مرر\n")


def test_determinism():
    src = "دالة f(x):\n    أعد x + 1\nاطبع(f(1))\n"
    a = transpile(src)
    b = transpile(src)
    assert a == b
