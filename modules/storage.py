"""
core.storage
------------
ذخیره‌سازی محلی پرونده‌ها به‌صورت JSON. هیچ داده‌ای به بیرون ارسال نمی‌شود.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from core.case_model import CaseFile
from core.config import CASES_DIR, ensure_dirs


def _safe_name(text: str) -> str:
    """تبدیل نام پرونده به یک نام فایل امن."""
    cleaned = re.sub(r"[^\w\u0600-\u06FF\- ]+", "", text).strip().replace(" ", "_")
    return cleaned or "case"


def save_case(case: CaseFile, chat: List[Dict[str, str]], outputs: Dict[str, str]) -> Path:
    """ذخیرهٔ کامل نشست (پرونده + چت + خروجی‌های تولیدشده)."""
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = CASES_DIR / f"{_safe_name(case.case_code or 'case')}_{stamp}.json"
    payload: Dict[str, Any] = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "case": case.to_dict(),
        "chat": chat,
        "outputs": outputs,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def list_cases() -> List[str]:
    """فهرست پرونده‌های ذخیره‌شده (جدیدترین ابتدا)."""
    ensure_dirs()
    files = sorted(CASES_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [p.name for p in files]


def load_case(filename: str) -> Dict[str, Any]:
    """بازیابی یک پروندهٔ ذخیره‌شده."""
    path = CASES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"پروندهٔ «{filename}» یافت نشد.")
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "case": CaseFile.from_dict(data.get("case", {})),
        "chat": data.get("chat", []),
        "outputs": data.get("outputs", {}),
    }


def delete_case(filename: str) -> None:
    """حذف پروندهٔ ذخیره‌شده."""
    path = CASES_DIR / filename
    if path.exists():
        path.unlink()
