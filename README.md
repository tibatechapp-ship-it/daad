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
daad repl                               # جلسة تفاعلية
zyko py examples/hello.daad --run       # عبر بوابة ZYKO (اختياري)
```

## امتداد VS Code

تلوين صياغة كامل و12 قصاصة برمجية للملفات `.daad` — في
[`editors/vscode/`](editors/vscode/):

```bash
cd editors/vscode
npx @vscode/vsce package
code --install-extension daad-vscode-0.1.0.vsix
```

القواعد مُتحقق منها بمحرك VS Code الحقيقي (vscode-textmate +
Oniguruma): 27 كلمة محجوزة، الدوال المدمجة، f-strings، والأرقام
العربية الشرقية ٠-٩ — كلها مغطاة باختبارات لا تنحرف عن
`keywords.py` و`PRELUDE`.

## ما الجديد في 0.2.0

- **جلسة تفاعلية** `daad repl` — حالة دائمة، سطور التعبيرات تطبع قيمتها، الكتل تُغلق بسطر فارغ، `خروج` أو Ctrl-D للانتهاء.
- **إسناد الفهرس والخاصية**: `x[i] = v` و `x[i] += v` و `obj.attr = v` (والفهرس المتداخل `م["أ"]["ب"] = 7`).
- **f-strings عربية**: `f"مرحبا {الاسم}"` — تمر كما هي إلى بايثون، بما فيها صيغ التنسيق `f"{3.14159:.2f}"`.
- **elif أصلي**: سلاسل وإلا_إذا تُصدَّر `elif` بايثوني نظيف بدل else/if المتداخلة.

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
