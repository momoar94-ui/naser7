"""
core.case_model
---------------
مدل دادهٔ «پروندهٔ بالینی». تمام ماژول‌ها روی همین ساختار کار می‌کنند.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, asdict
from datetime import date
from typing import Any, Dict, List

# چک‌لیست نشانه‌های پرکاربرد برای غربال سریع
SYMPTOM_CHECKLIST: List[str] = [
    "خلق افسرده", "بی‌لذتی (آنهدونیا)", "اختلال خواب", "تغییر اشتها/وزن",
    "خستگی و کاهش انرژی", "احساس بی‌ارزشی/گناه", "افت تمرکز", "کندی/تحریک روانی‌حرکتی",
    "افکار خودکشی", "خودآسیبی", "نگرانی مفرط", "حملهٔ پانیک", "اجتناب موقعیتی",
    "ترس از ارزیابی اجتماعی", "وسواس فکری", "اعمال وارسی/شست‌وشو", "فلاش‌بک/کابوس",
    "گوش‌به‌زنگی (Hypervigilance)", "کرختی هیجانی", "تحریک‌پذیری/خشم", "دوره‌های سرخوشی",
    "کاهش نیاز به خواب", "پرحرفی/پرش افکار", "رفتار پرخطر/تکانشی", "توهم", "هذیان",
    "بی‌سازمانی گفتار", "علائم منفی (کاهش عاطفه/اراده)", "بی‌توجهی", "بیش‌فعالی",
    "مشکل تنظیم هیجان", "بی‌ثباتی روابط", "ترس از رهاشدگی", "علائم جسمانی‌سازی",
    "مصرف مواد/الکل", "اختلال تصویر بدنی", "پرخوری/محدودسازی غذا", "گسست/مسخ واقعیت",
]

GENDER_OPTIONS = ["نامشخص", "زن", "مرد", "سایر"]
MARITAL_OPTIONS = ["نامشخص", "مجرد", "متأهل", "مطلقه", "همسر فوت‌شده", "جدا از هم"]
RISK_LEVELS = ["ارزیابی نشده", "بدون خطر مشهود", "خطر پایین", "خطر متوسط", "خطر بالا / بحرانی"]


@dataclass
class CaseFile:
    """ساختار کامل اطلاعات یک مراجع."""

    # --- شناسه و جمعیت‌شناسی (بدون نام واقعی؛ رعایت محرمانگی) ---
    case_code: str = ""
    session_date: str = field(default_factory=lambda: date.today().isoformat())
    age: str = ""
    gender: str = "نامشخص"
    marital_status: str = "نامشخص"
    education: str = ""
    occupation: str = ""
    referral_source: str = ""

    # --- شکایت و شرح حال ---
    chief_complaint: str = ""
    present_illness: str = ""
    onset_course: str = ""
    symptoms: List[str] = field(default_factory=list)
    symptom_details: str = ""
    functional_impact: str = ""

    # --- سوابق ---
    past_psychiatric_history: str = ""
    medical_history: str = ""
    medications: str = ""
    substance_use: str = ""
    family_history: str = ""
    developmental_history: str = ""
    trauma_history: str = ""
    social_support: str = ""
    cultural_context: str = ""

    # --- مشاهدات و سنجش ---
    mse: str = ""
    test_results: str = ""
    risk_level: str = "ارزیابی نشده"
    risk_notes: str = ""
    strengths: str = ""
    therapist_observations: str = ""
    therapy_goals: str = ""

    # ------------------------------------------------------------------ API
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaseFile":
        """ساخت پرونده از دیکشنری، با نادیده‌گرفتن کلیدهای ناشناخته."""
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})

    @property
    def is_empty(self) -> bool:
        """آیا پرونده هنوز محتوای بالینی معناداری ندارد؟"""
        return not any([self.chief_complaint.strip(), self.present_illness.strip(),
                        self.symptoms, self.symptom_details.strip()])

    @property
    def label(self) -> str:
        code = self.case_code.strip() or "بدون‌کد"
        return f"{code} — {self.session_date}"

    def to_context(self) -> str:
        """
        تبدیل پرونده به یک بلوک متنی ساختاریافته برای تزریق در پرامپت مدل.
        فیلدهای خالی حذف می‌شوند تا زمینهٔ مدل شلوغ نشود.
        """
        groups = [
            ("مشخصات پایه", [
                ("کد پرونده", self.case_code), ("تاریخ جلسه", self.session_date),
                ("سن", self.age), ("جنسیت", self.gender),
                ("وضعیت تأهل", self.marital_status), ("تحصیلات", self.education),
                ("شغل", self.occupation), ("منبع ارجاع", self.referral_source),
            ]),
            ("شکایت اصلی و شرح حال", [
                ("شکایت اصلی", self.chief_complaint),
                ("شرح حال بیماری فعلی", self.present_illness),
                ("شروع، سیر و مدت", self.onset_course),
                ("نشانه‌های علامت‌گذاری‌شده", "، ".join(self.symptoms)),
                ("توضیح تکمیلی نشانه‌ها", self.symptom_details),
                ("تخریب عملکرد", self.functional_impact),
            ]),
            ("سوابق", [
                ("سابقهٔ روان‌پزشکی/درمانی", self.past_psychiatric_history),
                ("سابقهٔ پزشکی و نورولوژیک", self.medical_history),
                ("داروهای فعلی", self.medications),
                ("مصرف مواد/الکل", self.substance_use),
                ("سابقهٔ خانوادگی", self.family_history),
                ("تاریخچهٔ رشدی و دلبستگی", self.developmental_history),
                ("تاریخچهٔ تروما و رویدادهای تنش‌زا", self.trauma_history),
                ("حمایت اجتماعی و روابط", self.social_support),
                ("زمینهٔ فرهنگی/مذهبی/اقتصادی", self.cultural_context),
            ]),
            ("مشاهدات بالینی و سنجش", [
                ("وضعیت روانی (MSE)", self.mse),
                ("نتایج آزمون‌ها/پرسشنامه‌ها", self.test_results),
                ("سطح خطر", self.risk_level),
                ("یادداشت خطر (خودکشی/دگرآزاری)", self.risk_notes),
                ("نقاط قوت و منابع مراجع", self.strengths),
                ("مشاهدات درمانگر", self.therapist_observations),
                ("اهداف اعلام‌شدهٔ مراجع", self.therapy_goals),
            ]),
        ]

        lines: List[str] = ["=== پروندهٔ بالینی مراجع ==="]
        for title, items in groups:
            rows = [f"- {k}: {str(v).strip()}" for k, v in items if str(v).strip()]
            if rows:
                lines.append(f"\n## {title}")
                lines.extend(rows)
        lines.append("\n=== پایان پرونده ===")
        return "\n".join(lines)
