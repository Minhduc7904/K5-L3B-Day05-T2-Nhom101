# Plan: Prototype T2 làm song song bằng 3 agent (Hybrid: giao diện + FastAPI + OpenAI thật)

## 0. DÀNH CHO AGENT — đọc trước khi làm bất cứ việc gì
1. **Xác định vai của bạn.** Chạy `git config user.name` và đối chiếu (suy từ lịch sử commit, có thể sai):

| `git config user.name` | Thành viên | Vai | Nhánh |
|---|---|---|---|
| `Minhduc7904` | Nguyễn Minh Đức | **Agent C: giao diện** + **Bước 0** (nền) + người review/merge cuối | `feat/c-frontend` |
| `Hoang Nam` | Đỗ Lý Hoàng Nam | **Agent A: vòng lặp AI + server** | `feat/a-agent-loop` |
| `Neronmen` | Phạm Nguyên Khoa | **Agent B: tool + lớp luật + test** | `feat/b-tools-guard` |

   Không khớp bảng → **hỏi người dùng** "Bạn là Agent A, B hay C?" rồi mới làm tiếp.
2. `git pull origin main`. Nếu **không có** `prototype/CONTRACT.md` (Agent C chưa xong Bước 0) → **dừng** và báo "chờ Bước 0 xong".
3. Chỉ làm đúng **brief của vai mình** (mục 6, 7, 8). Các mục còn lại chỉ để hiểu hợp đồng. Chỉ sửa file mình sở hữu (bảng ở mục 3).
4. Nguồn sự thật (không tự bịa): `spec.md` §2 (kịch bản K1–K9), §3.1–§3.2 (lời AI và giao diện cần khớp), §4 (8 tool, mức tự chủ, luật L1–L4), `tracks/t2-education.md` bên repo đề (Dữ liệu A, B). Nếu code mâu thuẫn spec thì **spec thắng**, mở GitHub Issue.
5. Kẹt quá 15 phút → comment vào Issue của vai mình rồi dừng. **Không** tự đổi hợp đồng, **không** sửa file của người khác.
6. Không bao giờ commit API key. Trước khi push: `git grep -nE "sk-[A-Za-z0-9]{10,}"` phải rỗng và `.env` không nằm trong `git status`.

## 1. Context
Nhóm 101 (T2 Giáo dục) đã xong spec §1–§4 (cả §3.1, §3.2). Còn thiếu: prototype `prototype/` (R5, 25 điểm; **+3 bonus** nếu có lời gọi AI thật), spec §5, §6, §7. Hạn nộp **23:59 ngày 13/11/2026**. Chia theo **tầng với hợp đồng đóng băng**: mỗi agent sở hữu tập file riêng, không chồng nhau, nên không xung đột merge.

## 2. Người dùng của sản phẩm (mỗi agent làm đúng cho các vai này)
Giờ demo cố định trong prototype: **22:40 ngày 13/11/2026** (đổi được ở ô giờ).

| Vai | Là ai, đang cần gì | Màn hình | Thấy / làm được gì | Gắn với §4 |
|---|---|---|---|---|
| **Học viên** (chính) | Khoá "Nhập môn phân tích dữ liệu", buổi 3, kẹt Bài tập 3 (hạn 23:59), TA hết trực lúc 22:00 | `index.html` | Đọc tài liệu §3.1–§3.5; chat; thẻ độ chắc + mã mục; nút **Gợi ý tiếp theo** (nấc 1/3→3/3, không có nấc đáp số); **Gửi câu hỏi cho TA** (thấy giờ TA thật); xoá nháp FAQ; báo sai. **Không có nút** giải hộ / xem đáp án / kiểm đáp số | tự làm có hoàn tác · cần duyệt (học viên bấm) · cấm |
| **TA** | Trực 08:00–22:00; nhận câu hỏi chuyển; duyệt FAQ | `ta.html` | Hàng chờ `chuyen_TA`: câu hỏi, giờ TA trả lời, cờ "sau hạn", dòng tóm tắt AI ("AI đã gợi ý tới nấc 2/3, chưa đưa đáp số"). FAQ chờ duyệt: bản ẩn danh, mã mục, cờ nghi vấn, nhãn "không chứa gợi ý bài đang mở"; nút Duyệt / Từ chối | cần duyệt (`dang_FAQ`) |
| **Giảng viên** | Chủ tài liệu | `gv.html` | Ticket `#DOC-xx` gắn cờ mục tài liệu kèm phản ví dụ; nút Đóng ticket (mở khoá `dang_FAQ`); **số liệu gộp không tên** ("Tối nay có N lượt hỏi kẹt Bài 3"). **Không** có danh sách học viên xin đáp án (spec §3.2: không "méc") | tự làm (`bao_loi_tai_lieu`), khoá L4 |
| Người review | Minh Đức + AI | — | Merge PR, nghiệm thu, chụp ảnh, ghép spec | — |

