"""daad CLI: transpile / run / check."""
from __future__ import annotations

import sys
from pathlib import Path

from .transpile import TranspileError, transpile


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        _print_help(); return 0

    cmd, rest = argv[0], argv[1:]
    if cmd == "transpile": return _cmd_transpile(rest)
    if cmd == "run":       return _cmd_run(rest)
    if cmd == "check":     return _cmd_check(rest)
    if cmd == "repl":
        from .repl import repl
        return repl()
    if cmd == "version":
        from . import __version__
        print(f"daad {__version__}"); return 0

    print(f"أمر غير معروف: {cmd}", file=sys.stderr)
    return 2


def _print_help() -> None:
    print("""\
daad — Arabic Python transpiler

الاستخدام:
  daad transpile FILE.daad        # يحول إلى Python، يكتب FILE.py
  daad transpile FILE.daad -      # يطبع Python على stdout
  daad run FILE.daad              # يحول ثم ينفذ
  daad check FILE.daad            # يتحقق من الصياغة فقط
  daad repl                       # جلسة تفاعلية (Ctrl-D أو «خروج» للانتهاء)
  daad version                    # يعرض الإصدار

أمثلة:
  daad run examples/hello.daad
  daad transpile examples/fib.daad - | python
""")


def _read_source(path: Path) -> tuple[str, int]:
    if not path.exists():
        print(f"الملف غير موجود: {path}", file=sys.stderr); return "", 2
    try:
        src = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"خطأ قراءة: {path} ليس UTF-8", file=sys.stderr); return "", 2
    return src, 0


def _cmd_transpile(args: list[str]) -> int:
    if not args:
        print("الاستخدام: daad transpile FILE.daad [-]", file=sys.stderr); return 2
    src_path = Path(args[0])
    src, code = _read_source(src_path)
    if code: return code

    try:
        py = transpile(src)
    except TranspileError as e:
        print(f"خطأ: {e}", file=sys.stderr); return 1

    if len(args) > 1 and args[1] == "-":
        sys.stdout.write(py)
        return 0
    out_path = src_path.with_suffix(".py")
    out_path.write_text(py, encoding="utf-8")
    print(f"✅ {out_path}")
    return 0


def _cmd_run(args: list[str]) -> int:
    if not args:
        print("الاستخدام: daad run FILE.daad", file=sys.stderr); return 2
    src_path = Path(args[0])
    src, code = _read_source(src_path)
    if code: return code

    try:
        py = transpile(src)
    except TranspileError as e:
        print(f"خطأ: {e}", file=sys.stderr); return 1

    try:
        compiled = compile(py, str(src_path), "exec")
    except SyntaxError as e:
        print(f"خطأ مولد Python: {e}", file=sys.stderr); return 1

    try:
        exec(compiled, {"__name__": "__main__", "__file__": str(src_path)})  # nosec B102
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 0
    except Exception as e:
        print(f"خطأ تنفيذ: {type(e).__name__}: {e}", file=sys.stderr); return 1
    return 0


def _cmd_check(args: list[str]) -> int:
    if not args:
        print("الاستخدام: daad check FILE.daad", file=sys.stderr); return 2
    src_path = Path(args[0])
    src, code = _read_source(src_path)
    if code: return code
    try:
        transpile(src)
    except TranspileError as e:
        print(f"❌ {src_path}: {e}", file=sys.stderr); return 1
    print(f"✅ {src_path} — صالح")
    return 0


if __name__ == "__main__":
    sys.exit(main())
