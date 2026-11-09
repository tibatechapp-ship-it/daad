"""اختبارات امتداد VS Code — القواعد تطابق اللغة الفعلية حرفيًا.

الضمانة: كل كلمة محجوزة في daad.keywords وكل دالة مدمجة في
emitter.PRELUDE تظهر في ملف القواعد ككلمة كاملة — لا انحراف بين
اللغة المترجِمة والتلوين، مهما تطور الاثنان.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from daad.emitter import PRELUDE
from daad.keywords import KEYWORDS

EXT = Path(__file__).resolve().parent.parent / "editors" / "vscode"
GRAMMAR_PATH = EXT / "syntaxes" / "daad.tmLanguage.json"
LANGCFG_PATH = EXT / "language-configuration.json"
SNIPPETS_PATH = EXT / "snippets" / "daad.json"
PACKAGE_PATH = EXT / "package.json"

WORD = r"(?<![\w\u0600-\u06FF]){}(?![\w\u0600-\u06FF])"


def _grammar_text() -> str:
    return GRAMMAR_PATH.read_text(encoding="utf-8")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _builtins() -> list[str]:
    out = []
    for line in PRELUDE.splitlines():
        if " = " in line and not line.lstrip().startswith("#"):
            out.append(line.split(" = ", 1)[0].strip())
    return out


def test_extension_files_exist():
    for name in (
        "package.json",
        "language-configuration.json",
        "syntaxes/daad.tmLanguage.json",
        "snippets/daad.json",
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "icon.png",
    ):
        assert (EXT / name).is_file(), f"مفقود: {name}"


def test_all_json_files_parse():
    for name in (
        "package.json",
        "language-configuration.json",
        "syntaxes/daad.tmLanguage.json",
        "snippets/daad.json",
    ):
        _load(EXT / name)


def test_grammar_covers_every_keyword():
    text = _grammar_text()
    missing = [kw for kw in KEYWORDS if not re.search(WORD.format(re.escape(kw)), text)]
    assert not missing, f"كلمات محجوزة غائبة عن التلوين: {missing}"


def test_grammar_covers_every_builtin():
    text = _grammar_text()
    missing = [b for b in _builtins() if not re.search(WORD.format(re.escape(b)), text)]
    assert not missing, f"دوال مدمجة غائبة عن التلوين: {missing}"


def test_grammar_no_arabic_keyword_leaks_into_other_words():
    """الحدود صحيحة: «و» لا تُلوَّن داخل «وإلا» وهكذا."""
    grammar = _load(GRAMMAR_PATH)
    groups = grammar["repository"]["keywords"]["patterns"]
    # كل مجموعة كلمات محاطة بحدود الكلمة على الحافتين
    for group in groups:
        pattern = group["match"]
        assert pattern.startswith("(?<![\\w\\u0600-\\u06FF])"), group["name"]
        assert pattern.endswith("(?![\\w\\u0600-\\u06FF])"), group["name"]


def test_grammar_fstring_and_arabic_numbers():
    text = _grammar_text()
    assert "string.quoted.double.interpolated.daad" in text
    assert "meta.interpolation.daad" in text
    assert "comment.line.number-sign.daad" in text
    numbers = _load(GRAMMAR_PATH)["repository"]["numbers"]["patterns"][0]["match"]
    # الأرقام العربية الشرقية ٠-٩ (يقرؤها Oniguruma كـ \u0660-\u0669)
    assert "\\u0660-\\u0669" in numbers


def test_language_configuration():
    cfg = _load(LANGCFG_PATH)
    assert cfg["comments"]["lineComment"] == "#"
    assert len(cfg["brackets"]) == 3
    assert "increaseIndentPattern" in cfg["indentationRules"]
    # وإلا/وإلا_إذا/إلا/أخيراً تعود بالإزاحة إلى مستوى الأصل
    decrease = cfg["indentationRules"]["decreaseIndentPattern"]
    for kw in ("وإلا_إذا", "وإلا", "إلا", "أخيراً"):
        assert kw in decrease


def test_package_manifest():
    pkg = _load(PACKAGE_PATH)
    assert pkg["name"] == "daad-vscode"
    assert pkg["publisher"] == "tibatechapp"
    assert pkg["license"] == "Apache-2.0"
    lang = pkg["contributes"]["languages"][0]
    assert lang["extensions"] == [".daad"]
    assert lang["id"] == "daad"
    gram = pkg["contributes"]["grammars"][0]
    grammar = _load(GRAMMAR_PATH)
    assert gram["scopeName"] == grammar["scopeName"] == "source.daad"
    assert gram["language"] == "daad"


def test_snippets_valid_and_cover_core_constructs():
    snippets = _load(SNIPPETS_PATH)
    assert len(snippets) >= 10
    text_bodies = json.dumps(snippets, ensure_ascii=False)
    for kw in ("دالة", "إذا", "لكل", "بينما", "صنف", "حاول", "اطبع"):
        assert kw in text_bodies, f"قصاصة غائبة عن: {kw}"
    for name, snip in snippets.items():
        assert snip.get("prefix"), name
        assert snip.get("body"), name
