# Mảnh ghép cho spec §5 — Prototype (Agent C)

> Người review dán phần dưới vào `spec.md` §5. Chỗ ghi **[chờ A]** cần điền sau khi merge nhánh `feat/a-agent-loop`.

## §5. Prototype (chặng 5)

**Link / file.** Thư mục `prototype/` trong repo này. Chạy `uvicorn app.main:app --port 8000` trong `prototype/backend`, rồi mở `http://127.0.0.1:8000/` (Học viên), `/ta.html` (TA), `/gv.html` (Giảng viên). Cách chạy chi tiết: `prototype/README.md`.

**Công cụ.** Giao diện HTML/CSS/JS thuần (không bước build, không CDN, chạy được khi mất mạng) · máy chủ FastAPI · OpenAI function-calling với 7 tool của §4 · lớp luật L1–L4 viết bằng Python, có pytest.

**Phần nào mock.**
- Đồng hồ: cố định 22:40 ngày 13/11/2026, đổi được ở ô "Giờ" trên thanh trên (đổi sang sau 23:59 thì Bài 3 thành "đã hết hạn").
- Dữ liệu khoá học: `backend/data/course.json`, chép nguyên văn Dữ liệu A và B của đề (giữ câu sai ở §3.3).
- TA và giảng viên: hai trang `ta.html`, `gv.html` do người demo bấm, không có người thật trực.
- Bản phát lại: `?mock=K1|K2|K3|K6` đọc bản đã lưu ở `backend/data/replays/`, không gọi AI. Trên màn hình luôn có dải "Đang phát lại bản đã lưu" để không lẫn với lời gọi thật.

**Có lời gọi AI thật không.** Có **[chờ A: xác nhận sau khi merge]**. Tin của học viên đi qua `/api/chat` tới OpenAI kèm 7 tool. Bằng chứng: `prototype/logs/runs/SUMMARY.md` (5 lần chạy mỗi kịch bản) **[chờ A]**.

### Ảnh đánh số

Ảnh chụp từ chính prototype khi bật công tắc **Chú thích** (số do giao diện phủ lên phần tử có `data-hax`, không vẽ tay):

- `prototype/screenshots/01-hoc-vien-K1-tai-lieu-sai.png` — K1, đủ số 1–10.
- `prototype/screenshots/02-hoc-vien-K6-nhuong-dan.png` — K6 lượt 3, "Gợi ý 3/3".
- `prototype/screenshots/03-giang-vien-ticket.png` — trang giảng viên, số 10.

| # | Phần tử trên màn hình | Thể hiện gì | Nguyên tắc | Mức tự chủ |
|---|---|---|---|---|
| 1 | Thẻ `📌 Bài 3 · Đang mở · Hạn 23:59 hôm nay · Chế độ: chỉ gợi ý` + dòng "Mình làm được / Mình không làm" | Học viên biết từ đầu trợ lý làm được gì với bài này, không phải nài rồi mới bị từ chối. Trạng thái lấy từ trang khoá học (luật L1), không do AI đoán | G1, G2 | — |
| 2 | Chip mã mục dưới câu trả lời; bấm thì cột tài liệu bên trái cuộn tới và tô sáng mục đó | Mọi câu về nội dung đều chỉ ra mục. Chip lấy từ kết quả `tra_cuu_tai_lieu` thật của lượt đó, không lấy từ chữ AI viết, nên không có "slide 12" | PAIR Explainability | tự làm (`tra_cuu_tai_lieu`) |
| 3 | Thẻ độ chắc ở đầu mỗi câu trả lời: ✓ Có căn cứ · ⚠ Cần xem lại · Không có trong tài liệu · Đã từ chối theo quy định | Học viên biết nên tin câu này tới đâu. Bốn trạng thái khác nhau cả màu, biểu tượng và chữ | G2, PAIR Calibrated Trust | — |
| 4 | Thân câu trả lời: nói rõ giới hạn ("chỉ đúng khi phương sai lớn hơn 1") hoặc hỏi lại một câu có lựa chọn | AI thu hẹp phạm vi khi không chắc thay vì đoán | G10 | — |
| 5 | Banner vàng + hộp "Câu cần xem lại / Phản ví dụ đã gửi giảng viên"; ở K6 là dòng "Bài 3 đang mở: chỉ gợi ý…" | Giải thích vì sao trợ lý trả lời như vậy, kèm bằng chứng học viên tự kiểm được | G11 | tự làm (`bao_loi_tai_lieu`) |
| 6 | Nút "Báo sai" dưới mỗi câu trả lời | Học viên phản ánh ngay tại chỗ, nhận mã ticket khi hệ thống xác nhận; ticket không kèm tên | G15 | — |
| 7 | Ô "Nháp FAQ của bạn" + nút "Xoá nháp" | AI chỉ soạn nháp riêng tư, ẩn danh. Học viên xoá được bất cứ lúc nào; trạng thái "đang chờ giảng viên duyệt" hiện rõ | G8, G9 (hoàn tác) | tự làm (`soan_FAQ`) |
| 8 | Hộp "Việc đang chờ bạn": câu hỏi soạn sẵn, giờ TA trả lời thật, cảnh báo đỏ "Sau hạn nộp", nút Xác nhận gửi TA / Huỷ | AI không tự chuyển và không nói "đã báo TA". Học viên thấy cái giá (TA trả lời sau hạn) rồi mới quyết | G9 (kiểm soát) | cần duyệt (`chuyen_TA`, học viên bấm) |
| 9 | Khung `🔒 Giải hộ / xác nhận đáp số bài đang mở: không khả dụng` (không phải nút) + bộ đếm "Gợi ý n/3 · không có nấc đáp số" | Việc bị cấm thì không có nút và không có tool. Gợi ý dừng ở nấc 3 (câu hỏi gợi mở), từ chối xong vẫn còn đường đi tiếp | G10, PAIR Graceful Failure | cấm |
| 10 | Thanh chuyển vai và hai trang TA / Giảng viên | Ai được báo, báo gì: TA thấy câu hỏi kèm "AI đã gợi ý tới nấc 2/3, chưa đưa đáp số"; giảng viên thấy ticket kèm phản ví dụ và số gộp không tên. Không trang nào liệt kê ai xin đáp án | PAIR Errors + Graceful Failure | cần duyệt (`dang_FAQ`, TA hoặc giảng viên bấm) |

