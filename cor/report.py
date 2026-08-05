"""
core.report
-----------
مونتاژ گزارش نهایی و خروجی‌گیری در قالب Markdown و HTML قابل چاپ (RTL).
"""

from __future__ import annotations

import html as html_lib
from datetime import datetime
from typing import Dict

from core.case_model import CaseFile
from core.config import APP_NAME, APP_VERSION

try:  # تبدیل Markdown → HTML (اختیاری اما توصیه‌شده)
    import markdown as _md
except ImportError:  # pragma: no cover
    _md = None


DISCLAIMER = (
    "این سند توسط یک دستیار هوش مصنوعی محلی و صرفاً به‌عنوان ابزار پشتیبان تصمیم‌گیری "
    "بالینی (Clinical Decision Support) تولید شده است. محتوای آن جایگزین قضاوت بالینی، "
    "مصاحبهٔ تشخیصی ساختاریافته و مسئولیت حرفه‌ای درمانگر نیست و پیش از استناد باید با "
    "متن اصلی DSM-5-TR و راهنماهای بالینی معتبر راستی‌آزمایی شود."
)


def build_report_markdown(case: CaseFile, outputs: Dict[str, str], extra_notes: str = "") -> str:
    """مونتاژ گزارش نهایی از خروجی همهٔ ماژول‌ها."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [
        "# گزارش جامع بالینی",
        "",
        f"**کد پرونده:** {case.case_code or '—'}  |  **تاریخ جلسه:** {case.session_date}  "
        f"|  **تاریخ تولید گزارش:** {now}",
        f"**سن:** {case.age or '—'}  |  **جنسیت:** {case.gender}  "
        f"|  **وضعیت تأهل:** {case.marital_status}",
        "",
        "---",
        "",
        "## ۱. دادهٔ خام پرونده",
        "",
        case.to_context(),
        "",
    ]

    section_map = [
        ("۲. جمع‌بندی تشخیصی DSM-5-TR", outputs.get("diagnosis", "")),
        ("۳. فرمول‌بندی بالینی", outputs.get("formulation", "")),
        ("۴. طرح درمان و مداخلات", outputs.get("treatment", "")),
        ("۵. گزارش یکپارچهٔ تدوین‌شده", outputs.get("report", "")),
    ]
    for title, body in section_map:
        if body.strip():
            parts += ["---", "", f"## {title}", "", body.strip(), ""]

    if extra_notes.strip():
        parts += ["---", "", "## یادداشت‌های تکمیلی درمانگر", "", extra_notes.strip(), ""]

    parts += [
        "---",
        "",
        "### سلب مسئولیت",
        DISCLAIMER,
        "",
        f"<small>تولیدشده توسط {APP_NAME} نسخهٔ {APP_VERSION} — پردازش ۱۰۰٪ محلی</small>",
    ]
    return "\n".join(parts)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
  body {{
    font-family: Vazirmatn, Tahoma, "IRANSans", sans-serif;
    line-height: 1.9; color: #1f2937; background: #fff;
    max-width: 900px; margin: 0 auto; padding: 40px 32px;
  }}
  h1 {{ color:#0F766E; border-bottom:3px solid #0F766E; padding-bottom:10px; }}
  h2 {{ color:#115E59; margin-top:32px; border-right:5px solid #14B8A6; padding-right:10px; }}
  h3 {{ color:#334155; }}
  table {{ border-collapse: collapse; width:100%; margin:16px 0; font-size:14px; }}
  th, td {{ border:1px solid #cbd5e1; padding:8px 10px; text-align:right; vertical-align:top; }}
  th {{ background:#F0FDFA; }}
  code, pre {{ background:#f1f5f9; padding:2px 6px; border-radius:4px; direction:ltr; }}
  blockquote {{ border-right:4px solid #14B8A6; margin:0; padding:6px 14px; background:#F0FDFA; }}
  .footer {{ margin-top:40px; font-size:12px; color:#64748b; border-top:1px solid #e2e8f0; padding-top:12px; }}
  @media print {{ body {{ padding:0; }} h2 {{ page-break-after: avoid; }} }}
</style>
</head>
<body>
{content}
<div class="footer">{disclaimer}</div>
</body>
</html>
"""


def markdown_to_html(md_text: str, title: str = "گزارش بالینی") -> str:
    """تبدیل گزارش Markdown به یک صفحهٔ HTML مستقل و قابل چاپ."""
    if _md is not None:
        body = _md.markdown(md_text, extensions=["tables", "fenced_code", "nl2br", "sane_lists"])
    else:  # حالت پشتیبان بدون کتابخانهٔ markdown
        body = f"<pre style='white-space:pre-wrap'>{html_lib.escape(md_text)}</pre>"
    return _HTML_TEMPLATE.format(title=title, content=body, disclaimer=DISCLAIMER)
