"""
core.llm_client
---------------
لایهٔ ارتباط با موتور هوش مصنوعی محلی (Ollama).

* هیچ API Key و هیچ ارتباط اینترنتی لازم نیست.
* از REST API رسمی Ollama استفاده می‌کند: /api/tags و /api/chat
* استریم توکن‌به‌توکن برای تجربهٔ کاربری روان.
"""

from __future__ import annotations

import json
from typing import Dict, Generator, List, Optional, Tuple

import requests

from core.config import LLMSettings

Message = Dict[str, str]  # {"role": "system"|"user"|"assistant", "content": "..."}


class OllamaError(RuntimeError):
    """خطای اختصاصی لایهٔ مدل، برای نمایش پیام فارسی به کاربر."""


# --------------------------------------------------------------------- utils
def _hold_partial_tag(text: str, tag: str) -> Tuple[str, str]:
    """
    جداسازی بخشی از متن که ممکن است ابتدای یک تگ ناقص باشد.
    خروجی: (بخش امن برای نمایش، بخش نگه‌داشته‌شده)
    """
    for i in range(len(tag) - 1, 0, -1):
        if text.endswith(tag[:i]):
            return text[:-i], text[-i:]
    return text, ""


def strip_thinking(stream: Generator[str, None, None]) -> Generator[str, None, None]:
    """
    حذف بلوک‌های <think>...</think> مدل‌های استدلالی به‌صورت زنده،
    تا زنجیرهٔ فکر داخلی مدل در گزارش بالینی ظاهر نشود.
    """
    open_tag, close_tag = "<think>", "</think>"
    buffer, inside = "", False

    for chunk in stream:
        buffer += chunk
        while True:
            if not inside:
                idx = buffer.find(open_tag)
                if idx == -1:
                    safe, buffer = _hold_partial_tag(buffer, open_tag)
                    if safe:
                        yield safe
                    break
                if idx > 0:
                    yield buffer[:idx]
                buffer = buffer[idx + len(open_tag):]
                inside = True
            else:
                idx = buffer.find(close_tag)
                if idx == -1:
                    _, buffer = _hold_partial_tag(buffer, close_tag)
                    break
                buffer = buffer[idx + len(close_tag):]
                inside = False

    if buffer and not inside:
        yield buffer


# -------------------------------------------------------------------- client
class OllamaClient:
    """کلاینت سبک و مقاوم برای سرویس محلی Ollama."""

    def __init__(self, host: str, timeout: int = 900) -> None:
        self.host: str = host.rstrip("/")
        self.timeout: int = timeout
        self._session: requests.Session = requests.Session()

    # ---------------------------------------------------------- diagnostics
    def ping(self) -> bool:
        """آیا سرویس Ollama بالا است؟"""
        try:
            resp = self._session.get(f"{self.host}/api/tags", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> List[str]:
        """فهرست مدل‌های نصب‌شده روی سیستم کاربر."""
        try:
            resp = self._session.get(f"{self.host}/api/tags", timeout=10)
            resp.raise_for_status()
            payload = resp.json()
        except requests.RequestException as exc:
            raise OllamaError(
                "اتصال به سرویس Ollama برقرار نشد. مطمئن شوید Ollama نصب و "
                f"در حال اجراست (دستور: `ollama serve`). آدرس: {self.host}"
            ) from exc
        except ValueError as exc:
            raise OllamaError("پاسخ نامعتبر از سرویس Ollama دریافت شد.") from exc

        return sorted(m.get("name", "") for m in payload.get("models", []) if m.get("name"))

    # ---------------------------------------------------------------- chat
    def chat_stream(
        self,
        messages: List[Message],
        settings: LLMSettings,
        model: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """
        ارسال گفتگو به مدل و بازگرداندن پاسخ به‌صورت جریانی (generator of str).
        """
        payload = {
            "model": model or settings.model,
            "messages": messages,
            "stream": True,
            "options": settings.as_options(),
            "keep_alive": settings.keep_alive,
        }

        try:
            with self._session.post(
                f"{self.host}/api/chat",
                json=payload,
                stream=True,
                timeout=(10, settings.timeout),
            ) as resp:
                if resp.status_code == 404:
                    raise OllamaError(
                        f"مدل «{payload['model']}» روی سیستم یافت نشد. "
                        f"ابتدا آن را دانلود کنید:  ollama pull {payload['model']}"
                    )
                resp.raise_for_status()

                for raw_line in resp.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    try:
                        data = json.loads(raw_line)
                    except json.JSONDecodeError:
                        continue

                    if "error" in data:
                        raise OllamaError(f"خطای موتور مدل: {data['error']}")

                    piece = (data.get("message") or {}).get("content", "")
                    if piece:
                        yield piece
                    if data.get("done"):
                        break

        except requests.exceptions.ReadTimeout as exc:
            raise OllamaError(
                "زمان پاسخ‌گویی مدل به پایان رسید. مدل کوچک‌تری انتخاب کنید "
                "یا مقدار Timeout را در نوار کناری افزایش دهید."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise OllamaError(
                "ارتباط با Ollama قطع است. سرویس را با دستور `ollama serve` اجرا کنید."
            ) from exc
        except requests.RequestException as exc:
            raise OllamaError(f"خطای شبکهٔ داخلی: {exc}") from exc

    def chat(
        self,
        messages: List[Message],
        settings: LLMSettings,
        model: Optional[str] = None,
    ) -> str:
        """نسخهٔ غیرجریانی؛ پاسخ کامل را به‌صورت یک رشته برمی‌گرداند."""
        return "".join(strip_thinking(self.chat_stream(messages, settings, model)))
