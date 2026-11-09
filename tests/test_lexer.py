"""Tests for daad.lexer."""
from __future__ import annotations

import pytest

from daad import LexError, TokenType, lex


def toks(src: str):
    return [t for t in lex(src) if t.type != TokenType.NEWLINE]


def test_keyword_if_maps_to_if():
    ts = toks("إذا صح:")
    assert ts[0].type == TokenType.KEYWORD
    assert ts[0].value == "إذا"
    assert ts[0].mapped == "if"


def test_identifier_arabic():
    ts = toks("متغير = 5")
    assert ts[0].type == TokenType.IDENT
    assert ts[0].value == "متغير"


def test_arabic_indic_digits_normalized():
    ts = toks("س = ٤٢")
    nums = [t for t in ts if t.type == TokenType.NUMBER]
    assert len(nums) == 1
    assert nums[0].value == "42"
    assert nums[0].mapped == "٤٢"   # original preserved


def test_mixed_digits():
    ts = toks("x = ١٢3")
    nums = [t for t in ts if t.type == TokenType.NUMBER]
    assert nums[0].value == "123"


def test_string_arabic():
    ts = toks('رسالة = "مرحبا"')
    strs = [t for t in ts if t.type == TokenType.STRING]
    assert len(strs) == 1
    assert strs[0].value == '"مرحبا"'


def test_comment_stripped():
    ts = toks("س = 5  # تعليق عربي")
    for t in ts:
        assert "تعليق" not in t.value


def test_hash_inside_string_not_a_comment():
    ts = toks('س = "a # b"')
    strs = [t for t in ts if t.type == TokenType.STRING]
    assert strs[0].value == '"a # b"'


def test_unclosed_string_raises():
    with pytest.raises(LexError, match="نص غير مغلق"):
        lex('س = "غير مكتمل')


def test_operator_two_char():
    ts = toks("س == 5")
    ops = [t for t in ts if t.type == TokenType.OP]
    assert ops[0].value == "=="


def test_operator_longest_match():
    ts = toks("س = ص ** 2")
    ops = [t for t in ts if t.type == TokenType.OP]
    assert ops[0].value == "="
    assert ops[1].value == "**"


def test_full_function():
    src = "دالة احسب(x):\n    أعد x + ١\n"
    ts = toks(src)
    assert ts[0].mapped == "def"
    assert any(t.mapped == "return" for t in ts)
    assert any(t.value == "1" for t in ts if t.type == TokenType.NUMBER)


def test_unknown_symbol_raises():
    with pytest.raises(LexError, match="رمز غير معروف"):
        lex("س = $")