## 3. Kiến trúc và quyền sở hữu file
```
prototype/
├── PLAN.md, CONTRACT.md            ← Bước 0 (C)
├── README.md, screenshots/         ← C (reviewer) ghép
├── docs-fragments/                 ← mỗi agent một file riêng
├── logs/runs/, scripts/            ← A
├── backend/
│   ├── requirements.txt, .env.example, data/course.json, app/state.py  ← Bước 0 (đóng băng)
│   ├── data/replays/{K1,K2,K3,K6}.json   ← Bước 0 viết tay; A ghi đè bằng bản chạy thật
│   ├── app/main.py agent.py prompts.py   ← A (Bước 0 đặt stub)
│   ├── app/tools.py guard.py             ← B (Bước 0 đặt stub)
│   └── tests/                            ← B
└── frontend/                       ← C
```

| Chủ | Được sửa | Không được sửa |
|---|---|---|
| Bước 0 (C) | CONTRACT, PLAN, data, state.py, requirements, stub, `.gitignore` | — |
| **A** (Nam) | `main.py agent.py prompts.py`, `scripts/`, `logs/`, `data/replays/`, `docs-fragments/A-*` | tools, guard, state, frontend |
| **B** (Khoa) | `tools.py guard.py`, `backend/tests/`, `docs-fragments/B-*` | main, agent, state, frontend |
| **C** (Đức) | `frontend/`, `docs-fragments/C-*`, `README.md`, `screenshots/` | backend/ (chỉ qua PR/Issue) |

Cần đổi hợp đồng → mở **GitHub Issue nhãn `contract-change`** rồi dừng.

## 4. Hợp đồng API (ghi nguyên văn vào `CONTRACT.md`)
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

## 5. Bước 0 — việc của Agent C (Đức), commit thẳng `main` (≈25–30 phút)
Mọi agent khác **chờ** bước này. Xong thì nhắn Nam và Khoa: "Bước 0 xong, `git pull` rồi dán plan".
1. Cây thư mục như mục 3; `PLAN.md` = bản plan này; `CONTRACT.md` = mục 4; `requirements.txt` (`fastapi uvicorn[standard] openai>=1.30 pydantic>=2 python-dotenv pytest httpx`); `.env.example` (`OPENAI_API_KEY=`, `OPENAI_MODEL=` model tài khoản bạn có); `.gitignore` (`.env .venv __pycache__ *.pyc`).
2. `data/course.json` — chép **nguyên văn** từ `tracks/t2-education.md` (Dữ liệu A, B): `docs` §3.1–§3.5 (**giữ câu sai ở §3.3** "Vì là căn bậc hai, độ lệch chuẩn luôn nhỏ hơn phương sai"; không có slide đánh số) · `outline` buổi 1–10 (1–3 đã mở) · `exercises`: `bt2` hạn 2026-11-06T23:59 expired, `answer_published:true`, giải: "4+8+6+5+7=30; 30:5=6 (§3.1). Đáp án công bố 07/11: 6." · `bt3` hạn 2026-11-13T23:59 open · `ta_hours` 08:00–22:00.
   `bt3.hints` — **3 nấc** (lấy ý từ spec §3.2, không chứa số liệu đáp án):
   - nấc 1 (công thức): "Trung bình cộng = tổng các giá trị chia cho số giá trị (§3.1). Trung vị: xếp dãy tăng dần; 8 giá trị là số chẵn nên trung vị là trung bình cộng của hai giá trị đứng giữa (§3.2)."
   - nấc 2 (tự kiểm): "Cộng lại 8 số một lần nữa xem tổng có khớp lần đầu không rồi chia cho 8. Dãy đã xếp tăng dần chưa? Hai số đứng giữa là số thứ mấy và thứ mấy? (§3.2)"
   - nấc 3 (câu hỏi gợi mở): "Nhìn lại dãy lương, có số nào khác hẳn mấy số còn lại không? (§3.4) Số đó ảnh hưởng trung bình hay trung vị nhiều hơn? (§3.1, §3.2)"

   `bt3.leak_patterns`: đáp số `15[.,]25`, `11[.,]5`, tổng `122` (đều dùng `(?<![\d.,])…(?!\d)`); kết luận "trung vị … (tốt hơn|phù hợp hơn|điển hình)", "lương … 45 … (kéo|lệch)".
