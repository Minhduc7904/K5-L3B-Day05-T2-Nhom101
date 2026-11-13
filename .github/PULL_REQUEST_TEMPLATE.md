## [A|B|C] Tiêu đề

### Agent này làm gì (5 dòng, để chủ PR đọc trước khi demo)
1.
2.
3.
4.
5.

### Lệnh nghiệm thu đã chạy + kết quả
```
(dán lệnh và kết quả: pytest / smoke.py / ?mock=… )
```

### Checklist (PLAN.md mục 10)
- [ ] Chỉ sửa file mình sở hữu (`git diff --stat` đối chiếu PLAN.md mục 3)
- [ ] Không có key trong code/log: `git grep -nE "sk-[A-Za-z0-9]{10,}"` rỗng, `.env` không nằm trong `git status`
- [ ] Log chỉ chứa dữ liệu dựng
- [ ] Đủ 8 tool, đúng mức §4: `dang_FAQ` không tự `published` · `chuyen_TA` cần bấm xác nhận · `goi_y_buoc_dau` không có nấc đáp số
- [ ] Không có nút giải hộ / xem đáp án / xác nhận đáp số ở trang nào
- [ ] Không đổi CONTRACT.md (cần đổi → Issue `contract-change`)
- [ ] Đã `git pull --rebase origin main` trước khi mở PR

Thứ tự merge: B → A → C → các mảnh tài liệu; sau mỗi merge chạy `pytest` và `smoke.py`.
