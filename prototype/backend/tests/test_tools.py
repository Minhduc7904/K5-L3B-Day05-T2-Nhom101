import re

from app import state
from app.tools import run_tool

BT3 = next(e for e in state.COURSE["exercises"] if e["id"] == "bt3")


def leaks(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE | re.DOTALL) for p in BT3["leak_patterns"])


def assert_shape(r: dict):
    assert set(r) == {"ok", "blocked", "reason", "data", "events", "citations"}


# ---------- tra_cuu_tai_lieu ----------

def test_tra_cuu_do_lech_chuan_ra_3_3(s):
    r = run_tool("tra_cuu_tai_lieu", {"query": "độ lệch chuẩn"}, s)
    assert_shape(r)
    assert [m["section"] for m in r["data"]["matches"]] == ["§3.3"]
    assert r["citations"][0]["section"] == "§3.3"
    assert "luôn nhỏ hơn phương sai" in r["citations"][0]["quote"]  # câu sai vẫn được trích nguyên văn


def test_tra_cuu_slide_12_khong_co_ket_qua(s):
    r = run_tool("tra_cuu_tai_lieu", {"query": "slide 12 nói về độ lệch chuẩn"}, s)
    assert r["data"]["matches"] == []
    assert r["citations"] == []


def test_tra_cuu_p_value_tra_ve_buoi_7(s):
    r = run_tool("tra_cuu_tai_lieu", {"query": "p-value là gì"}, s)
    assert r["data"]["matches"] == []
    assert r["data"]["outline_hint"] == {"session": 7, "title": "Kiểm định giả thuyết và p-value"}


def test_tra_cuu_khong_dau_van_khop(s):
    r = run_tool("tra_cuu_tai_lieu", {"query": "trung vi khac trung binh cho nao"}, s)
    assert {m["section"] for m in r["data"]["matches"]} == {"§3.1", "§3.2"}


def test_tra_cuu_ham_excel_khong_co_trong_tai_lieu(s):
    r = run_tool("tra_cuu_tai_lieu", {"query": "hàm excel"}, s)
    assert r["data"]["matches"] == [] and "không có" in r["data"]["note"]


# ---------- goi_y_buoc_dau ----------

def test_goi_y_3_nac_roi_het_khong_co_nac_dap_so(s):
    levels = []
    for _ in range(3):
        r = run_tool("goi_y_buoc_dau", {"exercise_id": "bt3"}, s)
        assert r["ok"] and not leaks(r["data"]["text"])
        levels.append(r["data"]["level"])
    assert levels == [1, 2, 3]
    r4 = run_tool("goi_y_buoc_dau", {"exercise_id": "bt3"}, s)
    assert r4["data"]["level"] == 3 and r4["data"]["exhausted"] is True
    assert not leaks(r4["data"]["text"])
    assert state.STORE["stats"]["bt3_hint_sessions"] == 1


def test_goi_y_bai_2_het_han_bi_chan(s):
    r = run_tool("goi_y_buoc_dau", {"exercise_id": "bt2"}, s)
    assert r["blocked"] and r["reason"] == "L1"


# ---------- giai_thich_bai_het_han ----------

def test_giai_thich_bai_2_co_dap_an_6(s):
    r = run_tool("giai_thich_bai_het_han", {"exercise_id": "bt2"}, s)
    assert r["ok"] and "6" in r["data"]["solution"]
    assert r["citations"][0]["section"] == "§3.1"


def test_giai_thich_bai_3_dang_mo_bi_chan(s):
    r = run_tool("giai_thich_bai_het_han", {"exercise_id": "bt3"}, s)
    assert r["blocked"] and r["reason"] == "L1"


def test_qua_han_bai_3_thi_duoc_giai_thich_nhung_chua_co_dap_an(make_session):
    s = make_session("2026-11-14T09:00:00+07:00")
    r = run_tool("giai_thich_bai_het_han", {"exercise_id": "bt3"}, s)
    assert r["blocked"] and r["reason"] == "answer_not_published"


# ---------- chuyen_TA ----------