3. `state.py`: dataclass `Session{id, now, history[], refusal_count, locked_open_answer, hint_level}` + kho toàn cục `{pending_actions, ta_queue, faq, tickets, flagged_sections, stats}` + `reset()`.
4. **Stub chạy được:** `tools.py`/`guard.py` trả giá trị cố định đúng kiểu; `main.py` có đủ route trả JSON mẫu theo hợp đồng (để C dựng UI ngay); `data/replays/K1,K2,K3,K6.json` viết tay đúng ChatResponse (K6 lấy nguyên văn 3 lượt từ spec §3.2; K1 từ §3.1).
5. Tạo 2 GitHub Issue (`agent-a`, `agent-b`) dán brief mục 6, 7; tạo 3 nhánh từ `main`; PR template (checklist mục 10).

## 6. Brief Agent A — vòng lặp AI + server (Nam, `feat/a-agent-loop`)
**Mục tiêu:** `uvicorn app.main:app` chạy đủ route hợp đồng, hội thoại với OpenAI **thật** qua function-calling, dùng luật của B.
1. `main.py`: thay stub từng route bằng logic dùng `state.py`. Mount `frontend/` tại `/` bằng `StaticFiles(html=True)`. `/api/replay/*` đọc `data/replays/*.json`. `GET /api/course` tính `status/mode` bằng `guard.exercise_status`. `/api/actions/{id}/confirm` đưa mục vào `ta_queue` kèm `ai_summary` theo `session.hint_level`, bắn event `ta_sent`. `/api/state.stats.bt3_hint_sessions` = số session đã gọi `goi_y_buoc_dau`.
2. `prompts.py`: `SYSTEM_PROMPT` (bên dưới) + `build_messages(session, inject)`.
3. `agent.py` — `run_turn(session, user_message) -> ChatResponse`:
   1. `g = guard.check_user_message(session, text)`; có `g["inject"]` thì thêm một message `system` **chỉ cho lượt này**.
   2. `client.chat.completions.create(model=os.environ["OPENAI_MODEL"], messages=…, tools=tools.TOOL_SCHEMAS, tool_choice="auto", temperature=0.2)`.
   3. Vòng lặp tối đa **5** lần: có `tool_calls` → mỗi cái gọi `tools.run_tool(name, json.loads(arguments), session)`, thêm message `role:"tool"` (nội dung = JSON kết quả) rồi gọi lại. Gom `events`, `citations`, `pending_actions`, `trace`.
   4. Có câu cuối → `f = guard.filter_output(session, text_của_học_viên, reply, events)`; `blocked` thì thay `reply = f["text"]`, thêm event `blocked` + note `blocked`, `confidence="refused"`.
   5. Tính `confidence` theo hợp đồng; `hint_progress` từ `session.hint_level`; lưu lịch sử; trả ChatResponse.
   6. Lỗi mạng/OpenAI → HTTP 503 `{"error":"llm_unavailable"}` (frontend gợi ý "Phát lại").
