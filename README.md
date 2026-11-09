# ضاد (daad) — Arabic Python

اكتب بايثون بالعربية. حتمي. بلا اعتماديات.

```daad
دالة احسب(x):
    أعد x + ١

اطبع(احسب(٥))
```

↓ `daad run file.daad` ↓

```
6
```

## التثبيت

```bash
git clone https://github.com/tibatechapp-ship-it/daad.git
cd daad
pip install -e .
```

## الاستخدام

```bash
daad run examples/fibonacci.daad
daad transpile examples/hello.daad -    # يطبع Python
daad check examples/hello.daad          # تحقق فقط
```

## الكلمات المحجوزة

| العربية | Python |
|:---|:---|
| إذا / وإلا / وإلا_إذا | if / else / elif |
| لكل / بينما | for / while |
| دالة / أعد | def / return |
| صنف | class |
| استورد / من / كما | import / from / as |
| صح / خطأ / عدم | True / False / None |
| و / أو / ليس | and / or / not |
| في / هو | in / is |

## الدوال المدمجة (عربية)

`اطبع`, `مدى`, `طول`, `نص`, `عدد`, `عشري`, `قائمة`, `قاموس`, `مدخل`.

## المبدأ

- **حتمي:** نفس المصدر → نفس البايتات
- **بلا نموذج:** لا LLM، لا شبكة
- **بلا اعتماديات:** Python 3.11+، فقط
- **بسيط:** يترجم إلى Python نظيف يمكنك قراءته

## الترخيص

Apache-2.0
