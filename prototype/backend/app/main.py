"""STUB do Bước 0 đặt: đủ route theo CONTRACT.md, trả JSON mẫu đúng hình dạng để Agent C dựng giao diện ngay.
Agent A (Nam) thay logic thật từng route (PLAN.md mục 6). Chạy: `uvicorn app.main:app --port 8000` trong prototype/backend.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from . import agent, guard, state

app = FastAPI(title="Trợ lý học bài T2 (stub)")

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
REPLAYS = ("K1", "K2", "K3", "K6")


def _session_or_404(session_id: str | None):
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
            "id": ex["id"], "title": ex["title"], "deadline": ex["deadline"],
            "status": status,
            "mode": "hint_only" if status == "open" else "full_explain",
            "answer_published": ex["answer_published"],
        })
    c = state.COURSE["course"]
    return {
        "course": {"title": c["title"], "current_session": c["current_session"],
                   "outline": c["outline"], "ta_hours": c["ta_hours"]},
        "exercises": exercises,
        "docs": state.COURSE["docs"],
        "flagged_sections": state.STORE["flagged_sections"],
    }


@app.post("/api/chat")
def chat(body: dict = Body(...)):
    s = _session_or_404(body.get("session_id"))
    return agent.run_turn(s, body.get("message", ""))


@app.get("/api/state")
def get_state():
    return state.STORE


@app.post("/api/actions/{action_id}/confirm")
def confirm_action(action_id: str, body: dict | None = Body(default=None)):
    # STUB: A cài logic thật (đưa vào ta_queue kèm ai_summary, bắn event ta_sent).
    return {"ok": True, "ta_queue_item": {
        "id": action_id, "question": "(stub)", "ta_reply_time": "2026-11-14T08:00:00+07:00",
        "after_deadline": True, "ai_summary": "AI đã gợi ý tới nấc 2/3, chưa đưa đáp số"}}


@app.post("/api/actions/{action_id}/cancel")
def cancel_action(action_id: str, body: dict | None = Body(default=None)):
    return {"ok": True}


@app.delete("/api/faq/{faq_id}")
def delete_faq(faq_id: str):
    return {"ok": True}


@app.post("/api/faq/{faq_id}/approve")
def approve_faq(faq_id: str):
    return {"ok": True, "status": "published"}


@app.post("/api/faq/{faq_id}/reject")
def reject_faq(faq_id: str):
    return {"ok": True, "status": "rejected"}


@app.post("/api/tickets/{ticket_id}/close")
def close_ticket(ticket_id: str):
    return {"ok": True}


@app.post("/api/feedback")
def feedback(body: dict = Body(...)):
    return {"ok": True, "ticket_id": "DOC-1"}


@app.get("/api/replay/{name}")
def replay(name: str):
    if name not in REPLAYS:
        raise HTTPException(404, {"error": "replay_not_found"})
    return json.loads((state.REPLAY_DIR / f"{name}.json").read_text(encoding="utf-8"))


@app.post("/api/reset")
def reset():
    state.reset()
    return {"ok": True}


# Mount cuối cùng để không che /api/*. Thư mục frontend/ do Agent C sở hữu.
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