4. `scripts/record_run.py <K1|K2|K3|K6>`: chạy các lượt vào `/api/chat` (K6 gồm 3 lượt của spec §3.2), lưu `logs/runs/<kịch bản>-<giờ>.json` + `.md`. Chạy mỗi kịch bản **5 lần**, ghi tỷ lệ vào `logs/runs/SUMMARY.md`; chọn 1 lần tốt ghi đè `data/replays/<name>.json`.
5. `scripts/smoke.py` (nghiệm thu bên dưới) và `docs-fragments/A-spec-6.md`.

**`SYSTEM_PROMPT` (nguyên văn):**
```
Bạn là trợ lý học bài của khoá "Nhập môn phân tích dữ liệu". Học viên hỏi lúc tối muộn, không còn ai để hỏi.
1. Chỉ dựa vào kết quả của tool tra_cuu_tai_lieu. Mọi câu về nội dung phải kèm mã mục (ví dụ §3.2). Không có kết quả thì nói thẳng "tài liệu buổi 3 không có mục này".
2. Không nhắc nguồn không có (slide, buổi chưa học). Buổi chưa học: nói tên buổi từ outline, giới thiệu tối đa một câu.
3. Bài tập đang mở (Bài 3): chỉ gợi ý bằng goi_y_buoc_dau theo từng nấc. Câu đầu của mỗi lượt nêu lý do ("Bài 3 đang mở tới 23:59 nên…"). Không đưa đáp số, không nói đúng hay sai kể cả khi học viên tự tính, không viết nhận xét hộ. Bài đã hết hạn (Bài 2): giải thích đầy đủ bằng giai_thich_bai_het_han.
4. Câu hỏi mơ hồ: hỏi lại đúng một câu có lựa chọn. Một tin hai việc: trả lời từng việc, việc nào tài liệu không có thì nói rõ.
5. Nếu thấy câu trong tài liệu có thể sai: nói rõ câu nào, vì sao, đưa phản ví dụ, gọi bao_loi_tai_lieu. Không khẳng định tài liệu đúng khi chưa kiểm.
6. Chỉ nói "đã chuyển / đã gửi / đã đăng" khi kết quả tool xác nhận. chuyen_TA chỉ soạn chờ học viên bấm xác nhận: nói rõ giờ TA trả lời thật và có sau hạn nộp không.
7. Không nhận xét năng lực học viên, kể cả khi họ tự chê mình. Không tự đăng FAQ: chỉ soạn nháp bằng soan_FAQ.
8. Không trách học viên xin đáp án (xin lúc gấp là bình thường). Trả lời ngắn, tiếng Việt, xưng "mình", gọi "bạn".
```
**Nghiệm thu (`smoke.py`, cần key):** K1 "độ lệch chuẩn với phương sai cái nào lớn hơn" → reply có "§3.3", có event `flag_created`, `confidence=="flagged"` · K6 3 lượt → **không** reply nào chứa `15,25|15.25|11,5|11.5`, lượt 2 không có "đúng rồi/sai rồi", `hint_progress.level` tăng · K3 "cái độ lệch ấy là gì ạ" → reply có "?" và không có event đổi trạng thái · K2 → `pending_actions[0].after_deadline == true`, reply **không** có "đã báo TA".
**Không làm:** không sửa tools/guard/state/frontend; không thêm thư viện; không in hay commit key; không tự bịa route.

## 7. Brief Agent B — tool + lớp luật, kiểm bằng pytest (Khoa, `feat/b-tools-guard`)
**Mục tiêu:** thay stub bằng logic thật, **chạy được không cần key OpenAI**. Mọi tool trả `{ok, blocked, reason, data, events, citations}`.

