"""High-level transpile pipeline: source → lex → parse → emit."""
from __future__ import annotations

from .emitter import emit_module
from .lexer import LexError, lex
from .parser import ParseError, parse


class TranspileError(Exception):
    """Any lexer, parser, or emitter error, unified."""


def transpile(source: str) -> str:
    try:
        tokens = lex(source)
        module = parse(tokens)
        return emit_module(module)
    except (LexError, ParseError) as e:
        raise TranspileError(str(e)) from e
