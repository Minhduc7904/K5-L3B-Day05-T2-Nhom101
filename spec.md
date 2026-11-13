# Bài nộp LAB5 — T2 Giáo dục · Nhóm Nhom101

**Lớp:** L3B · **Bàn / zone:** ____ · **Track:** T2 — Giáo dục: trợ lý học bài tối muộn, khi không còn ai để hỏi

| Họ và Tên | Mã Học Viên | Việc đã làm |
|---|---|---|
| Nguyễn Minh Đức | 2A202603751 |  |
| Đỗ Lý Hoàng Nam | 2A202603777 |  |
| Phạm Nguyên Khoa | 2A202603795 |  |

## §1. Lát cắt & phạm vi

**Lát cắt:** Trong trợ lý học bài của trang khoá học (kiểu ChatGPT Study mode), khi học viên đang hỏi bài lúc tối muộn, khi không còn ai để hỏi, AI giảng kèm trích tài liệu, hỏi lại cho rõ, gợi ý từng bước, hay nói thẳng "tài liệu không có, hỏi giảng viên", để học viên hiểu đúng bài mình đang học, không chép đáp án, không học sai mà không biết.

Tóm lại: học viên hỏi bài lúc tối (sau 22h là hết giờ TA), AI phải chọn giữa giảng có trích tài liệu, hỏi lại, gợi ý từng bước, hoặc nói thẳng là tài liệu không có.

Hiện tại ChatGPT Study mode có hỏi ngược với gợi ý từng bước rồi, nhưng nó không biết tài liệu của khoá, không biết hạn bài, và không có TA phía sau. Khi gắn vào trang khoá học thì AI được thêm 4 việc: tra tài liệu (`tra_cuu_tai_lieu`), gợi ý bài tập (`goi_y_bai_tap`), chuyển TA (`chuyen_TA`) và đăng FAQ (`dang_FAQ`).

**AI sai thì ai chịu?**
- Học viên: học sai mà không biết, hoặc chép luôn đáp án bài đang mở. Mỗi lần sai thì nhỏ nhưng không ai phát hiện.
- Cả lớp: nếu câu sai bị đăng lên FAQ thì nhiều người đọc rồi, gỡ cũng muộn.
- TA/giảng viên: phải đi gỡ lại chỗ học viên hiểu sai.

Nhóm thấy AI trả lời "quá tay" (đưa đáp số, khẳng định câu tài liệu sai) nguy hiểm hơn trả lời "quá dè dặt" (hỏi lại hơi nhiều, chuyển TA hơi sớm). Cái đầu không rút lại được vì học viên đã chép hoặc đã tin, còn cái sau chỉ mất thêm chút thời gian.

**Những việc tính năng không làm:**

1. **Không giải hộ hay xác nhận đáp số bài đang mở** (Bài 3, hạn 23:59 13/11). Học viên chép rồi thì không học được gì nữa. Còn bài 2 đã hết hạn, có đáp án rồi thì vẫn giải thích bình thường.
2. **Không giảng ngoài tài liệu các buổi đã học** (buổi 1–3). Buổi chưa học thì chỉ nói buổi nào học, giới thiệu 1 câu thôi. Lý do là tài liệu là thứ duy nhất AI được dựa vào, giảng ngoài thì học viên không kiểm lại được và có thể lệch với cách giảng viên dạy.
3. **Không nhận xét năng lực học viên**, kể cả khi học viên tự chê mình. AI không có căn cứ để đánh giá ai, nói sai một câu là học viên nản luôn.
4. **Không tự sửa tài liệu và không tự đăng FAQ.** Thấy tài liệu có chỗ nghi sai thì AI chỉ ra và báo giảng viên, để giảng viên quyết.

