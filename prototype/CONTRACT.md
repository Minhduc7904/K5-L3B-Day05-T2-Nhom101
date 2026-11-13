# CONTRACT — Hợp đồng API (đóng băng)

> Nguồn: `PLAN.md` mục 4. Muốn đổi → mở GitHub Issue nhãn `contract-change` rồi dừng; không tự sửa file này.

State dùng chung toàn cục (TA và GV thấy việc của học viên); chỉ lịch sử chat, đồng hồ và `hint_level` gắn với `session_id`. `POST /api/reset` xoá hết để demo lại.

| Method + đường dẫn | Body | Trả về |
|---|---|---|
| `POST /api/session` | `{now?: ISO}` mặc định `2026-11-13T22:40:00+07:00` | `{session_id, now}` |
| `GET /api/course?session_id=` | — | `{course:{title,current_session:3,outline[],ta_hours:{start:"08:00",end:"22:00"}}, exercises:[{id,title,deadline,status:"open"\|"expired",mode:"hint_only"\|"full_explain",answer_published}], docs:[{section,title,text}], flagged_sections:[string]}` |
| `POST /api/chat` | `{session_id, message}` | **ChatResponse** |
| `GET /api/state` | — | `{pending_actions[], ta_queue[], faq[], tickets[], flagged_sections[], stats:{bt3_hint_sessions:int}}` |
| `POST /api/actions/{id}/confirm` · `/cancel` | `{session_id}` | `{ok, ta_queue_item?}`; item có `ai_summary` ("AI đã gợi ý tới nấc N/3, chưa đưa đáp số") |
| `DELETE /api/faq/{id}` | — | xoá **nháp** (hoàn tác của `soan_FAQ`) |
| `POST /api/faq/{id}/approve` · `/reject` | — | FAQ → `published` / `rejected` |
| `POST /api/tickets/{id}/close` | — | đóng ticket, gỡ cờ mục → mở khoá `dang_FAQ` |
| `POST /api/feedback` | `{session_id, message_id, text}` | tạo ticket `type:"feedback"` (nút "Báo sai", G15) |
| `GET /api/replay/{K1\|K2\|K3\|K6}` | — | `{turns:[{user, response: ChatResponse}]}` |
| `POST /api/reset` | — | `{ok:true}` |

**ChatResponse:**
```json
{
  "message_id": "m1",
  "reply": "string (tiếng Việt)",
  "confidence": "grounded | flagged | no_source | refused",
  "citations": [{"section": "§3.3", "title": "…", "quote": "…"}],
  "notes": [{"type": "warning | blocked | info", "text": "…"}],
  "events": [{"type": "tool_call | blocked | flag_created | faq_draft_created | faq_pending_review | faq_locked | ta_pending_confirm | ta_sent", "text": "…", "data": {}}],
  "pending_actions": [{"id": "a1", "type": "chuyen_TA", "summary": "…", "ta_reply_time": "2026-11-14T08:00:00+07:00", "after_deadline": true}],
  "hint_progress": {"level": 2, "max": 3},
  "trace": [{"tool": "tra_cuu_tai_lieu", "args": {}, "result_summary": "…"}]
}
```
(`hint_progress` là `null` khi lượt đó không gợi ý bài.)

**Độ chắc do server tính, model không được tự khai:** `flagged_sections` giao với citations → `flagged`; có citations → `grounded`; không có → `no_source`; câu bị chặn/từ chối theo luật → `refused`. **Citations chỉ lấy từ kết quả `tra_cuu_tai_lieu` thật của lượt đó**, không lấy từ chữ model viết (chặn bịa nguồn "slide 12").

**Giao ước hàm Python** (stub do Bước 0 đặt, B lấp thân, A chỉ gọi):
```python
# tools.py
TOOL_SCHEMAS: list[dict]    # định dạng OpenAI: {"type":"function","function":{name,description,parameters}}
def run_tool(name: str, args: dict, session) -> dict
#   {"ok": bool, "blocked": bool, "reason": str|None, "data": dict, "events": list[dict], "citations": list[dict]}
# guard.py
def check_user_message(session, text: str) -> dict   # {"must_refuse": bool, "inject": str|None, "intent": "solve|confirm|write|none"}
def filter_output(session, user_text: str, text: str, turn_events: list[dict]) -> dict  # {"text","blocked","reason"}
def exercise_status(session, exercise_id: str) -> str   # "open" | "expired"
```

