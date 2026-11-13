"""Tool của trợ lý (Agent B). Chữ ký, tên tool và TOOL_SCHEMAS giữ nguyên theo CONTRACT.md.

run_tool trả: {"ok", "blocked", "reason", "data", "events", "citations"}
"""
from __future__ import annotations

import re
from datetime import datetime, time, timedelta

from . import guard, state


def _fn(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


_S = {"type": "string"}

TOOL_SCHEMAS: list[dict] = [
    _fn("tra_cuu_tai_lieu",
        "Tìm trong tài liệu buổi 1–3 của khoá, trả đoạn kèm mã mục (§3.x). Chỉ đọc.",
        {"query": {**_S, "description": "Từ khoá hoặc câu hỏi cần tra"}}, ["query"]),
    _fn("goi_y_buoc_dau",
        "Gợi ý làm bài tập ĐANG MỞ theo từng nấc (1 công thức, 2 tự kiểm, 3 câu hỏi gợi mở). Không có nấc đáp số.",
        {"exercise_id": {**_S, "description": "Ví dụ bt3"}}, ["exercise_id"]),
    _fn("giai_thich_bai_het_han",
        "Giải thích đầy đủ bài tập ĐÃ HẾT HẠN và đã có đáp án công bố (ví dụ bt2).",
        {"exercise_id": {**_S, "description": "Ví dụ bt2"}}, ["exercise_id"]),
    _fn("chuyen_TA",
        "Soạn câu hỏi chuyển cho TA. Chỉ soạn chờ học viên bấm xác nhận, chưa gửi. Trả giờ TA trả lời thật và cờ sau hạn.",
        {"question": _S, "exercise_id": {**_S, "description": "Tuỳ chọn, ví dụ bt3"}}, ["question"]),
    _fn("soan_FAQ",
        "Soạn BẢN NHÁP FAQ ẩn danh (bỏ tên, bỏ lời tự chê, không chứa gợi ý bài đang mở). Không đăng.",
        {"question": _S, "answer": _S,
         "section_refs": {"type": "array", "items": _S, "description": "Mã mục được trích, ví dụ [\"§3.2\"]"}},
        ["question", "answer", "section_refs"]),
    _fn("dang_FAQ",
        "Đưa bản nháp FAQ vào hàng chờ giảng viên/TA duyệt. Không bao giờ tự đăng. Bị khoá nếu mục tài liệu đang bị gắn cờ.",
        {"faq_id": _S}, ["faq_id"]),
    _fn("bao_loi_tai_lieu",
        "Tạo ticket ẩn danh cho giảng viên khi nghi một câu trong tài liệu sai; gắn cờ mục đó.",
        {"section": {**_S, "description": "Ví dụ §3.3"}, "claim": {**_S, "description": "Câu nghi sai"},
         "counterexample": {**_S, "description": "Phản ví dụ"}},
        ["section", "claim", "counterexample"]),
]


# ---------- tiện ích ----------


def _res(ok=True, blocked=False, reason=None, data=None, events=None, citations=None) -> dict:
    return {"ok": ok, "blocked": blocked, "reason": reason, "data": data or {},
            "events": events or [], "citations": citations or []}


def _blocked(reason: str, text: str, data: dict | None = None) -> dict:
    return _res(ok=False, blocked=True, reason=reason, data={"message": text, **(data or {})},
                events=[{"type": "blocked", "text": text, "data": {"reason": reason}}])


def _event(type_: str, text: str, data: dict | None = None) -> dict:
    return {"type": type_, "text": text, "data": data or {}}


_DOCS = {d["section"]: d for d in state.COURSE["docs"]}


def _citation(section: str) -> dict | None:
    d = _DOCS.get(section)
    return {"section": d["section"], "title": d["title"], "quote": d["text"]} if d else None


def _citations_in(text: str) -> list[dict]:
    """Citation cho các mã mục (§3.x) xuất hiện trong một đoạn chữ CÓ SẴN trong course.json."""
    out, seen = [], set()
    for sec in re.findall(r"§\d+\.\d+", text or ""):
        c = _citation(sec)
        if c and sec not in seen:
            seen.add(sec)
            out.append(c)
    return out


# ---------- tra_cuu_tai_lieu (tự làm, chỉ đọc) ----------

# Từ khoá đã bỏ dấu -> mục. Thứ tự trong danh sách = thứ tự trả về.
_DOC_KEYWORDS = [
    ("§3.3", ["do lech chuan", "phuong sai", "do lech"]),
    ("§3.2", ["trung vi", "du lieu lech"]),
    ("§3.1", ["trung binh"]),
    ("§3.4", ["ngoai lai"]),
    ("§3.5", ["bai tap 3", "bai 3", "bt3"]),
]
# Chủ đề của buổi chưa mở (outline), để AI nói "buổi X sẽ học" thay vì giảng.
_OUTLINE_KEYWORDS = [
    (4, ["truc quan", "bieu do"]),
    (5, ["xac suat"]),
    (6, ["phan phoi chuan"]),
    (7, ["p-value", "p value", "pvalue", "kiem dinh"]),
    (8, ["hoi quy"]),
    (9, ["lam sach"]),
    (10, ["du an cuoi"]),
]


def tra_cuu_tai_lieu(session, query: str) -> dict:
    q = guard.norm(query)
    data: dict = {"query": query, "matches": []}

    if "slide" in q:
        # Tài liệu buổi 3 không có slide đánh số: không trả gì để model không ghép nội dung vào "slide 12".
        data["note"] = "Tài liệu buổi 3 không có slide đánh số, chỉ có các mục §3.1–§3.5."
        return _res(data=data, events=[_event("tool_call", "Tra tài liệu: không có slide đánh số")])

    for num, kws in _OUTLINE_KEYWORDS:
        if any(k in q for k in kws):
            o = next(x for x in state.COURSE["course"]["outline"] if x["session"] == num)
            data["outline_hint"] = {"session": o["session"], "title": o["title"]}
            data["note"] = f"Chủ đề thuộc buổi {o['session']} ({o['title']}), chưa mở, chưa có tài liệu."
            return _res(data=data, events=[_event("tool_call", f"Tra tài liệu: thuộc buổi {num}, chưa học")])

    sections = [sec for sec, kws in _DOC_KEYWORDS if any(k in q for k in kws)]
    data["matches"] = [{"section": s, "title": _DOCS[s]["title"], "text": _DOCS[s]["text"]} for s in sections]
    if not sections:
        data["note"] = "Tài liệu buổi 3 không có mục này."
    flagged = [s for s in sections if s in state.STORE["flagged_sections"]]
    if flagged:
        data["flagged"] = flagged
    label = ", ".join(sections) if sections else "không có kết quả"
    return _res(data=data, citations=[_citation(s) for s in sections],
                events=[_event("tool_call", f"Tra tài liệu: {label}")])


# ---------- goi_y_buoc_dau (tự làm, có trần: không có nấc đáp số) ----------

def goi_y_buoc_dau(session, exercise_id: str) -> dict:
    ex = guard.get_exercise(exercise_id)
    if ex is None:
        return _blocked("unknown_exercise", f"Không có bài tập {exercise_id}.")
    if guard.exercise_status(session, exercise_id) != "open":
        return _blocked("L1", f"{ex['title']} đã hết hạn, dùng giai_thich_bai_het_han để giải thích đầy đủ.")
    hints = ex.get("hints") or []
    if not hints:
        return _blocked("no_hints", f"{ex['title']} chưa có gợi ý.")

    max_level = len(hints)
    exhausted = session.hint_level >= max_level
    session.hint_level = min(session.hint_level + 1, max_level)
    hint = hints[session.hint_level - 1]

    state.HINT_SESSIONS.add(session.id)
    state.STORE["stats"]["bt3_hint_sessions"] = len(state.HINT_SESSIONS)

    data = {"exercise_id": exercise_id, "level": hint["level"], "max": max_level,
            "kind": hint["kind"], "text": hint["text"]}
    if exhausted:
        data["exhausted"] = True
        data["note"] = "Đã hết nấc gợi ý, không có nấc đáp số. Bạn có thể gửi câu hỏi cho TA."
    return _res(data=data, citations=_citations_in(hint["text"]),
                events=[_event("tool_call", f"Gợi ý nấc {hint['level']}/{max_level}",
                               {"level": hint["level"], "max": max_level})])


# ---------- giai_thich_bai_het_han (tự làm, chỉ bài hết hạn và đã có đáp án) ----------

def giai_thich_bai_het_han(session, exercise_id: str) -> dict:
    ex = guard.get_exercise(exercise_id)
    if ex is None:
        return _blocked("unknown_exercise", f"Không có bài tập {exercise_id}.")
    if guard.exercise_status(session, exercise_id) == "open":
        return _blocked("L1", f"{ex['title']} đang mở, chỉ được gợi ý từng bước bằng goi_y_buoc_dau.")
    if not ex.get("answer_published"):
        return _blocked("answer_not_published", f"{ex['title']} đã hết hạn nhưng giảng viên chưa công bố đáp án.")
    data = {"exercise_id": exercise_id, "solution": ex["solution"],
            "published_answer": ex.get("published_answer")}
    return _res(data=data, citations=_citations_in(ex["solution"]),
                events=[_event("tool_call", f"Giải thích {ex['title']} (đã hết hạn, có đáp án)")])


# ---------- chuyen_TA (cần học viên bấm xác nhận) ----------

def _ta_reply_time(now: datetime) -> tuple[datetime, bool]:
    hours = state.COURSE["course"]["ta_hours"]
    start = time.fromisoformat(hours["start"])
    end = time.fromisoformat(hours["end"])
    t = now.timetz().replace(tzinfo=None)
    if start <= t < end:
        return now, True
    day = now.date() if t < start else now.date() + timedelta(days=1)
    return datetime.combine(day, start, tzinfo=now.tzinfo), False


def chuyen_TA(session, question: str, exercise_id: str | None = None) -> dict:
    reply_at, on_duty = _ta_reply_time(session.now)

    # Bài liên quan: bài được chỉ định, nếu không thì các bài đang mở.
    if exercise_id and guard.get_exercise(exercise_id):
        related = [guard.get_exercise(exercise_id)]
    else:
        related = guard.open_exercises(session)
    late = [ex for ex in related
            if guard.exercise_status(session, ex["id"]) == "open"
            and reply_at > datetime.fromisoformat(ex["deadline"])]

    action = {
        "id": state.next_id("a"),
        "type": "chuyen_TA",
        "session_id": session.id,
        "question": question,
        "exercise_id": exercise_id or (late[0]["id"] if late else None),
        "summary": question if len(question) <= 120 else question[:117] + "...",
        "ta_reply_time": reply_at.isoformat(),
        "on_duty": on_duty,
        "after_deadline": bool(late),
        "status": "pending",
    }
    state.STORE["pending_actions"].append(action)

    when = "TA đang trực" if on_duty else f"TA trả lời từ {reply_at.strftime('%H:%M %d/%m')}"
    if late:
        when += f", sau hạn nộp {late[0]['title']}"
    return _res(data={"pending_action": action, "message": f"Đã soạn câu hỏi, chờ học viên bấm xác nhận. {when}."},
                events=[_event("ta_pending_confirm", f"Câu hỏi cho TA đang chờ bạn xác nhận ({when})",
                               {"action_id": action["id"]})])


# ---------- soan_FAQ (tự làm: chỉ nháp riêng tư, ẩn danh) ----------

_SELF_PUT_DOWN = re.compile(r"\b(ngu|dốt|kém|tệ|đần|ngốc|chậm hiểu|bỏ tay|không hợp)\b", re.IGNORECASE)
_NAME = re.compile(r"\b(em|mình|tôi|tớ)\s+tên\s+là\s+[^\s,.!?]+(\s+[A-ZÀ-Ỹ][^\s,.!?]*)*|@\w+", re.IGNORECASE)


def _anonymize(text: str) -> str:
    text = _NAME.sub("", text or "")
    parts = re.split(r"(?<=[.!?,;…])\s+|\n+", text)
    kept = [p for p in parts if p.strip() and not _SELF_PUT_DOWN.search(p)]
    out = " ".join(kept).strip(" ,;")
    return re.sub(r"\s{2,}", " ", out)


def soan_FAQ(session, question: str, answer: str, section_refs: list | None = None) -> dict:
    refs = [r for r in (section_refs or []) if isinstance(r, str)]
    clean_q = _anonymize(question)
    clean_a = _anonymize(answer)
    if guard.leak_hits(session, f"{clean_q}\n{clean_a}"):
        return _blocked("L1_leak", "Bản nháp có chứa đáp số hoặc gợi ý quá tay của bài đang mở nên không soạn.")
    if not clean_q:
        return _blocked("empty_question", "Câu hỏi chỉ còn lời tự chê sau khi ẩn danh, không có gì để đưa vào FAQ.")

    faq = {
        "id": state.next_id("f"),
        "question": clean_q,
        "answer": clean_a,
        "section_refs": refs,
        "status": "draft",
        "flagged": [r for r in refs if r in state.STORE["flagged_sections"]],
        "no_open_hint": True,  # đã qua kiểm leak_patterns
        "created_at": session.now.isoformat(),
    }
    state.STORE["faq"].append(faq)
    return _res(data={"faq": faq}, citations=[c for c in (_citation(r) for r in refs) if c],
                events=[_event("faq_draft_created", "Đã soạn bản nháp FAQ ẩn danh (chưa đăng)", {"faq_id": faq["id"]})])


# ---------- dang_FAQ (cần giảng viên/TA duyệt; L4 khoá khi mục bị gắn cờ) ----------

def dang_FAQ(session, faq_id: str) -> dict:
    faq = next((f for f in state.STORE["faq"] if f["id"] == faq_id), None)
    if faq is None:
        return _blocked("faq_not_found", f"Không có bản nháp {faq_id}.")
    if faq["status"] == "pending_review":
        return _res(data={"faq": faq, "message": "Bản nháp đã nằm trong hàng chờ duyệt."},
                    events=[_event("faq_pending_review", "FAQ đang chờ giảng viên/TA duyệt", {"faq_id": faq_id})])
    if faq["status"] != "draft":
        return _blocked("not_draft", f"FAQ {faq_id} đang ở trạng thái {faq['status']}, không gửi duyệt được.")

    locked = [r for r in faq["section_refs"] if r in state.STORE["flagged_sections"]]
    if locked:
        res = _blocked("L4", f"Mục {', '.join(locked)} đang bị gắn cờ chờ giảng viên xem lại, chưa được đưa lên FAQ.",
                       {"locked_sections": locked})
        res["events"].append(_event("faq_locked", f"FAQ bị khoá vì {', '.join(locked)} đang bị gắn cờ",
                                    {"faq_id": faq_id, "sections": locked}))
        return res

    faq["status"] = "pending_review"  # Không bao giờ tự 'published': chỉ /approve mới đăng.
    return _res(data={"faq": faq},
                events=[_event("faq_pending_review", "Đã gửi FAQ cho giảng viên/TA duyệt (chưa đăng)", {"faq_id": faq_id})])


# ---------- bao_loi_tai_lieu (tự làm: ticket ẩn danh + gắn cờ) ----------

def bao_loi_tai_lieu(session, section: str, claim: str, counterexample: str) -> dict:
    sec = section.strip()
    if not sec.startswith("§"):
        sec = "§" + sec
    if sec not in _DOCS:
        return _blocked("unknown_section", f"Tài liệu không có mục {section}.")

    existing = next((t for t in state.STORE["tickets"]
                     if t.get("type") == "doc_flag" and t["section"] == sec and t["status"] == "open"), None)
    if existing:
        return _res(data={"ticket": existing, "duplicate": True}, citations=[_citation(sec)],
                    events=[_event("flag_created", f"Mục {sec} đã được gắn cờ ({existing['id']})",
                                   {"ticket_id": existing["id"], "section": sec})])

    ticket = {
        "id": state.next_id("DOC-"),
        "type": "doc_flag",
        "section": sec,
        "claim": claim,
        "counterexample": counterexample,
        "status": "open",
        "created_at": session.now.isoformat(),  # ẩn danh: không lưu session_id hay tên học viên
    }
    state.STORE["tickets"].append(ticket)
    if sec not in state.STORE["flagged_sections"]:
        state.STORE["flagged_sections"].append(sec)
    return _res(data={"ticket": ticket}, citations=[_citation(sec)],
                events=[_event("flag_created", f"Đã gắn cờ {sec} và gửi giảng viên ({ticket['id']})",
                               {"ticket_id": ticket["id"], "section": sec})])


# ---------- điểm vào duy nhất ----------

_TOOLS = {
    "tra_cuu_tai_lieu": tra_cuu_tai_lieu,
    "goi_y_buoc_dau": goi_y_buoc_dau,
    "giai_thich_bai_het_han": giai_thich_bai_het_han,
    "chuyen_TA": chuyen_TA,
    "soan_FAQ": soan_FAQ,
    "dang_FAQ": dang_FAQ,
    "bao_loi_tai_lieu": bao_loi_tai_lieu,
}


def run_tool(name: str, args: dict, session) -> dict:
    fn = _TOOLS.get(name)
    if fn is None:
        # Ví dụ model tự bịa tool "giai_ho": không có tool nào làm việc bị cấm.
        return _blocked("unknown_tool", f"Không có tool {name}.")
    try:
        return fn(session, **(args or {}))
    except TypeError as e:
        return _res(ok=False, reason="bad_args", data={"message": f"Sai tham số cho {name}: {e}"})
