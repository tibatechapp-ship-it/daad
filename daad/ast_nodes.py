"""AST node definitions for Daad. All dataclasses; no logic here."""
from __future__ import annotations

from dataclasses import dataclass, field


# ── Base ─────────────────────────────────────────────────────
class Node:
    """Marker base class for all AST nodes."""

class Expression(Node):
    """Marker base for expression nodes."""

class Statement(Node):
    """Marker base for statement nodes."""


# ── Expressions ──────────────────────────────────────────────
@dataclass
class Name(Expression):
    id: str

@dataclass
class Number(Expression):
    value: str  # "42", "3.14" — always ASCII digits

@dataclass
class Str(Expression):
    value: str  # includes the surrounding quotes

@dataclass
class FString(Expression):
    value: str  # includes the f prefix and quotes — passed through to Python

@dataclass
class Bool(Expression):
    value: bool

@dataclass
class NoneLit(Expression):
    pass

@dataclass
class BinOp(Expression):
    left: Expression
    op: str
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

@dataclass
class Call(Expression):
    func: Expression
    args: list[Expression] = field(default_factory=list)

@dataclass
class Attribute(Expression):
    value: Expression
    attr: str

@dataclass
class Subscript(Expression):
    value: Expression
    index: Expression

@dataclass
class ListLit(Expression):
    elements: list[Expression] = field(default_factory=list)

@dataclass
class TupleLit(Expression):
    elements: list[Expression] = field(default_factory=list)

@dataclass
class DictLit(Expression):
    keys: list[Expression] = field(default_factory=list)
    values: list[Expression] = field(default_factory=list)


# ── Statements ───────────────────────────────────────────────
@dataclass
class Module(Node):
    body: list[Statement] = field(default_factory=list)

@dataclass
class FunctionDef(Statement):
    name: str
    params: list[str]
    body: list[Statement]

@dataclass
class ClassDef(Statement):
    name: str
    bases: list[str]
    body: list[Statement]

@dataclass
class If(Statement):
    test: Expression
    body: list[Statement]
    orelse: list[Statement] = field(default_factory=list)

@dataclass
class For(Statement):
    target: str
    iter: Expression
    body: list[Statement]

@dataclass
class While(Statement):
    test: Expression
    body: list[Statement]

@dataclass
class Return(Statement):
    value: Expression | None = None

@dataclass
class Assign(Statement):
    target: Expression  # Name, Subscript, or Attribute
    value: Expression

@dataclass
class AugAssign(Statement):
    target: Expression  # Name, Subscript, or Attribute
    op: str  # "+", "-", "*", "/"
    value: Expression

@dataclass
class ExprStmt(Statement):
    value: Expression

@dataclass
class Pass(Statement):
    pass

@dataclass
class Break(Statement):
    pass

@dataclass
class Continue(Statement):
    pass

@dataclass
class Import(Statement):
    module: str
    alias: str | None = None

@dataclass
class ImportFrom(Statement):
    module: str
    names: list[str] = field(default_factory=list)