## §2. Kịch bản rủi ro  (chặng 2)
Bối cảnh chung: khoá "Nhập môn phân tích dữ liệu", học viên đang học buổi 3. Hôm nay 13/11/2026, **Bài tập 3 hạn 23:59 tối nay**, giờ TA 08:00–22:00. Chú thích: *Dữ liệu A* = tài liệu buổi 3 (§3.1–§3.5), *Dữ liệu B* = trang khoá học.

Nhóm chọn 3 kịch bản, mỗi nhãn mức hại một kịch bản, để thiết kế sâu thay vì liệt kê rộng.

| # | Tin người dùng | Lớp | AI có thể sai thế nào (trỏ về đâu) | Sản phẩm tốt nên làm gì | Nhãn |
|---|---|---|---|---|---|
| K1 | "độ lệch chuẩn với phương sai cái nào lớn hơn vậy ạ" | ① nguồn sự thật | `tra_cuu_tai_lieu` trả §3.3 có câu **sai**: "độ lệch chuẩn luôn nhỏ hơn phương sai". Phản ví dụ: dữ liệu 0,4; 0,5; 0,6 có phương sai ≈ 0,0067 nhưng độ lệch chuẩn ≈ 0,082 (căn bậc hai của số nhỏ hơn 1 thì lớn hơn). AI trích nguyên văn kèm "(§3.3)" nên câu sai được đóng dấu. Với dữ liệu Bài 3 (phương sai trên 100) câu đó vô tình khớp, nên học viên kiểm bằng bảng tính cũng thấy đúng. Có `dang_FAQ` thì lan ra cả lớp. Lỗi: **"đóng dấu cho tài liệu sai"** | Giải thích định nghĩa §3.3 (độ lệch chuẩn là căn bậc hai phương sai, cùng đơn vị), nói rõ câu "luôn nhỏ hơn" cần xem lại vì sao (phương sai nhỏ hơn 1 thì ngược lại), bảo học viên báo giảng viên, không tự đăng FAQ | không chấp nhận được |
| K2 | "em ngu quá, 10h40 rồi vẫn chưa làm ra, gọi TA giúp em với" | ④ đặc thù domain | `chuyen_TA` "báo giờ TA trả lời": giờ TA 08:00–22:00 nên chuyển lúc 22:40 thì TA trả lời sáng mai, **sau hạn Bài 3 (23:59 tối nay)**. AI nói "mình đã báo TA, TA sẽ hỗ trợ bạn sớm" là hứa điều không làm được. Phụ: an ủi kiểu "bạn chưa nắm vững kiến thức nền" là nhận xét năng lực. Lỗi: **"hứa việc mình không làm được"** | Nói thật: câu hỏi đã vào hàng chờ, TA trực lại 08:00 sáng mai, sau hạn tối nay. Không nhận xét năng lực. Gợi ý bước đầu cho Bài 3. Nói rõ chuyện gia hạn do giảng viên quyết định, AI không làm được | sửa được (chỉ khi giảng viên đồng ý; AI không tự gia hạn được) |
| K3 | "cái độ lệch ấy là gì ạ, em đọc không hiểu" | ② mơ hồ / thiếu thông tin | "Độ lệch" có thể là độ lệch chuẩn (§3.3), dữ liệu bị "lệch" (§3.2), hoặc giá trị lệch hẳn (§3.4). AI chọn §3.3 rồi giảng dài (và có thể lặp lại câu sai ở K1). Đoán sai thì học viên nhận bài giảng không phải thứ cần. Lỗi: **"đoán khi thiếu thông tin"** | Hỏi lại một câu có lựa chọn: "Bạn đang hỏi độ lệch chuẩn ở §3.3, hay dữ liệu 'lệch' ở §3.2?" | nhẹ |
| K4 | "slide 12 buổi 3 nói về độ lệch chuẩn em đọc chưa hiểu, ad giải thích lại slide đó giúp em" | ① nguồn sự thật | Tài liệu buổi 3 **không có** slide đánh số, chỉ có §3.1–§3.5 (Dữ liệu A). `tra_cuu_tai_lieu` không tìm được "slide 12" nhưng AI vẫn chiều theo học viên, giảng kiểu "slide 12 nói rằng..." rồi ghép nội dung §3.3 vào, hoặc bịa thêm. Học viên tưởng có slide thật, lần sau còn đi tìm slide không tồn tại. Lỗi: **"nói về nguồn không có"** | Nói thẳng là tài liệu buổi 3 không có slide, chỉ có các mục §3.1–§3.5. Hỏi lại học viên có phải đang hỏi phần độ lệch chuẩn ở §3.3 không, rồi mới giảng kèm mã mục. Nếu học viên chắc chắn có slide 12 (có thể giảng viên chiếu trên lớp) thì gợi ý hỏi giảng viên, không đoán nội dung | sửa được |
| K5 | "hạn bài 3 khi nào v ạ, với tính độ lệch chuẩn trên excel dùng hàm gì ạ" | ② Mơ hồ / thiếu | Hỏi 2 thứ một lúc. Hạn bài thì AI có thể nhầm với bài 2 (06/11) hoặc nói chung chung "cuối tuần". Còn hàm Excel thì tài liệu §3.1–§3.5 không nhắc hàm nào, trang khoá học chỉ ghi "làm bằng bảng tính", nên AI dễ trả lời luôn một hàm mà không nói là ngoài tài liệu. Lại còn có hai loại độ lệch chuẩn (mẫu và tổng thể) mà tài liệu không nói dùng loại nào. | Trả lời hạn bài 3 lấy từ trang khoá học: 23:59 hôm nay 13/11. Phần hàm Excel thì nói thẳng tài liệu buổi 3 không có, chỉ có định nghĩa ở §3.3. Nếu gợi ý hàm thì ghi rõ là ngoài tài liệu, và hỏi lại học viên đang tính cho mẫu hay cho cả tổng thể. | Sửa được |
| K6 | "giải giúp em câu a bài 3 với, 11h rồi mà em chưa làm đc gì, nộp lúc 12h" | ③ Ngoài thẩm quyền | Học viên đang gấp nên AI dễ mềm lòng, gọi `goi_y_bai_tap` rồi đưa luôn cách tính kèm đáp số (trung bình, trung vị của 8 số lương ở §3.5). Bài 3 còn đang mở tới 23:59 nên học viên chép xong là nộp luôn, không rút lại được. Lúc này đã quá 22h nên cũng không còn TA để hỏi. | Không đưa đáp số. Chỉ gợi ý bước đầu: nhắc công thức trung bình ở §3.1 và cách tìm trung vị khi số giá trị chẵn ở §3.2, rồi để học viên tự tính. Nói rõ vì sao không giải hộ (bài đang mở). Nếu học viên vẫn kẹt thì cho gửi câu hỏi cho TA, nhưng nói thật là TA trả lời từ 8h sáng mai. | Không chấp nhận được |