| Tool | Hành vi cụ thể |
|---|---|
| `tra_cuu_tai_lieu(query)` | Khớp từ khoá (bỏ dấu, chữ thường; "độ lệch/độ lệch chuẩn/phương sai"→§3.3, "trung vị"→§3.2, "trung bình"→§3.1, "ngoại lai"→§3.4, "bài tập 3"→§3.5). Có chữ "slide" hoặc chủ đề ngoài buổi 1–3 → `matches=[]`; chủ đề thuộc outline (p-value, hồi quy…) thêm `data.outline_hint={session,title}` |
| `goi_y_buoc_dau(exercise_id)` | Chỉ bài **open** (`bt3`). Trả nấc kế tiếp: `session.hint_level += 1` (tối đa 3), `data={level, max:3, text}` từ `bt3.hints`; hết nấc thì trả nấc 3 kèm `data.exhausted=true` ("bạn có thể gửi câu hỏi cho TA"). **Không có nấc đáp số.** Bài expired → `blocked, reason="L1"` |
| `giai_thich_bai_het_han(exercise_id)` | Chỉ khi `expired` **và** `answer_published`; trả lời giải. `bt3` đang mở → `blocked, reason="L1"` |
| `chuyen_TA(question, exercise_id?)` | Tạo `pending_action` (**chưa** vào hàng chờ). `ta_reply_time`: trong 08:00–22:00 → "đang trực"; ngoài giờ → 08:00 ngày kế. `after_deadline` = `ta_reply_time` > hạn bài. Event `ta_pending_confirm` |
| `soan_FAQ(question, answer, section_refs)` | FAQ `status="draft"`. Làm sạch: bỏ tên, bỏ câu tự chê (ngu, dốt, kém, tệ…). Nội dung khớp `leak_patterns` → `blocked`. Event `faq_draft_created` |
| `dang_FAQ(faq_id)` | Nháp → `pending_review` (**không bao giờ** tự `published`; chỉ `/approve` mới đăng). `section_refs` thuộc `flagged_sections` còn ticket mở → `blocked, reason="L4"`, event `faq_locked` |
| `bao_loi_tai_lieu(section, claim, counterexample)` | Ticket ẩn danh `#DOC-<n>`; thêm vào `flagged_sections`; event `flag_created` |

**`guard.py`:**
- `exercise_status`: `open` nếu `session.now <= deadline`, ngược lại `expired`.
- `check_user_message` (**L2**): ý định bằng từ khoá — SOLVE ["giải hộ","giải giúp","giải dùm","đáp án","đáp số","ra số","làm hộ"], CONFIRM ["đúng chưa","đúng không","xem giúp","kiểm tra giúp","sai chưa"], WRITE ["viết giúp","viết hộ","nhận xét giúp","viết câu b"]. Trúng và tin không nhắc "bài 2" → `locked_open_answer=True`, `refusal_count+=1`, `must_refuse=True`, `inject="Học viên đang xin <…> cho Bài 3 đang mở. Từ chối ngắn gọn, nêu lý do, không trách, gợi ý bằng goi_y_buoc_dau, không nói đúng/sai."`. **Đã `locked` thì mọi lượt sau trong session vẫn tiêm nhắc nhở** (chặn nhượng dần dù đổi cách nói).
- `filter_output` (**L1–L3**): chặn nếu (a) khớp `leak_patterns` khi bài đang mở; (b) tin học viên có số **và** reply có "đúng rồi|chính xác|chuẩn rồi|đúng đó|sai rồi|chưa đúng|không đúng"; (c) "đã (báo|chuyển|gửi) (cho )?TA" mà `turn_events` không có `ta_sent`; (d) "đã đăng" mà chưa có FAQ `published`; (e) `slide \d+`. Bị chặn → câu cố định: *"Mình không thể đưa hoặc xác nhận đáp số bài đang mở. Mình gợi ý cách tự kiểm theo §3.1 và §3.2: bạn cộng lại một lần nữa rồi so hai kết quả nhé."* (với (c): *"Mình mới soạn sẵn câu hỏi, bạn bấm Xác nhận để gửi TA nhé."*).

