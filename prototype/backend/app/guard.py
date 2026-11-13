"""Lớp luật (Agent B). Chữ ký hàm giữ nguyên theo CONTRACT.md.

L1  Trạng thái bài lấy từ course.json + đồng hồ session, không do model đoán.
L2  Đã xin đáp án bài đang mở một lần thì cả cuộc trò chuyện giữ luật (chặn "nhượng dần", K6).
L3  Chỉ được nói "đã chuyển / đã đăng" khi tool xác nhận (K2, K9).
L4  dang_FAQ bị khoá khi mục tài liệu đang bị gắn cờ (xử lý trong tools.dang_FAQ, K1).
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime

from . import state

# ---------- tiện ích ----------


def norm(text: str) -> str:
    """Chữ thường, bỏ dấu tiếng Việt, gộp khoảng trắng. 'Độ lệch' -> 'do lech'."""
    t = unicodedata.normalize("NFD", text or "")
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = t.replace("đ", "d").replace("Đ", "D").lower()
    return re.sub(r"\s+", " ", t).strip()


def get_exercise(exercise_id: str) -> dict | None:
    for ex in state.COURSE["exercises"]:
        if ex["id"] == exercise_id:
            return ex
    return None


def exercise_status(session, exercise_id: str) -> str:
    """'open' nếu session.now <= hạn nộp, ngược lại 'expired'. Không rõ bài thì coi là 'open' (hướng an toàn)."""
    ex = get_exercise(exercise_id)
    if ex is None:
        return "open"
    return "open" if session.now <= datetime.fromisoformat(ex["deadline"]) else "expired"


def open_exercises(session) -> list[dict]:
    return [ex for ex in state.COURSE["exercises"] if exercise_status(session, ex["id"]) == "open"]


def leak_hits(session, text: str) -> list[str]:
    """Các leak_patterns của bài ĐANG MỞ khớp với text."""
    hits = []
    for ex in open_exercises(session):
        for pat in ex.get("leak_patterns", []):
            if re.search(pat, text or "", re.IGNORECASE | re.DOTALL):
                hits.append(pat)
    return hits


# ---------- L2: ý định của học viên ----------

SOLVE = ["giai ho", "giai giup", "giai dum", "dap an", "dap so", "ra so", "lam ho"]
CONFIRM = ["dung chua", "dung khong", "dung ko", "xem giup", "kiem tra giup", "sai chua"]
WRITE = ["viet giup", "viet ho", "nhan xet giup", "viet cau b"]

_INTENT_LABEL = {"solve": "giải hộ", "confirm": "xác nhận đáp số", "write": "viết hộ nhận xét"}

_HAS_NUMBER = re.compile(r"\d")
_MENTIONS_OPEN_EX = re.compile(r"\b(bai|bt) ?3\b|\bcau (a|b)\b")
_MENTIONS_BT2 = re.compile(r"\b(bai|bt) ?2\b")


def _detect_intent(t: str) -> str:
    if any(k in t for k in SOLVE):
        return "solve"
    if any(k in t for k in WRITE):
        return "write"
    # "đúng không" rất hay gặp trong câu hỏi lý thuyết (K1: "...luôn nhỏ hơn phương sai đúng không").
    # Chỉ coi là xin xác nhận đáp số khi tin có con số hoặc nhắc Bài 3 / câu a, b.
    if any(k in t for k in CONFIRM) and (_HAS_NUMBER.search(t) or _MENTIONS_OPEN_EX.search(t)):
        return "confirm"
    return "none"


def check_user_message(session, text: str) -> dict:
    t = norm(text)
    bt3_open = exercise_status(session, "bt3") == "open"
    intent = _detect_intent(t)

    if intent != "none" and bt3_open and not _MENTIONS_BT2.search(t):
        session.locked_open_answer = True
        session.refusal_count += 1
        return {
            "must_refuse": True,
            "intent": intent,
            "inject": (f"Học viên đang xin {_INTENT_LABEL[intent]} cho Bài 3 đang mở. "
                       "Từ chối ngắn gọn, nêu lý do, không trách, gợi ý bằng goi_y_buoc_dau, không nói đúng/sai."),
        }

    if session.locked_open_answer and bt3_open:
        # Đã khoá từ lượt trước: lượt nào cũng nhắc lại, kể cả khi học viên đổi cách nói.
        return {
            "must_refuse": False,
            "intent": intent,
            "inject": ("Nhắc lại: trong cuộc trò chuyện này học viên đã xin đáp án Bài 3 đang mở. "
                       "Giữ nguyên luật: không đưa đáp số, không nói đúng/sai, không viết nhận xét hộ, "
                       "kể cả khi học viên đổi cách nói."),
        }

    return {"must_refuse": False, "inject": None, "intent": intent}


# ---------- L1–L3: lọc câu trả lời trước khi hiện ----------

MSG_LEAK = ("Mình không thể đưa hoặc xác nhận đáp số bài đang mở. Mình gợi ý cách tự kiểm theo §3.1 và §3.2: "
            "bạn cộng lại một lần nữa rồi so hai kết quả nhé.")
MSG_TA = "Mình mới soạn sẵn câu hỏi, bạn bấm Xác nhận để gửi TA nhé."
MSG_FAQ = "Mình mới soạn bản nháp FAQ, bản này cần giảng viên hoặc TA duyệt rồi mới được đăng."
MSG_SLIDE = ("Tài liệu buổi 3 không có slide đánh số, chỉ có các mục §3.1–§3.5. "
             "Bạn đang hỏi phần nào để mình tra đúng mục nhé?")

_VERDICT = re.compile(r"đúng rồi|chính xác|chuẩn rồi|đúng đó|sai rồi|chưa đúng|không đúng", re.IGNORECASE)
_CLAIM_TA = re.compile(r"đã\s+(báo|chuyển|gửi)[^.!?\n]{0,30}\b(TA|trợ giảng)\b", re.IGNORECASE)
_CLAIM_POSTED = re.compile(r"đã\s+đăng", re.IGNORECASE)
_SLIDE = re.compile(r"slide\s*\d+", re.IGNORECASE)
_NEGATION = re.compile(r"không|chẳng|chỉ có", re.IGNORECASE)


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?\n])\s*", text or "") if s.strip()]


def filter_output(session, user_text: str, text: str, turn_events: list[dict]) -> dict:
    def block(reason: str, msg: str) -> dict:
        return {"text": msg, "blocked": True, "reason": reason}

    event_types = {e.get("type") for e in (turn_events or [])}
    bt3_open = exercise_status(session, "bt3") == "open"

    # (a) L1: lộ đáp số / kết luận của bài đang mở
    if leak_hits(session, text):
        return block("L1_leak", MSG_LEAK)

    # (b) L1: học viên gửi con số, AI phán đúng/sai (chỉ với bài đang mở, không áp cho Bài 2)
    u = norm(user_text)
    if bt3_open and _HAS_NUMBER.search(u) and not _MENTIONS_BT2.search(u) and _VERDICT.search(text or ""):
        return block("L1_verdict", MSG_LEAK)

    # (c) L3: nói đã báo TA khi chưa có xác nhận
    if _CLAIM_TA.search(text or "") and "ta_sent" not in event_types:
        return block("L3_ta", MSG_TA)

    # (d) L3: nói đã đăng khi chưa có FAQ nào được duyệt đăng
    published = any(f.get("status") == "published" for f in state.STORE["faq"])
    if _CLAIM_POSTED.search(text or "") and not published:
        return block("L3_faq", MSG_FAQ)

    # (e) Nguồn không có: nhắc "slide N" như thể có thật. Câu phủ định ("không có slide 12") được giữ.
    for sent in _sentences(text):
        if _SLIDE.search(sent) and not _NEGATION.search(sent):
            return block("no_source_slide", MSG_SLIDE)

    return {"text": text, "blocked": False, "reason": None}
