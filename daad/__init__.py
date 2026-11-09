"""Daad — Arabic Python transpiler."""
from __future__ import annotations

from .emitter import emit_module
from .lexer import LexError, Token, TokenType, lex
from .parser import ParseError, parse
from .transpile import TranspileError, transpile

__version__ = "0.2.0"
__all__ = [
    "lex", "Token", "TokenType", "LexError",
    "parse", "ParseError",
    "emit_module",
    "transpile", "TranspileError",
    "__version__",
]
