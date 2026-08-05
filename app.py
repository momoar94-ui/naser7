"""
app.py — نقطهٔ ورود «دستیار هوشمند بالینی روان‌شناسان»
=====================================================
اجرا:  streamlit run app.py

معماری:
    core/    → منطق مستقل از UI (مدل داده، اتصال LLM، پرامپت‌ها، گزارش)
    ui/      → استایل و اجزای رابط کاربری
    modules/ → ماژول‌های بالینی؛ هر تب یک ماژول مستقل
"""

from __future__ import annotations

import streamlit as st

from core.config import APP_ICON, APP_NAME, APP_SUBTITLE, ensure_dirs
from core.state import init_state
from modules import (case_intake, chat_dsm, formulation, report_view,
                     treatment_plan)
from ui.sidebar import render_sidebar
from ui.styles import app_header, clinical_note, inject_css

# ---------------------------------------------------------------- bootstrap
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()
inject_css()
init_state()

app_header(APP_NAME, APP_SUBTITLE + " • موتور محلی، بدون ارسال داده به اینترنت 🔒")

# نوار کناری → کلاینت و تنظیمات مدل
client, settings = render_sidebar()

# ---------------------------------------------------------------- tabs
tab_case, tab_chat, tab_form, tab_tx, tab_report, tab_help = st.tabs([
    "📋 پروندهٔ بیمار",
    "💬 چت تشخیصی DSM-5",
    "🧩 فرمول‌بندی بالینی",
    "🗺 طرح درمان",
    "📄 گزارش جامع",
    "❓ راهنما",
])

with tab_case:
    case_intake.render()

with tab_chat:
    chat_dsm.render(client, settings)

with tab_form:
    formulation.render(client, settings)

with tab_tx:
    treatment_plan.render(client, settings)

with tab_report:
    report_view.render(client, settings)

with tab_help:
    st.markdown(
        """
### راهنمای استفاده

**گردش کار پیشنهادی**

۱. در تب «پروندهٔ بیمار» داده‌های بالینی را وارد کنید (حداقل: شکایت اصلی، شرح حال، نشانه‌ها).
۲. در تب «چت تشخیصی» فرضیه‌ها را با گفتگوی معیارمحور پالایش کنید و در پایان
دکمهٔ «جمع‌بندی تشخیصی» را بزنید.
۳. در تب «فرمول‌بندی» رویکردهای نظری موردنظر خود را انتخاب و تحلیل را تولید کنید.
۴. در تب «طرح درمان» پروتکل جلسه‌به‌جلسه بسازید.
۵. در تب «گزارش جامع» همه‌چیز را در یک سند واحد مونتاژ و خروجی بگیرید.

**نکات فنی**

- اگر پاسخ‌ها کند است، مدل کوچک‌تری انتخاب کنید یا `num_ctx` را کاهش دهید.
- اگر پاسخ‌ها بیش از حد «خلاقانه» است، دما (Temperature) را روی ۰٫۲ تنظیم کنید.
- برای پرونده‌های طولانی، طول زمینه را روی ۱۶۳۸۴ یا بالاتر بگذارید.

**محدودیت‌ها**

مدل‌های زبانی ممکن است معیار یا منبع را نادرست بازتولید کنند. این ابزار برای
«ساختاردهی به تفکر بالینی» طراحی شده است، نه برای صدور تشخیص. مسئولیت نهایی
تشخیص، درمان و مدیریت خطر همواره بر عهدهٔ درمانگر دارای صلاحیت است.
        """
    )
    clinical_note(
        "استفادهٔ اخلاقی: پیش از ثبت داده، رضایت آگاهانهٔ مراجع را دریافت کنید و "
        "از کد پرونده به‌جای اطلاعات هویتی استفاده نمایید."
    )
