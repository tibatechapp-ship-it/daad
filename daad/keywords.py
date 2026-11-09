"""الكلمات المحجوزة في لغة ضاد (Daad)."""
from __future__ import annotations

#: mapping: Arabic keyword → English Python keyword
KEYWORDS: dict[str, str] = {
    # control flow
    "إذا": "if",
    "وإلا": "else",
    "وإلا_إذا": "elif",
    # loops
    "لكل": "for",
    "بينما": "while",
    # functions & classes
    "دالة": "def",
    "أعد": "return",
    "صنف": "class",
    # modules
    "استورد": "import",
    "من": "from",
    "كما": "as",
    # exceptions
    "حاول": "try",
    "إلا": "except",
    "أخيراً": "finally",
    "ارفع": "raise",
    # misc
    "مرر": "pass",
    "اكسر": "break",
    "استمر": "continue",
    "مع": "with",
    "في": "in",
    "صح": "True",
    "خطأ": "False",
    "عدم": "None",
    "و": "and",
    "أو": "or",
    "ليس": "not",
    "هو": "is",
}

#: Arabic-Indic → ASCII digit translation table
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
