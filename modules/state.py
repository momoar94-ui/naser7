"""
core.state
----------
مدیریت متمرکز session_state استریم‌لیت: پرونده، تاریخچهٔ چت و خروجی ماژول‌ها.
"""

from __future__ import annotations

from dataclasses import fields
from typing import Any, Dict, List

import streamlit as st

from core.case_model import CaseFile
from core.config import LLMSettings

FIELD_PREFIX = "f_"          # پیشوند کلید ویجت‌های فرم پرونده
OUTPUT_KEYS = ("diagnosis", "formulation", "treatment", "report")


def init_state() -> None:
    """مقداردهی اولیهٔ وضعیت برنامه (فقط یک‌بار در هر نشست)."""
    ss = st.session_state
    ss.setdefault("llm", LLMSettings())
    ss.setdefault("case", CaseFile())
    ss.setdefault("chat_messages", [])                    # [{'role','content'}]
    ss.setdefault("outputs", {k: "" for k in OUTPUT_KEYS})
    ss.setdefault("loaded_case_name", "")


def collect_case() -> CaseFile:
    """
    خواندن مقادیر ویجت‌های فرم از session_state و ساخت شیء CaseFile.
    چون تب‌های Streamlit همگی در هر اجرا رندر می‌شوند، مقادیر پایدار می‌مانند.
    """
    data: Dict[str, Any] = {}
    for f in fields(CaseFile):
        key = FIELD_PREFIX + f.name
        if key in st.session_state:
            data[f.name] = st.session_state[key]
    case = CaseFile(**data)
    st.session_state.case = case
    return case


def push_case_to_widgets(case: CaseFile) -> None:
    """نوشتن مقادیر یک پروندهٔ بارگذاری‌شده در کلیدهای ویجت‌ها."""
    for f in fields(CaseFile):
        st.session_state[FIELD_PREFIX + f.name] = getattr(case, f.name)
    st.session_state.case = case


def reset_all() -> None:
    """شروع پروندهٔ جدید: پاک‌سازی فرم، چت و خروجی‌ها."""
    for f in fields(CaseFile):
        st.session_state.pop(FIELD_PREFIX + f.name, None)
    st.session_state.case = CaseFile()
    st.session_state.chat_messages = []
    st.session_state.outputs = {k: "" for k in OUTPUT_KEYS}
    st.session_state.loaded_case_name = ""


def has_output(key: str) -> bool:
    return bool(st.session_state.outputs.get(key, "").strip())


def set_output(key: str, value: str) -> None:
    st.session_state.outputs[key] = value


def get_output(key: str) -> str:
    return st.session_state.outputs.get(key, "")


def chat_history() -> List[Dict[str, str]]:
    return st.session_state.chat_messages
