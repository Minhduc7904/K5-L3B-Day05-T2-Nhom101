"""STUB do Bước 0 đặt. Agent B (Khoa) thay thân hàm; KHÔNG đổi chữ ký.

Luật: L1 trạng thái bài từ course.json · L2 giữ nguyên suốt hội thoại · L3 chỉ nói "đã làm" khi tool xác nhận · L4 khoá dang_FAQ khi mục bị gắn cờ.
"""
from __future__ import annotations


def check_user_message(session, text: str) -> dict:
    # STUB: không bao giờ chặn. B cài L2 (xem PLAN.md mục 7).
    return {"must_refuse": False, "inject": None, "intent": "none"}


def filter_output(session, user_text: str, text: str, turn_events: list[dict]) -> dict:
    # STUB: cho qua mọi thứ. B cài L1–L3.
    return {"text": text, "blocked": False, "reason": None}


def exercise_status(session, exercise_id: str) -> str:
    # STUB cố định: bt2 hết hạn, còn lại đang mở (hướng an toàn, L1). B thay bằng so session.now với deadline.
    return "expired" if exercise_id == "bt2" else "open"
