"""Interactive REPL for daad (ضاد).

State persists across inputs. Lines ending with ":" open a block that is
closed by a blank line. Expression lines echo their value like Python's REPL.
"""
from __future__ import annotations

from . import ast_nodes as ast
from .emitter import PRELUDE, emit_expr
from .lexer import LexError, _strip_comment, lex
from .parser import ParseError, parse
from .transpile import TranspileError, transpile

BANNER = "ضاد — Arabic Python REPL. اكتب «خروج» للخروج، أو Ctrl-D."
PROMPT = "ضاد> "
BLOCK_PROMPT = "…... "

_EXIT_WORDS = {"خروج", "exit", "quit", "exit()", "quit()"}


def _ends_block(line: str) -> bool:
    stripped = _strip_comment(line).rstrip()
    return bool(stripped) and stripped.endswith(":")


def repl(
    namespace: dict | None = None,
    input_fn=input,
    output_fn=print,
    banner: bool = True,
) -> int:
    """Run the interactive loop. input_fn/output_fn are injectable for tests."""
    ns = dict(namespace) if namespace else {"__name__": "__main__", "__doc__": None}
    exec(compile(PRELUDE, "<daad-prelude>", "exec"), ns)  # nosec B102
    if banner:
        output_fn(BANNER)

    buffer: list[str] = []
    while True:
        try:
            line = input_fn(BLOCK_PROMPT if buffer else PROMPT)
        except EOFError:
            if buffer:
                # Ctrl-D closes the pending block too
                _exec_block("\n".join(buffer) + "\n", ns, output_fn)
                buffer.clear()
            output_fn("")
            break
        except KeyboardInterrupt:
            buffer.clear()
            output_fn("(أُلغيت)")
            continue

        if line.strip() in _EXIT_WORDS:
            break

        if buffer:
            if not line.strip():
                _exec_block("\n".join(buffer) + "\n", ns, output_fn)
                buffer.clear()
            else:
                buffer.append(line)
            continue

        if not line.strip():
            continue
        if _ends_block(line):
            buffer.append(line)
            continue
        _exec_line(line, ns, output_fn)
    return 0


def _exec_line(src: str, ns: dict, output_fn) -> None:
    try:
        module = parse(lex(src))
        if len(module.body) == 1 and isinstance(module.body[0], ast.ExprStmt):
            code = compile(emit_expr(module.body[0].value), "<ضاد>", "eval")
            value = eval(code, ns)  # nosec B307
            if value is not None:
                output_fn(repr(value))
            return
        _exec_block(src, ns, output_fn)
    except (LexError, ParseError, TranspileError) as e:
        output_fn(f"خطأ: {e}")
    except Exception as e:
        output_fn(f"خطأ تنفيذ: {type(e).__name__}: {e}")


def _exec_block(src: str, ns: dict, output_fn) -> None:
    try:
        py = transpile(src)
        exec(compile(py, "<ضاد>", "exec"), ns)  # nosec B102
    except (LexError, ParseError, TranspileError) as e:
        output_fn(f"خطأ: {e}")
    except Exception as e:
        output_fn(f"خطأ تنفيذ: {type(e).__name__}: {e}")