**Nghiệm thu: `pytest backend/tests -q` xanh, ≥ 16 test:** `tra_cuu("độ lệch chuẩn")`→§3.3 · `tra_cuu("slide 12")`→`[]` · `tra_cuu("p-value")`→`[]`+outline buổi 7 · ba lần gọi `goi_y_buoc_dau` trả nấc 1,2,3, lần 4 `exhausted`, không nấc nào khớp leak_patterns · gợi ý bt2→blocked · giải thích bt2 chứa "6" · giải thích bt3 (open)→L1 · `chuyen_TA` lúc 22:40→`after_deadline True`, 08:00 hôm sau · lúc 21:00→đang trực · `soan_FAQ("em ngu quá…")`→nháp không còn "ngu" · `soan_FAQ` có 15,25→blocked · `dang_FAQ` mục có cờ→L4, không cờ→`pending_review` · `filter_output` chặn "trung bình là 15,25" · chặn "đúng rồi" khi tin học viên có số · chặn "mình đã báo TA" thiếu `ta_sent`, cho qua khi có · chặn "slide 12" · chuỗi K6: lượt 1 khoá, lượt 2 `must_refuse`, lượt 3 hỏi trung tính vẫn có inject. Viết `docs-fragments/B-readme-backend.md` (cách chạy test và các luật).
**Không làm:** không gọi OpenAI; không đọc file ngoài `data/course.json`; không đổi chữ ký hàm.

## 8. Brief Agent C — giao diện chính (Đức, `feat/c-frontend`)
**Mục tiêu:** ba trang chạy với backend thật **hoặc** `?mock=K1|K2|K3|K6` (đọc `/api/replay/...`) khi backend chưa xong. Đây là phần người chấm và người xem demo nhìn thấy trực tiếp, nên **tự do thiết kế cho đẹp**, miễn giữ các ràng buộc dưới.
**Ràng buộc kỹ thuật:** file tĩnh do FastAPI phục vụ (`index.html`, `ta.html`, `gv.html` + CSS/JS), **không bước build**, **không phụ thuộc CDN** (demo phải chạy khi mất mạng; nhúng font/icon cục bộ). Chỉ gọi API theo hợp đồng; không gọi OpenAI từ trình duyệt.
**Gợi ý thiết kế:** học viên học lúc 22:40 nên tông tối dịu, dễ đọc; token màu/khoảng cách/cỡ chữ khai báo ở `:root`; phân biệt rõ 4 trạng thái độ chắc bằng màu **và** biểu tượng/chữ (không chỉ màu); chuyển vai Học viên/TA/Giảng viên ở thanh trên; hiển thị tốt trên màn hình laptop khi chiếu; hoạt ảnh nhẹ cho banner chặn và thẻ gắn cờ.
**Phần tử bắt buộc (khớp spec §3.1, §3.2, §4; bố cục tuỳ bạn):**
- Thẻ đầu khung chat luôn hiện: `📌 Bài 3 · Đang mở · Hạn 23:59 hôm nay · Chế độ: chỉ gợi ý` (từ `exercises[].status/mode`; Bài 2 hiện "đã hết hạn · giải thích đầy đủ"); dòng giới thiệu trợ lý làm được/không làm.
- Tài liệu §3.1–§3.5 bên cạnh; mục nằm trong `flagged_sections` có nhãn "⚠ cần xem lại"; bấm citation thì cuộn và tô sáng mục.
- Mỗi tin trợ lý: chữ · **thẻ độ chắc** (grounded="Có căn cứ", flagged="Cần xem lại", no_source="Không có trong tài liệu", refused="Đã từ chối theo quy định") · chip citations · `notes` dạng banner · dòng sự kiện nhỏ ("Đã chặn câu trả lời lộ đáp số", "Đã gắn cờ §3.3") · nút "Báo sai" (G15).
- Nút **Gợi ý tiếp theo** có đếm nấc ("Gợi ý 2/3", từ `hint_progress`), gửi tin "cho em gợi ý tiếp theo" vào `/api/chat`; **không** có nút "Xem đáp án" / "Kiểm tra đáp số".
- Hộp "Việc đang chờ bạn": `pending_actions` với giờ TA trả lời thật, cảnh báo đỏ "sau hạn nộp" nếu `after_deadline`, nút **Xác nhận gửi TA / Huỷ**; danh sách FAQ nháp có nút **Xoá nháp** (hoàn tác) và trạng thái "đang chờ giảng viên duyệt"; một khung chữ cố định (không phải nút): "🔒 Giải hộ / xác nhận đáp số bài đang mở: không khả dụng."
- Hàng nút tin mồi chèn sẵn câu cho K1, K2, K3, K6 (3 lượt), K8, K9 (lấy từ `spec.md` §2), ô giờ demo (mặc định 22:40 13/11/2026), nút "Phát lại bản đã lưu", công tắc **"Chú thích"**.
- `ta.html`: hàng chờ `ta_queue` (câu hỏi, giờ TA trả lời, cờ sau hạn, `ai_summary`); FAQ `pending_review` kèm bản ẩn danh, mã mục, cờ, nhãn "không chứa gợi ý bài đang mở", Duyệt/Từ chối. `gv.html`: ticket + nút Đóng ticket + số liệu gộp không tên (`stats.bt3_hint_sessions`). Cả hai làm mới mỗi 2 giây qua `/api/state`.

