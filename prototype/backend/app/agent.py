"""STUB do Bước 0 đặt. Agent A (Nam) thay bằng vòng lặp OpenAI function-calling thật (PLAN.md mục 6)."""
from __future__ import annotations

from . import state


def run_turn(session, user_message: str) -> dict:
    """Trả ChatResponse (xem CONTRACT.md). STUB: câu hỏi lại cố định, không gọi OpenAI."""
    session.history.append({"role": "user", "content": user_message})
    reply = "(stub) Bạn đang hỏi độ lệch chuẩn ở §3.3, hay dữ liệu 'lệch' ở §3.2?"
    session.history.append({"role": "assistant", "content": reply})
    return {
        "message_id": state.next_id("m"),
        "reply": reply,
        "confidence": "no_source",
        "citations": [],
        "notes": [{"type": "info", "text": "Bản stub: chưa gọi AI thật."}],
        "events": [],
        "pending_actions": [],
        "hint_progress": None,
        "trace": [],
    }
