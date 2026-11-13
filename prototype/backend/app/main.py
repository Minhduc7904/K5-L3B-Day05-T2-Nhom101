"""FastAPI server cho Trợ lý học bài T2 (Hoàn chỉnh theo CONTRACT.md).
Agent A (Nam) cài đặt logic server & vòng lặp agent.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Nạp OPENAI_API_KEY / OPENAI_MODEL từ backend/.env (không ghi đè biến môi trường đã có).
# Phải chạy trước khi agent.py đọc os.environ.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from . import agent, guard, state  # noqa: E402

app = FastAPI(title="Trợ lý học bài T2 — AI20K K5")

# Enable CORS for convenience
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
REPLAYS = ("K1", "K2", "K3", "K6")


def _session_or_404(session_id: str | None) -> state.Session:
    s = state.get_session(session_id) if session_id else None
    if s is None:
        raise HTTPException(404, {"error": "session_not_found"})
    return s


@app.post("/api/session")
def create_session(body: dict | None = Body(default=None)):
    s = state.create_session((body or {}).get("now"))
    return {"session_id": s.id, "now": s.now.isoformat()}


@app.get("/api/course")
def get_course(session_id: str | None = None):
    s = _session_or_404(session_id)
    exercises = []
    for ex in state.COURSE["exercises"]:
        status = guard.exercise_status(s, ex["id"])
        exercises.append({
            "id": ex["id"],
            "title": ex["title"],
            "deadline": ex["deadline"],
            "status": status,
            "mode": "hint_only" if status == "open" else "full_explain",
            "answer_published": ex.get("answer_published", False),
        })
    c = state.COURSE["course"]
    return {
        "course": {
            "title": c["title"],
            "current_session": c["current_session"],
            "outline": c["outline"],
            "ta_hours": c["ta_hours"],
        },
        "exercises": exercises,
        "docs": state.COURSE["docs"],
        "flagged_sections": state.STORE["flagged_sections"],
    }


@app.post("/api/chat")
def chat(body: dict = Body(...)):
    session_id = body.get("session_id")
    message = body.get("message", "")
    s = _session_or_404(session_id)
    return agent.run_turn(s, message)


@app.get("/api/state")
def get_state():
    state.STORE["stats"]["bt3_hint_sessions"] = len(state.HINT_SESSIONS)
    return state.STORE


@app.post("/api/actions/{action_id}/confirm")
def confirm_action(action_id: str, body: dict | None = Body(default=None)):
    sess_id = (body or {}).get("session_id")
    s = state.get_session(sess_id) if sess_id else None
    hint_lvl = s.hint_level if s else 0

    # Tìm action trong pending_actions
    action = None
    for a in list(state.STORE["pending_actions"]):
        if a.get("id") == action_id:
            action = a
            state.STORE["pending_actions"].remove(a)
            break

    if action:
        question = action.get("question", "")
        ta_reply = action.get("ta_reply_time", "2026-11-14T08:00:00+07:00")
        after_deadline = action.get("after_deadline", True)
    else:
        question = "(câu hỏi đã chuyển)"
        ta_reply = "2026-11-14T08:00:00+07:00"
        after_deadline = True

    ai_summary = (
        f"AI đã gợi ý tới nấc {hint_lvl}/3, chưa đưa đáp số"
        if hint_lvl > 0
        else "AI chưa đưa gợi ý nào, chưa đưa đáp số"
    )

    item = {
        "id": action_id,
        "question": question,
        "exercise_id": action.get("exercise_id") if action else None,
        "on_duty": action.get("on_duty", False) if action else False,
        "ta_reply_time": ta_reply,
        "after_deadline": after_deadline,
        "ai_summary": ai_summary,
        "confirmed_at": s.now.isoformat() if s else datetime.now().isoformat(),
    }
    state.STORE["ta_queue"].append(item)
    return {"ok": True, "ta_queue_item": item}


@app.post("/api/actions/{action_id}/cancel")
def cancel_action(action_id: str, body: dict | None = Body(default=None)):
    state.STORE["pending_actions"] = [
        a for a in state.STORE["pending_actions"] if a.get("id") != action_id
    ]
    return {"ok": True}


@app.delete("/api/faq/{faq_id}")
def delete_faq(faq_id: str):
    state.STORE["faq"] = [
        f for f in state.STORE["faq"]
        if not (f.get("id") == faq_id and f.get("status") == "draft")
    ]
    return {"ok": True}


@app.post("/api/faq/{faq_id}/approve")
def approve_faq(faq_id: str):
    for f in state.STORE["faq"]:
        if f.get("id") == faq_id:
            f["status"] = "published"
            return {"ok": True, "status": "published"}
    raise HTTPException(404, {"error": "faq_not_found"})


@app.post("/api/faq/{faq_id}/reject")
def reject_faq(faq_id: str):
    for f in state.STORE["faq"]:
        if f.get("id") == faq_id:
            f["status"] = "rejected"
            return {"ok": True, "status": "rejected"}
    raise HTTPException(404, {"error": "faq_not_found"})


@app.post("/api/tickets/{ticket_id}/close")
def close_ticket(ticket_id: str):
    closed_section = None
    for t in state.STORE["tickets"]:
        if t.get("id") == ticket_id:
            t["status"] = "closed"
            closed_section = t.get("section")
            break

    if closed_section:
        still_open = any(
            t.get("section") == closed_section and t.get("status") == "open"
            for t in state.STORE["tickets"]
        )
        if not still_open and closed_section in state.STORE["flagged_sections"]:
            state.STORE["flagged_sections"].remove(closed_section)

    return {"ok": True}


@app.post("/api/feedback")
def feedback(body: dict = Body(...)):
    sess_id = body.get("session_id")
    msg_id = body.get("message_id")
    text = body.get("text", "")
    ticket_id = state.next_id("DOC-")
    ticket = {
        "id": ticket_id,
        "type": "feedback",
        "session_id": sess_id,
        "message_id": msg_id,
        "text": text,
        "status": "open",
    }
    state.STORE["tickets"].append(ticket)
    return {"ok": True, "ticket_id": ticket_id}


@app.get("/api/replay/{name}")
def replay(name: str):
    if name not in REPLAYS:
        raise HTTPException(404, {"error": "replay_not_found"})
    replay_file = state.REPLAY_DIR / f"{name}.json"
    if not replay_file.is_file():
        raise HTTPException(404, {"error": "replay_file_missing"})
    return json.loads(replay_file.read_text(encoding="utf-8"))


@app.post("/api/reset")
def reset():
    state.reset()
    return {"ok": True}


# Mount static frontend directory
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
