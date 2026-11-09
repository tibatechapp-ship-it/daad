<div dir="rtl">

# ضاد لـ Visual Studio Code — امتداد الرسمي للغة daad

تلوين الصياغة، القوسية التلقائية، القصاصات البرمجية، والمحاذاة
الذكية لملفات **`.daad`** — لغة **ضاد**: بايثون عربي حتمي
([المستودع الرئيسي](https://github.com/tibatechapp-ship-it/daad)).

## المزايا

- **تلوين كامل**: الكلمات المحجوزة العربية الـ27، الدوال المدمجة
  التسع، النصوص والـf-strings العربية (`f"مرحبا {الاسم}"`)، الأرقام
  العربية الشرقية `٠١٢٣٤٥٦٧٨٩`، التعليقات، وعوامل التشغيل.
- **أسماء الدوال والأصناف** تُميَّز تلقائيًا بعد `دالة` و`صنف`.
- **محاذاة ذكية**: السطر الجديد بعد `:` يزيد الإزاحة، و`وإلا` /
  `وإلا_إذا` / `إلا` / `أخيراً` يعود بها إلى مستوى الأصل.
- **قوسية تلقائية** وإحاطة لـ `()` `[]` `{}` `"` `'`.
- **12 قصاصة برمجية**: دالة، إذا/وإلا، لكل، بينما، صنف، حاول،
  اطبع، استورد، f-string — ببادئات عربية وإنجليزية معًا.

## التثبيت من المصدر

```bash
git clone https://github.com/tibatechapp-ship-it/daad.git
cd daad/editors/vscode
npx @vscode/vsce package
code --install-extension daad-vscode-0.1.0.vsix
```

للاستخدام الكامل (تشغيل الملفات): ثبّت المترجم نفسه

```bash
pip install git+https://github.com/tibatechapp-ship-it/daad.git
daad run ملفك.daad        # أو: zyko py ملفك.daad --run
```

## خريطة الألوان (نطاقات TextMate)

| العنصر | النطاق |
| --- | --- |
| الكلمات المحجوزة (إذا، لكل، دالة…) | `keyword.control.*` / `keyword.declaration.*` |
| و / أو / ليس / في / هو | `keyword.operator.logical` |
| صح / خطأ / عدم | `constant.language` |
| الدوال المدمجة (اطبع، مدى، طول…) | `support.function.builtin` |
| النصوص العادية | `string.quoted.double` / `single` |
| f-strings | `string.quoted.*.interpolated` + `meta.interpolation` |
| الأرقام (بما فيها ٠-٩) | `constant.numeric` |
| التعليقات `#` | `comment.line.number-sign` |
| أسماء الدوال/الأصناف | `entity.name.function` / `entity.name.type` |

## الترخيص

Apache-2.0 — مثل مشروع ضاد نفسه.

</div>