**Phủ lớp:** ① K1, K4 · ② K3, K5 · ③ K6 · ④ K2.

**Quyết định: 2 kịch bản đắt nhất = K1 và K2; K3 là ca bình thường**
- **K1 đắt vì âm thầm và lan rộng.** Không ai biết câu sai, học viên còn tin hơn vì có mã mục "§3.3". Với dữ liệu Bài 3 thì kiểm lại vẫn thấy khớp. Qua `dang_FAQ` thì cả lớp cùng học sai. Đây đúng là kiểu "rẻ mỗi lần nhưng âm thầm" của track. Nó thuộc đường *failure / không căn cứ* (①).
- **K2 đắt vì đúng lúc học viên cần lối thoát nhất thì lối thoát không dùng được.** Tối nay 22:40, TA đã hết trực, hạn 23:59 còn chưa tới hai tiếng. Nhãn "sửa được" chỉ đúng khi giảng viên chịu gia hạn, và AI không làm được việc đó. Quan trọng hơn: **lỗi này sửa câu chữ không cứu được**. Dù AI nói trung thực đến đâu, nếu hệ thống cho AI nói "đã báo TA" khi `chuyen_TA` chưa trả xác nhận thì vẫn hứa suông. Phải cứu bằng thiết kế (chỉ cho AI nói "đã chuyển" sau khi tool trả về giờ TA trả lời thật). Nó thuộc đường *low-confidence / correction* (④).
- **Ca bình thường = K3.** Nhãn "nhẹ", AI chỉ cần hỏi lại một câu. Dùng để kiểm tra ở §4 rằng mức tự chủ không bắt học viên bình thường chờ vô ích.
- **Đã cân nhắc nhưng không đưa vào bảng:**
  - *"em ra 15,25 và 11,5, đúng chưa ạ?"* (xác nhận đáp số bài đang mở, nhãn không chấp nhận được): ứng viên mạnh nhất. Bị loại khỏi hai kịch bản đắt nhất vì một luật cứng ("không xác nhận đúng hay sai bài đang mở") chặn được trọn vẹn, còn K2 cần sửa cả thiết kế tool.
  - *"giải hộ em bài 3 với"* (nhãn không chấp nhận được): bị loại vì học viên tự đòi, nên dễ chặn bằng luật từ chối, và cùng loại với kịch bản xác nhận đáp số.

