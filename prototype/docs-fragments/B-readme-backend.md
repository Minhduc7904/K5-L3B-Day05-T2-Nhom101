# Backend phần B: tool + lớp luật (Khoa)

File: `backend/app/tools.py`, `backend/app/guard.py`, `backend/tests/`. Không cần key OpenAI.

## Chạy test

```bash
cd prototype
python -m venv .venv
.venv/Scripts/python -m pip install pytest      # Windows; macOS/Linux: .venv/bin/python
.venv/Scripts/python -m pytest -q               # 32 test
```

## 7 tool và mức tự chủ (khớp spec §4)

Mọi tool trả `{ok, blocked, reason, data, events, citations}`. Bị chặn thì `ok=false, blocked=true`, `data.message` là câu giải thích để model nói lại.

| Tool | Mức | Làm gì | Bị chặn khi |
|---|---|---|---|
| `tra_cuu_tai_lieu` | tự làm | Khớp từ khoá (bỏ dấu) → mục §3.1–§3.5, trả citation nguyên văn | Hỏi "slide" → `matches=[]` + note. Chủ đề buổi chưa học → `matches=[]` + `outline_hint` |
| `goi_y_buoc_dau` | tự làm, có trần | Nấc 1 công thức → 2 tự kiểm → 3 câu hỏi gợi mở. Gọi quá 3 lần vẫn trả nấc 3 + `exhausted` | Bài đã hết hạn (L1). **Không có nấc đáp số** |
| `giai_thich_bai_het_han` | tự làm | Lời giải Bài 2 | Bài đang mở (L1), hoặc chưa công bố đáp án |
| `chuyen_TA` | cần học viên xác nhận | Tạo `pending_action` (chưa vào `ta_queue`), tính giờ TA trả lời thật và cờ `after_deadline` | — |
| `soan_FAQ` | tự làm | Nháp ẩn danh: bỏ tên, bỏ câu tự chê | Có đáp số Bài 3 (`L1_leak`) |
| `dang_FAQ` | cần GV/TA duyệt | Nháp → `pending_review`. **Không bao giờ tự `published`** | Mục đang bị gắn cờ (L4, event `faq_locked`) |
| `bao_loi_tai_lieu` | tự làm | Ticket ẩn danh `DOC-n`, gắn cờ mục. Gọi lại cùng mục không tạo ticket trùng | Mục không tồn tại |

Tool lạ (ví dụ model tự bịa `giai_ho`) → `blocked, reason="unknown_tool"`.

**Cho Agent A:** `chuyen_TA` trả hành động ở `data.pending_action` (đúng hình dạng `pending_actions[]` trong ChatResponse) và đã thêm vào `STORE["pending_actions"]`. `goi_y_buoc_dau` tự cập nhật `session.hint_level`, `HINT_SESSIONS` và `stats.bt3_hint_sessions`.

## Luật trong `guard.py`

- **L1 `exercise_status`:** `open` nếu `session.now <= deadline`. Đổi ô giờ demo sang 14/11 thì Bài 3 thành `expired`.
- **L2 `check_user_message`:** nhận ý định xin giải / xác nhận / viết hộ bằng từ khoá. Trúng với Bài 3 đang mở → `must_refuse` + khoá session. Đã khoá thì **mọi lượt sau vẫn có `inject` nhắc luật**, kể cả khi học viên đổi cách nói (chặn "nhượng dần" của K6).
- **L1–L3 `filter_output`:** chặn trước khi hiện (a) đáp số hoặc kết luận Bài 3 (`leak_patterns`) · (b) "đúng rồi / sai rồi" khi học viên gửi con số · (c) "đã báo/chuyển/gửi TA" mà lượt đó chưa có event `ta_sent` · (d) "đã đăng" khi chưa có FAQ `published` · (e) nhắc "slide N" như thể có thật.

## Mấy chỗ B chủ động làm khác plan một chút (theo nguyên tắc "spec thắng")

1. **"đúng không" chỉ tính là xin xác nhận đáp số khi tin có con số hoặc nhắc Bài 3 / câu a, b.** Nếu không, câu lý thuyết của K1 ("độ lệch chuẩn luôn nhỏ hơn phương sai đúng không") cũng bị từ chối, trái với §3.1.
2. **(b) không áp cho Bài 2:** học viên hỏi "bài 2 em ra 6 đúng không" thì được trả lời, vì bài đã hết hạn (K8, spec §4).
3. **(e) giữ câu phủ định:** "tài liệu không có slide 12" là câu trả lời đúng của K4 nên không bị chặn. Bị chặn thì thay bằng câu hỏi lại về mục, không dùng câu về đáp số.
4. **(c), (d), (e) có câu thay riêng** cho đúng tình huống (TA, FAQ, slide). Plan chỉ ghi câu thay cho đáp số và TA.

## Lỗi còn lại đã biết

- Khớp từ khoá nên câu hỏi diễn đạt lạ có thể không ra mục nào; khi đó model nhận `matches=[]` và phải nói "tài liệu không có".
- `leak_patterns` có mẫu "trung vị … phù hợp hơn". Khi Bài 3 đang mở, một câu giảng chung chung kiểu "trung vị phù hợp hơn cho dữ liệu lệch" cũng bị chặn. Nhóm chấp nhận chặn thừa còn hơn lộ đáp án câu b.
