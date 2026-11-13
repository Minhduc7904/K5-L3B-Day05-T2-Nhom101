"""Vòng lặp AI Agent với OpenAI function-calling (Agent A — Nam).
Tuân thủ CONTRACT.md và PLAN.md mục 6.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from fastapi import HTTPException
from openai import OpenAI

from . import guard, prompts, state, tools


def run_turn(session: state.Session, user_message: str) -> dict:
    """Xử lý một lượt chat giữa học viên và AI:
    1. Kiểm tra guard input (L2).
    2. Gọi OpenAI chat completion kèm tools (tối đa 5 vòng lặp).
    3. Lọc output qua guard filter (L1-L3).
    4. Tính toán độ chắc (confidence) do server quyết định.
    5. Cập nhật lịch sử và trả về ChatResponse chuẩn.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    model_name = os.environ.get("OPENAI_MODEL") or "gpt-5.4"

    if not api_key:
        raise HTTPException(status_code=503, detail={"error": "llm_unavailable", "reason": "OPENAI_API_KEY_missing"})

    # 1. Guard check input
    g = guard.check_user_message(session, user_message)
    inject = g.get("inject")

    # Lưu tin nhắn người dùng vào lịch sử
    session.history.append({"role": "user", "content": user_message})

    # Xây dựng messages cho OpenAI
    msgs = prompts.build_messages(session, inject)

    turn_events: list[dict] = []
    turn_citations: list[dict] = []
    turn_pending_actions: list[dict] = []
    turn_trace: list[dict] = []
    notes: list[dict] = []
    reply = ""
    hint_called = False

    try:
        client = OpenAI(api_key=api_key)

        # 2. Vòng lặp tool calls tối đa 5 lần
        for loop_idx in range(5):
            response = client.chat.completions.create(
                model=model_name,
                messages=msgs,
                tools=tools.TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.2,
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                # Thêm message tool_calls vào context tạm thời của turn
                msgs.append(msg)

                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    try:
                        fn_args = json.loads(tool_call.function.arguments)
                    except Exception:
                        fn_args = {}

                    # Chạy tool của Agent B
                    res = tools.run_tool(fn_name, fn_args, session)

                    # Gom trace
                    summary_str = str(res.get("data", ""))[:160]
                    turn_trace.append({
                        "tool": fn_name,
                        "args": fn_args,
                        "result_summary": summary_str,
                    })

                    # Gom events
                    if res.get("events"):
                        turn_events.extend(res["events"])

                    # Gom citations
                    if res.get("citations"):
                        turn_citations.extend(res["citations"])

                    # Theo dõi gợi ý bài tập
                    if fn_name == "goi_y_buoc_dau":
                        hint_called = True
                        if res.get("ok"):
                            state.HINT_SESSIONS.add(session.id)

                    # Kiểm tra pending action sinh ra từ tool
                    if fn_name == "chuyen_TA" and res.get("ok"):
                        p_act = res.get("data", {}).get("pending_action")
                        if p_act:
                            turn_pending_actions.append(p_act)
                        else:
                            # Tìm trong state.STORE
                            for pa in state.STORE.get("pending_actions", []):
                                if pa not in turn_pending_actions:
                                    turn_pending_actions.append(pa)

                    # Đưa kết quả tool vào messages
                    msgs.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(res, ensure_ascii=False),
                    })
            else:
                reply = msg.content or ""
                break
        else:
            if not reply:
                reply = "Hệ thống đang bận xử lý, bạn vui lòng thử lại nhé."

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"error": "llm_unavailable", "message": str(exc)},
        )

    # 3. Lọc output qua guard filter
    f = guard.filter_output(session, user_message, reply, turn_events)
    is_blocked = f.get("blocked", False)
    if is_blocked:
        reply = f.get("text", reply)
        turn_events.append({
            "type": "blocked",
            "text": f.get("reason", "Câu trả lời bị chặn theo quy định"),
            "data": {},
        })
        notes.append({
            "type": "blocked",
            "text": f.get("reason", "Đã chặn câu trả lời vi phạm quy chế"),
        })

    # 4. Tính toán độ chắc (confidence) do server tính
    if is_blocked or g.get("must_refuse"):
        confidence = "refused"
    else:
        flagged_set = set(state.STORE.get("flagged_sections", []))
        cited_sections = {c.get("section") for c in turn_citations if c.get("section")}
        if flagged_set.intersection(cited_sections):
            confidence = "flagged"
            notes.append({
                "type": "warning",
                "text": "Mục tài liệu này đang có điểm nghi vấn mâu thuẫn cần giảng viên rà soát.",
            })
        elif turn_citations:
            confidence = "grounded"
        else:
            confidence = "no_source"

    # Lưu câu trả lời của trợ lý vào lịch sử
    session.history.append({"role": "assistant", "content": reply})

    # Tính hint_progress
    hint_progress = (
        {"level": session.hint_level, "max": 3}
        if (hint_called or session.hint_level > 0)
        else None
    )

    message_id = state.next_id("m")

    # Loại bỏ duplicate citations
    seen_quotes = set()
    unique_citations = []
    for c in turn_citations:
        key = (c.get("section"), c.get("title"))
        if key not in seen_quotes:
            seen_quotes.add(key)
            unique_citations.append(c)

    return {
        "message_id": message_id,
        "reply": reply,
        "confidence": confidence,
        "citations": unique_citations,
        "notes": notes,
        "events": turn_events,
        "pending_actions": turn_pending_actions,
        "hint_progress": hint_progress,
        "trace": turn_trace,
    }