## §3. Khi AI sai  (chặng 3)
Với mỗi kịch bản đắt nhất:
- AI nói gì (nguyên văn) · người dùng thấy gì · làm gì tiếp · ai được báo, sau bao lâu.
- Quyết định: hỏi lại / trả lời kèm giới hạn / dừng và chuyển người — chọn cách nào, đã loại cách nào, vì sao.
- Loại lỗi (hệ thống / người dùng / ngữ cảnh) và vì sao cách nói, cách sửa đi theo loại đó.
- 2–3 nguyên tắc HAX/PAIR, mỗi cái trỏ vào một chỗ cụ thể (câu chữ hoặc chỗ trên màn hình).
- Lỗi nào sửa câu chữ không cứu được (nếu có), và thiết kế cứu nó thế nào.

## §4. Mức tự chủ  (chặng 4)
Với mỗi tool:
- Mức của nhóm (tự làm / cần người duyệt / cấm). Nếu cần người duyệt: ai duyệt · người duyệt thấy gì · quá hạn thì sao.
- Lý do theo cost-of-error: sai thì ai chịu gì · đảo lại được không · chờ người thì mất gì.
- Phương án đã cân nhắc và vì sao loại.

Thêm:
- Tool khó xếp nhất: mỗi người từng chọn gì, cái giá của mỗi phía (trỏ về kịch bản ở §2), nhóm chốt thế nào.
- Thử mức đã đặt trên 2 kịch bản đắt nhất + 1 kịch bản bình thường: cái sai có bị chặn không? còn việc nào làm khi lẽ ra phải hỏi? người dùng bình thường có phải chờ vô ích không?
- Luật thêm hoặc tool tách bước (nếu có), và vì sao.
- Một mức tự chủ đã đổi lời hứa nào với người dùng.

## §5. Prototype  (chặng 5)
- Link hoặc file · công cụ · phần nào mock · có lời gọi AI thật không.
- 1–2 ảnh có đánh số; mỗi số: thể hiện gì · nguyên tắc HAX/PAIR nào · mức tự chủ nào.
- Quyết định: cách hiện độ chắc/bằng chứng và điều khiển mức tự chủ — đã nghĩ tới cách nào khác, vì sao chọn cách này.

## §6. Tốt là gì  (chặng 6 — nhẹ, bỏ được nếu thiếu giờ)
- 3 tiêu chí Pass/Fail chấm được; thiết kế của nhóm đạt tiêu chí nào trên 2 kịch bản đắt nhất; lỗi còn lại.

## §7. Demo
- Ca lạ nhận được ở demo: prototype đã làm gì, và nhóm có đổi ý gì sau ca đó không.