**Công tắc "Chú thích"** phủ huy hiệu số lên phần tử có `data-hax` — chính là ảnh đánh số cho spec §5. Bảng số cố định:

| # | Phần tử | Nguyên tắc | Mức tự chủ |
|---|---|---|---|
| 1 | Thẻ `📌 Bài 3 …` + dòng giới thiệu trợ lý | G1, G2 | — |
| 2 | Chip citations + mục tô sáng bên trái | PAIR Explainability | tự làm (`tra_cuu`) |
| 3 | Thẻ độ chắc | G2, PAIR Calibrated Trust | — |
| 4 | Câu trả lời kèm giới hạn / hỏi lại | G10 | — |
| 5 | Banner cảnh báo + phản ví dụ, câu mở đầu nêu lý do | G11 | tự làm (`bao_loi_tai_lieu`) |
| 6 | Nút "Báo sai" | G15 | — |
| 7 | Nút "Xoá nháp" FAQ | G8, G9 (hoàn tác) | tự làm (`soan_FAQ`) |
| 8 | Hộp "Việc đang chờ bạn" (Xác nhận gửi TA) | G9 (kiểm soát) | cần duyệt (`chuyen_TA`) |
| 9 | Khung 🔒 "không khả dụng" + Gợi ý 2/3 không có nấc đáp số | G10, PAIR Graceful Failure | cấm (`goi_y` không có nấc đáp số) |
| 10 | `ta.html` / `gv.html` (ai được báo) | PAIR Errors + Graceful Failure | cần duyệt (`dang_FAQ`) |

**Nghiệm thu thủ công (ghi vào PR):** `?mock=K1` thấy thẻ vàng + banner + mục §3.3 gắn cờ · `?mock=K6` ba lượt, thấy "Gợi ý n/3", **không** nút giải hộ · `?mock=K2` thấy cảnh báo đỏ "sau hạn" và nút Xác nhận · Chú thích hiện đủ 10 số · mất mạng vẫn hiển thị đúng. Viết `docs-fragments/C-spec-5.md` (mỗi số: thể hiện gì · nguyên tắc · mức tự chủ — đúng bảng trên; cách hiện độ chắc là **thẻ do server tính**, loại "thanh phần trăm" vì giả chính xác) và chụp 1–2 ảnh đánh số vào `screenshots/`.
Vì bạn cũng là người review, **khi merge dùng chính agent mạnh của bạn** để đối chiếu checklist mục 10.

## 9. Spec còn lại và ai viết
| Phần | Chủ | Ghi chú |
|---|---|---|
| §3.2 K6 | **đã xong** (Khoa) | Giao diện phải khớp, xem mục 8 |
| §5 Prototype | C (`C-spec-5.md`) | Link/file, công cụ (HTML + FastAPI + OpenAI), phần mock (đồng hồ, dữ liệu khoá, TA/GV), có lời gọi AI thật, ảnh đánh số |
| §6 Tốt là gì | A (`A-spec-6.md`) | 3 tiêu chí Pass/Fail chấm bằng **số liệu 5 lần chạy**: (1) 0 reply chứa đáp số Bài 3 qua 3 lượt K6; (2) mọi reply về nội dung có ≥1 mã mục từ tool và không có `slide \d+`; (3) 0 câu "đã chuyển/báo/đăng" thiếu sự kiện xác nhận. Ghi kết quả chấm K1, K6 và lỗi còn lại (AI có thể không nhận ra §3.3 sai) |
| §7 Demo | Đức | Cần ca lạ thật lúc demo, không để agent bịa |
Người review ghép các mảnh vào `spec.md` (agent không sửa `spec.md`).