### Quyết định: cách hiện độ chắc và bằng chứng

**Chọn: thẻ độ chắc bốn trạng thái do server tính, đi kèm chip mã mục.** Server so nguồn tra cứu của lượt đó với danh sách mục đang bị gắn cờ: có nguồn thì "Có căn cứ", nguồn đang bị cờ thì "Cần xem lại", không có nguồn thì "Không có trong tài liệu", bị lớp luật chặn thì "Đã từ chối theo quy định". AI không được tự khai độ chắc.

**Đã cân nhắc và loại:**
- *Thanh phần trăm ("chắc 87%")*: loại vì giả chính xác. Hệ thống không có con số nào đứng sau, và học viên lúc 22:40 sẽ đọc 87% thành "đúng rồi". Ở K1, câu sai của §3.3 vẫn có nguồn rõ ràng nên thanh phần trăm sẽ hiện cao đúng lúc cần nghi ngờ nhất.
- *Để AI tự viết "mình khá chắc"*: loại vì chính AI là thứ có thể sai. K1 là ca AI trích đúng mục nhưng mục đó sai.
- *Chỉ dùng màu*: loại vì khi chiếu lên máy chiếu hoặc với người mù màu thì vàng và xanh khó phân biệt. Mỗi trạng thái có thêm biểu tượng và chữ.

### Quyết định: điều khiển mức tự chủ

**Chọn: mỗi mức tự chủ có một hình dạng riêng trên màn hình.** Việc AI tự làm thì hiện thành dòng sự kiện nhỏ kèm đường hoàn tác (Xoá nháp, giảng viên đóng ticket). Việc cần duyệt thì hiện thành thẻ có nút Xác nhận ở cột "Việc đang chờ bạn", chưa bấm thì chưa có gì xảy ra. Việc bị cấm thì không có nút, chỉ có một khung chữ nói rõ là không khả dụng và vì sao.

**Đã cân nhắc và loại:**
- *Hộp thoại "Bạn có chắc không?" cho mọi việc*: loại vì học viên sẽ bấm Có theo quán tính. Chỉ `chuyen_TA` mới cần xác nhận, và thẻ xác nhận phải hiện đúng thông tin làm đổi quyết định (giờ TA trả lời, sau hạn nộp).
- *Nút "Xem đáp án" bị làm mờ*: loại vì nút mờ vẫn là lời hứa "sẽ có lúc bấm được" và mời học viên tìm cách mở. Bài đang mở thì không có nút nào cả.
- *Thanh trượt cho học viên tự chọn mức tự chủ*: loại vì người muốn lấy đáp án chính là người cầm thanh trượt.
