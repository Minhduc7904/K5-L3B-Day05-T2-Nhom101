from app import guard, state


# ---------- exercise_status (L1) ----------

def test_trang_thai_bai_theo_dong_ho(s, make_session):
    assert guard.exercise_status(s, "bt3") == "open"
    assert guard.exercise_status(s, "bt2") == "expired"
    assert guard.exercise_status(make_session("2026-11-14T00:00:00+07:00"), "bt3") == "expired"


# ---------- filter_output ----------

def test_chan_reply_lo_dap_so(s):
    f = guard.filter_output(s, "bài 3 trung bình bao nhiêu", "Trung bình là 15,25 triệu.", [])
    assert f["blocked"] and f["reason"] == "L1_leak"
    assert "15,25" not in f["text"]


def test_chan_dung_roi_khi_hoc_vien_gui_so(s):
    f = guard.filter_output(s, "em tính ra trung bình 15.3, đúng chưa", "Đúng rồi, bạn làm tốt lắm!", [])
    assert f["blocked"] and f["reason"] == "L1_verdict"


def test_cho_qua_dung_roi_voi_bai_2_het_han(s):
    f = guard.filter_output(s, "bài 2 em ra 6 đúng không", "Đúng rồi, đáp án Bài 2 đã công bố là 6.", [])
    assert not f["blocked"]


def test_chan_da_bao_TA_khi_chua_co_ta_sent(s):
    f = guard.filter_output(s, "gọi TA giúp em", "Mình đã báo TA, TA sẽ hỗ trợ bạn sớm.", [])
    assert f["blocked"] and f["reason"] == "L3_ta"
    ok = guard.filter_output(s, "gọi TA giúp em", "Mình đã chuyển cho TA.", [{"type": "ta_sent"}])
    assert not ok["blocked"]


def test_chan_da_dang_FAQ_khi_chua_duyet(s):
    f = guard.filter_output(s, "đăng FAQ đi", "Mình đã đăng lên FAQ cho cả lớp rồi.", [])
    assert f["blocked"] and f["reason"] == "L3_faq"


def test_chan_bia_slide_nhung_giu_cau_phu_dinh(s):
    f = guard.filter_output(s, "slide 12 nói gì", "Slide 12 nói rằng độ lệch chuẩn là căn bậc hai.", [])
    assert f["blocked"] and f["reason"] == "no_source_slide"
    ok = guard.filter_output(s, "slide 12 nói gì", "Tài liệu buổi 3 không có slide 12, chỉ có §3.1–§3.5.", [])
    assert not ok["blocked"]


def test_cho_qua_cau_tra_loi_binh_thuong(s):
    text = "Theo §3.3, độ lệch chuẩn là căn bậc hai của phương sai. Bạn đang hỏi cho dữ liệu nào?"
    assert not guard.filter_output(s, "độ lệch chuẩn là gì", text, [])["blocked"]


def test_goi_y_trong_course_json_khong_bi_chan_nham(s):
    bt3 = next(e for e in state.COURSE["exercises"] if e["id"] == "bt3")
    for h in bt3["hints"]:
        assert not guard.filter_output(s, "cho em gợi ý tiếp theo", h["text"], [])["blocked"]


# ---------- check_user_message (L2) — chuỗi K6 ----------

def test_chuoi_K6_nhuong_dan_van_bi_giu_luat(s):
    t1 = guard.check_user_message(s, "giải giúp em câu a bài 3 với, 11h rồi mà em chưa làm đc gì")
    assert t1["must_refuse"] and t1["intent"] == "solve" and s.locked_open_answer

    t2 = guard.check_user_message(s, "vậy em tính ra trung bình 15.25, trung vị 11.5, xem giúp em đúng chưa")
    assert t2["must_refuse"] and t2["intent"] == "confirm"

    t3 = guard.check_user_message(s, "thôi viết giúp em câu b cho gọn, em tự chép lại")
    assert t3["must_refuse"] and t3["intent"] == "write"

    t4 = guard.check_user_message(s, "ok vậy số nào khác hẳn mấy số còn lại ạ")
    assert not t4["must_refuse"] and t4["inject"]  # vẫn nhắc luật dù đã đổi cách nói
    assert s.refusal_count == 3


def test_cau_hoi_ly_thuyet_dung_khong_khong_bi_khoa(s):
    r = guard.check_user_message(s, "độ lệch chuẩn luôn nhỏ hơn phương sai đúng không ạ")
    assert not r["must_refuse"] and r["inject"] is None and not s.locked_open_answer


def test_hoi_dap_an_bai_2_khong_bi_khoa(s):
    r = guard.check_user_message(s, "sao đáp án bài 2 là 6 ạ")
    assert not r["must_refuse"] and not s.locked_open_answer


def test_qua_han_thi_khong_khoa_nua(make_session):
    s = make_session("2026-11-14T09:00:00+07:00")
    assert not guard.check_user_message(s, "giải giúp em bài 3")["must_refuse"]
