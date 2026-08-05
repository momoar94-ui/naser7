"""
core.config
-----------
تنظیمات سراسری برنامه، مسیرها و دیتاکلاس پارامترهای مدل زبانی.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict

# ---------------------------------------------------------------- meta
APP_NAME: str = "دستیار هوشمند بالینی"
APP_SUBTITLE: str = "Clinical Co-Pilot for Psychologists & Psychotherapists"
APP_VERSION: str = "1.0.0"
APP_ICON: str = "🧠"

# ---------------------------------------------------------------- paths
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
CASES_DIR: Path = DATA_DIR / "cases"
EXPORTS_DIR: Path = DATA_DIR / "exports"

# ---------------------------------------------------------------- llm
# آدرس سرویس محلی Ollama (قابل تغییر با متغیر محیطی OLLAMA_HOST)
DEFAULT_HOST: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

# مدل پیش‌فرض؛ اگر نصب نباشد، اولین مدل موجود انتخاب می‌شود.
DEFAULT_MODEL: str = os.getenv("PSY_MODEL", "qwen2.5:14b-instruct")

# مدل‌های پیشنهادی برای این کاربرد (کیفیت فارسی + استدلال بالینی)
SUGGESTED_MODELS: Dict[str, str] = {
    "qwen2.5:14b-instruct": "بهترین توازن فارسی/استدلال (~9GB VRAM یا 16GB RAM)",
    "qwen2.5:32b-instruct": "کیفیت بالاتر، نیازمند ~20GB VRAM",
    "gemma3:12b": "فارسی روان، چندزبانه (~8GB)",
    "aya-expanse:8b": "تخصصی چندزبانه، سبک (~5GB)",
    "llama3.1:8b": "سبک و سریع، فارسی متوسط (~5GB)",
    "mistral-nemo:12b": "پنجرهٔ زمینهٔ بزرگ (~7GB)",
}

# پنجره‌های زمینهٔ قابل انتخاب
CONTEXT_WINDOWS = [4096, 8192, 16384, 32768]


@dataclass
class LLMSettings:
    """پارامترهای قابل تنظیم موتور استنتاج محلی."""

    host: str = DEFAULT_HOST
    model: str = DEFAULT_MODEL
    temperature: float = 0.30          # دقت بالینی ← خلاقیت پایین
    top_p: float = 0.90
    repeat_penalty: float = 1.08
    num_ctx: int = 8192                # طول زمینه
    num_predict: int = 2048            # حداکثر توکن خروجی
    timeout: int = 900                 # ثانیه (مدل‌های بزرگ کند هستند)
    keep_alive: str = "30m"            # مدل در RAM بماند تا پاسخ‌ها سریع شود

    def as_options(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری options مورد انتظار Ollama."""
        return {
            "temperature": float(self.temperature),
            "top_p": float(self.top_p),
            "repeat_penalty": float(self.repeat_penalty),
            "num_ctx": int(self.num_ctx),
            "num_predict": int(self.num_predict),
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


import requests

# کلید API خود را اینجا قرار دهید
API_KEY = "your_API_KEY_HERE"

def get_ai_response(user_message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen/qwen-2.5-72b-instruct:free", # مدل رایگان Qwen
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        # دریافت متن پاسخ
        if "choices" in response_data:
            return response_data["choices"][0]["message"]["content"]
        else:
            return f"خطا از سمت سرور: {response_data}"
            
    except Exception as e:
        return f"خطا در ارتباط: {str(e)}"