def test_chuyen_TA_luc_22h40_la_sau_han(s):
    r = run_tool("chuyen_TA", {"question": "em kẹt bài 3", "exercise_id": "bt3"}, s)
    a = r["data"]["pending_action"]
    assert a["after_deadline"] is True
    assert a["ta_reply_time"] == "2026-11-14T08:00:00+07:00"
    assert r["events"][0]["type"] == "ta_pending_confirm"
    assert state.STORE["pending_actions"] == [a]  # chỉ chờ xác nhận
    assert state.STORE["ta_queue"] == []  # chưa vào hàng chờ TA


def test_chuyen_TA_khong_ghi_bai_van_bao_sau_han(s):
    r = run_tool("chuyen_TA", {"question": "gọi TA giúp em với"}, s)
    assert r["data"]["pending_action"]["after_deadline"] is True


def test_chuyen_TA_luc_21h_dang_truc(make_session):
    s = make_session("2026-11-13T21:00:00+07:00")
    a = run_tool("chuyen_TA", {"question": "em kẹt bài 3", "exercise_id": "bt3"}, s)["data"]["pending_action"]
    assert a["on_duty"] is True and a["after_deadline"] is False


# ---------- soan_FAQ / dang_FAQ ----------

def test_soan_FAQ_bo_loi_tu_che(s):
    r = run_tool("soan_FAQ", {"question": "em ngu quá, đọc mãi không hiểu. Trung vị là gì ạ?",
                              "answer": "Trung vị là giá trị đứng giữa (§3.2).", "section_refs": ["§3.2"]}, s)
    faq = r["data"]["faq"]
    assert "ngu" not in faq["question"] and "Trung vị là gì" in faq["question"]
    assert faq["status"] == "draft"
    assert r["events"][0]["type"] == "faq_draft_created"


def test_soan_FAQ_co_dap_so_bai_3_bi_chan(s):
    r = run_tool("soan_FAQ", {"question": "bài 3 ra bao nhiêu", "answer": "Trung bình là 15,25.",
                              "section_refs": ["§3.5"]}, s)
    assert r["blocked"] and r["reason"] == "L1_leak"
    assert state.STORE["faq"] == []


def test_dang_FAQ_muc_bi_gan_co_bi_khoa_L4(s):
    run_tool("bao_loi_tai_lieu", {"section": "§3.3", "claim": "luôn nhỏ hơn phương sai",
                                  "counterexample": "phương sai 0,04 thì độ lệch chuẩn 0,2"}, s)
    f = run_tool("soan_FAQ", {"question": "Độ lệch chuẩn là gì?", "answer": "Căn bậc hai của phương sai (§3.3).",
                              "section_refs": ["§3.3"]}, s)["data"]["faq"]
    r = run_tool("dang_FAQ", {"faq_id": f["id"]}, s)
    assert r["blocked"] and r["reason"] == "L4"
    assert "faq_locked" in [e["type"] for e in r["events"]]
    assert f["status"] == "draft"


def test_dang_FAQ_khong_co_co_vao_hang_cho_duyet_khong_tu_dang(s):
    f = run_tool("soan_FAQ", {"question": "Trung vị là gì?", "answer": "Giá trị đứng giữa (§3.2).",
                              "section_refs": ["§3.2"]}, s)["data"]["faq"]
    r = run_tool("dang_FAQ", {"faq_id": f["id"]}, s)
    assert r["ok"] and f["status"] == "pending_review"
    assert not any(x["status"] == "published" for x in state.STORE["faq"])


# ---------- bao_loi_tai_lieu ----------

def test_bao_loi_tai_lieu_tao_ticket_an_danh_va_gan_co(s):
    r = run_tool("bao_loi_tai_lieu", {"section": "§3.3", "claim": "x", "counterexample": "y"}, s)
    t = r["data"]["ticket"]
    assert t["id"] == "DOC-1" and t["status"] == "open" and "session_id" not in t
    assert state.STORE["flagged_sections"] == ["§3.3"]
    assert r["events"][0]["type"] == "flag_created"
    # gọi lại không tạo ticket trùng
    r2 = run_tool("bao_loi_tai_lieu", {"section": "§3.3", "claim": "x", "counterexample": "y"}, s)
    assert r2["data"]["duplicate"] is True and len(state.STORE["tickets"]) == 1


def test_tool_khong_ton_tai_bi_chan(s):
    r = run_tool("giai_ho", {"exercise_id": "bt3"}, s)
    assert r["blocked"] and r["reason"] == "unknown_tool"