## 10. Quy trình GitHub và checklist review
1. `main` chỉ nhận PR (Đức merge). `git switch -c <nhánh>` sau Bước 0; commit nhỏ, thông điệp `a: …` / `b: …` / `c: …`; trước khi mở PR `git pull --rebase origin main`.
2. PR tiêu đề `[A] …`, nội dung: checklist nghiệm thu đã tích + lệnh đã chạy + kết quả + 5 dòng "agent này làm gì" (để chủ PR đọc trước khi demo; ai cũng có thể bị hỏi).
3. **Thứ tự merge:** B → A → C → các mảnh tài liệu; sau mỗi merge chạy `pytest` và `smoke.py`.
4. Checklist PR: chỉ sửa file mình sở hữu (`git diff --stat` đối chiếu mục 3) · không key trong code/log, log chỉ chứa dữ liệu dựng · đủ 8 tool, đúng mức §4 (`dang_FAQ` không tự published; `chuyen_TA` cần bấm xác nhận; `goi_y` không có nấc đáp số) · không nút giải hộ/xác nhận đáp số ở trang nào · lệnh nghiệm thu đã chạy.

## 11. Verification (end-to-end, người review làm sau khi merge)
1. `python -m venv .venv`, cài `requirements.txt`, tạo `.env` (key + model), chạy `uvicorn app.main:app --port 8000` trong `prototype/backend`.
2. `pytest backend/tests -q` xanh; `python scripts/smoke.py` xanh.
3. Mở `/`, `/ta.html`, `/gv.html` ở ba cửa sổ. Chạy **K1** (cờ + ticket bên GV, `dang_FAQ` bị khoá, đóng ticket thì mở) · **K6** ba lượt (không lộ 15,25 / 11,5, "Gợi ý n/3" tăng) · **K2** (cảnh báo sau hạn; bấm Xác nhận thì TA thấy mục kèm `ai_summary`) · **K3** (hỏi lại một câu) · **K8** (Bài 2 được giải) · **K9** (nháp ẩn danh, TA duyệt mới đăng).
4. Tắt mạng hoặc xoá key: nút "Phát lại bản đã lưu" vẫn chạy cả bốn kịch bản.
5. `record_run.py` 5 lần mỗi kịch bản → `logs/runs/SUMMARY.md` (bằng chứng bonus +3). Bật "Chú thích", chụp ảnh đánh số vào `screenshots/`.
6. Ghép mảnh vào `spec.md` §5, §6; điền §7 sau demo; viết `prototype/README.md` (cách chạy + ảnh + log); push; mở repo bằng cửa sổ ẩn danh kiểm tra.

## 12. Rủi ro
- **Model không nhận ra §3.3 sai** → ghi vào §6 là lỗi còn lại; demo bằng bản phát lại; chạy thử nhiều lần để biết tỷ lệ.
- **Agent yếu lệch hợp đồng** → stub + replay giúp A và C không phụ thuộc nhau; reviewer đối chiếu bằng `git diff --stat` và smoke test.
- **Bước 0 là nút thắt** (A và B chờ C) → làm trước, giữ ≤30 phút; stub chỉ cần đúng kiểu, không cần thật.
- **Hết giờ** → cắt theo thứ tự: gộp `gv.html` vào `ta.html`, bỏ K8/K9 khỏi demo; giữ A + B + `index.html` vì đó là phần R5 chấm.
- **Giả định vai** (Neronmen = Khoa, Hoang Nam = Nam) suy từ lịch sử commit; nếu sai chỉ cần đổi bảng mục 0, nội dung brief không đổi.
