"""Lexer for Daad (Arabic Python).

Turns Arabic source text into a flat stream of typed tokens. Handles:
* Arabic keywords (إذا، دالة، أعد، ...)
* Arabic-Indic numerals (٠١٢٣٤٥٦٧٨٩ → 0-9)
* Arabic identifiers (letters + digits + underscore, Unicode range)
* String literals with escapes
* Comments (# تعليق)
* Operators (longest match first)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .keywords import ARABIC_DIGITS, KEYWORDS


class TokenType(Enum):
    KEYWORD = "KEYWORD"
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    STRING = "STRING"
    FSTRING = "FSTRING"
    OP = "OP"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str          # raw text (or normalized for NUMBER)
    line: int
    col: int
    mapped: str | None = None   # for KEYWORD, the English equivalent

    def __repr__(self) -> str:
        m = f" → {self.mapped}" if self.mapped else ""
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col}{m})"


OPERATORS: tuple[str, ...] = (
    "==", "!=", "<=", ">=", "->", "**", "//", "+=", "-=", "*=", "/=",
    "=", "<", ">", "+", "-", "*", "/", "%",
    ":", ",", ".", "(", ")", "[", "]", "{", "}",
    "@", "&", "|", "^", "~",
)

IDENT_RE = re.compile(r"[A-Za-z_\u0600-\u06FF][A-Za-z0-9_\u0600-\u06FF]*")


class LexError(Exception):
    def __init__(self, msg: str, line: int, col: int) -> None:
        super().__init__(f"{msg} (السطر {line}، العمود {col})")
        self.line = line
        self.col = col


def lex(source: str) -> list[Token]:
    """Tokenize Daad source. Returns a list (easier to test than an iterator)."""
    tokens: list[Token] = []
    for line_no, raw_line in enumerate(source.splitlines(), start=1):
        line = _strip_comment(raw_line)
        i, n = 0, len(line)
        while i < n:
            ch = line[i]

            if ch in " \t":
                i += 1
                continue

            if ch in "\"'":
                j = i + 1
                while j < n and line[j] != ch:
                    j += 2 if line[j] == "\\" else 1
                if j >= n:
                    raise LexError("نص غير مغلق", line_no, i + 1)
                tokens.append(Token(TokenType.STRING, line[i : j + 1], line_no, i + 1))
                i = j + 1
                continue

            if ch.isdigit() or ch in "٠١٢٣٤٥٦٧٨٩":
                j = i
                while j < n and (line[j].isdigit() or line[j] in "٠١٢٣٤٥٦٧٨٩."):
                    j += 1
                raw = line[i:j]
                tokens.append(Token(TokenType.NUMBER, raw.translate(ARABIC_DIGITS), line_no, i + 1, raw))
                i = j
                continue

            m = IDENT_RE.match(line, i)
            if m:
                word = m.group(0)
                # f-string: the letter f/F glued to a quote opens a formatted literal,
                # lexed raw (prefix + quotes included) and passed through to Python.
                if word in ("f", "F") and i + 1 < n and line[i + 1] in "\"'":
                    quote = line[i + 1]
                    j = i + 2
                    while j < n and line[j] != quote:
                        j += 2 if line[j] == "\\" else 1
                    if j >= n:
                        raise LexError("نص غير مغلق", line_no, i + 1)
                    tokens.append(Token(TokenType.FSTRING, line[i : j + 1], line_no, i + 1))
                    i = j + 1
                    continue
                if word in KEYWORDS:
                    tokens.append(Token(TokenType.KEYWORD, word, line_no, i + 1, KEYWORDS[word]))
                else:
                    tokens.append(Token(TokenType.IDENT, word, line_no, i + 1))
                i = m.end()
                continue

            for op in OPERATORS:
                if line.startswith(op, i):
                    tokens.append(Token(TokenType.OP, op, line_no, i + 1))
                    i += len(op)
                    break
            else:
                raise LexError(f"رمز غير معروف: {ch!r}", line_no, i + 1)

        tokens.append(Token(TokenType.NEWLINE, "\\n", line_no, len(line) + 1))

    tokens.append(Token(TokenType.EOF, "", len(source.splitlines()) + 1, 1))
    return tokens


def _strip_comment(line: str) -> str:
    """Cut a line at the first '#' that's not inside a string literal."""
    in_str: str | None = None
    for i, ch in enumerate(line):
        if in_str:
            if ch == in_str:
                in_str = None
        elif ch in "\"'":
            in_str = ch
        elif ch == "#":
            return line[:i]
    return line
