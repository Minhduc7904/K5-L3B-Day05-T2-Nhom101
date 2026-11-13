"""Trạng thái dùng chung — ĐÓNG BĂNG ở Bước 0 (chỉ đổi qua Issue `contract-change`).

- Kho toàn cục STORE: TA và GV thấy việc của học viên.
- Session: chỉ lịch sử chat, đồng hồ (`now`, datetime có múi giờ) và `hint_level` gắn với session_id.
- `reset()` xoá hết (POST /api/reset) để demo lại.
"""
from __future__ import annotations

import itertools
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COURSE_PATH = DATA_DIR / "course.json"
REPLAY_DIR = DATA_DIR / "replays"

with COURSE_PATH.open(encoding="utf-8") as _f:
    COURSE: dict = json.load(_f)

DEFAULT_NOW = COURSE["default_now"]  # "2026-11-13T22:40:00+07:00"


@dataclass
class Session:
    id: str
    now: datetime
    history: list = field(default_factory=list)  # message dạng OpenAI {"role","content"}
    refusal_count: int = 0
    locked_open_answer: bool = False  # L2: đã từ chối giải/xác nhận/viết hộ bài đang mở
    hint_level: int = 0  # 0..3, số nấc gợi ý Bài 3 đã đưa


def _empty_store() -> dict:
    return {
        "pending_actions": [],  # chuyen_TA chờ học viên bấm xác nhận
        "ta_queue": [],  # đã xác nhận, TA thấy (có ai_summary)
        "faq": [],  # {id, question, answer, section_refs, status: draft|pending_review|published|rejected}
        "tickets": [],  # {id: "DOC-1", type: "doc_flag"|"feedback", section, claim, counterexample, status: open|closed}
        "flagged_sections": [],  # ["§3.3"]
        "stats": {"bt3_hint_sessions": 0},
    }


STORE: dict = _empty_store()
SESSIONS: dict[str, Session] = {}
HINT_SESSIONS: set[str] = set()  # session_id đã gọi goi_y_buoc_dau (đếm cho stats)
_counters: dict[str, itertools.count] = {}


def parse_now(value: str | None) -> datetime:
    return datetime.fromisoformat(value or DEFAULT_NOW)


def create_session(now: str | None = None) -> Session:
    s = Session(id=uuid.uuid4().hex[:12], now=parse_now(now))
    SESSIONS[s.id] = s
    return s


def get_session(session_id: str) -> Session | None:
    return SESSIONS.get(session_id)


def next_id(prefix: str) -> str:
    """next_id('a') -> 'a1', 'a2'... Dùng cho a (action), f (faq), m (message); ticket dùng 'DOC-<n>'."""
    c = _counters.setdefault(prefix, itertools.count(1))
    return f"{prefix}{next(c)}"


def reset() -> None:
    global STORE
    STORE.clear()
    STORE.update(_empty_store())
    SESSIONS.clear()
    HINT_SESSIONS.clear()
    _counters.clear()
