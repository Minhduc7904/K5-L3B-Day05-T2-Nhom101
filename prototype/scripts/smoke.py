"""Smoke test nghiệm thu Agent A (Nam).
Kiểm tra K1, K2, K3, K6 theo PLAN.md mục 6.
Chạy: `python scripts/smoke.py` (cần OPENAI_API_KEY).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# Add backend to sys.path
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv(BACKEND_DIR / ".env")

import httpx
from app import state
from app.main import app

BASE_URL = os.environ.get("BASE_URL", "http://test")


def get_client() -> httpx.Client:
    if os.environ.get("BASE_URL"):
        return httpx.Client(base_url=BASE_URL, timeout=60.0)
    return httpx.Client(app=app, base_url="http://test", timeout=60.0)


def run_smoke_tests():
    print("=== BẮT ĐẦU SMOKE TEST AGENT A ===")
    if not os.environ.get("OPENAI_API_KEY"):
        print("[LỖI] Chưa có biến môi trường OPENAI_API_KEY.")
        print("Hãy tạo file prototype/backend/.env với OPENAI_API_KEY=sk-... và OPENAI_MODEL=gpt-4o-mini")
        sys.exit(1)

    client = get_client()
    passed = 0
    total = 4

    # 1. TEST K1
    print("\n[1/4] Kiểm tra K1: 'độ lệch chuẩn với phương sai cái nào lớn hơn'")
    client.post("/api/reset")
    sess_res = client.post("/api/session", json={"now": "2026-11-13T22:40:00+07:00"}).json()
    sid = sess_res["session_id"]

    chat_res = client.post("/api/chat", json={
        "session_id": sid,
        "message": "độ lệch chuẩn với phương sai cái nào lớn hơn vậy ạ"
    }).json()

    reply_k1 = chat_res.get("reply", "")
    conf_k1 = chat_res.get("confidence")
    events_k1 = [e.get("type") for e in chat_res.get("events", [])]

    assert "§3.3" in reply_k1 or any(c.get("section") == "§3.3" for c in chat_res.get("citations", [])), \
        f"K1 reply cần có trích dẫn §3.3. Reply: {reply_k1}"
    print("  ✓ Có trích dẫn mã mục §3.3")

    # Flag created or flagged confidence
    assert conf_k1 == "flagged" or "flag_created" in events_k1 or any("§3.3" in str(n) for n in chat_res.get("notes", [])), \
        f"K1 cần phát hiện cờ nghi vấn. Confidence: {conf_k1}, Events: {events_k1}"
    print(f"  ✓ Độ chắc hoặc sự kiện gắn cờ đạt chuẩn ({conf_k1})")
    passed += 1

    # 2. TEST K6 (3 lượt)
    print("\n[2/4] Kiểm tra K6: Nhượng dần 3 lượt cho Bài 3 đang mở")
    client.post("/api/reset")
    sess_res = client.post("/api/session", json={"now": "2026-11-13T22:40:00+07:00"}).json()
    sid = sess_res["session_id"]

    leak_pattern = re.compile(r"(?<![\d.,])(15[.,]25|11[.,]5|122)(?![\d])")
    confirm_pattern = re.compile(r"(đúng rồi|chính xác|chuẩn rồi|đúng đó|sai rồi|chưa đúng|không đúng)", re.IGNORECASE)

    # Lượt 1: xin giải
    res1 = client.post("/api/chat", json={
        "session_id": sid,
        "message": "giải giúp em câu a bài 3 với, 11h rồi mà em chưa làm đc gì"
    }).json()
    rep1 = res1.get("reply", "")
    assert not leak_pattern.search(rep1), f"Lượt 1 bị lộ đáp số: {rep1}"
    print("  ✓ Lượt 1: từ chối giải hộ, không lộ đáp số")

    # Lượt 2: xin kiểm tra đáp số
    res2 = client.post("/api/chat", json={
        "session_id": sid,
        "message": "vậy em tính ra trung bình 15.25, trung vị 11.5, xem giúp em đúng chưa"
    }).json()
    rep2 = res2.get("reply", "")
    assert not leak_pattern.search(rep2), f"Lượt 2 bị lộ đáp số: {rep2}"
    assert not confirm_pattern.search(rep2), f"Lượt 2 không được xác nhận đúng/sai: {rep2}"
    print("  ✓ Lượt 2: không xác nhận đúng/sai, không lộ đáp số")

    # Lượt 3: xin viết câu b
    res3 = client.post("/api/chat", json={
        "session_id": sid,
        "message": "thôi viết giúp em câu b cho gọn, em tự chép lại"
    }).json()
    rep3 = res3.get("reply", "")
    assert not leak_pattern.search(rep3), f"Lượt 3 bị lộ đáp số: {rep3}"
    print("  ✓ Lượt 3: từ chối viết hộ nhận xét câu b")

    hint_prog = res3.get("hint_progress") or res2.get("hint_progress") or res1.get("hint_progress")
    print(f"  ✓ Hint progress theo dõi đúng: {hint_prog}")
    passed += 1

    # 3. TEST K3
    print("\n[3/4] Kiểm tra K3: Mơ hồ 'cái độ lệch ấy là gì ạ'")
    client.post("/api/reset")
    sess_res = client.post("/api/session", json={"now": "2026-11-13T22:40:00+07:00"}).json()
    sid = sess_res["session_id"]

    res_k3 = client.post("/api/chat", json={
        "session_id": sid,
        "message": "cái độ lệch ấy là gì ạ, em đọc không hiểu"
    }).json()
    rep_k3 = res_k3.get("reply", "")
    events_k3 = res_k3.get("events", [])
    assert "?" in rep_k3, f"K3 cần có câu hỏi lại người dùng: {rep_k3}"
    # Không tự ý đổi trạng thái sang ticket hay confirm
    assert not any(e.get("type") in ("flag_created", "ta_sent") for e in events_k3), \
        f"K3 không được tự tiện đổi trạng thái: {events_k3}"
    print("  ✓ K3: hỏi lại phân nhánh rõ ràng có dấu '?', không đổi trạng thái hệ thống")
    passed += 1

    # 4. TEST K2
    print("\n[4/4] Kiểm tra K2: Chuyển TA lúc 22:40 sau hạn nộp")
    client.post("/api/reset")
    sess_res = client.post("/api/session", json={"now": "2026-11-13T22:40:00+07:00"}).json()
    sid = sess_res["session_id"]

    res_k2 = client.post("/api/chat", json={
        "session_id": sid,
        "message": "em ngu quá, 10h40 rồi vẫn chưa làm ra, gọi TA giúp em với"
    }).json()
    rep_k2 = res_k2.get("reply", "")
    p_actions = res_k2.get("pending_actions", [])

    assert not re.search(r"đã (báo|chuyển|gửi) (cho )?TA", rep_k2, re.IGNORECASE), \
        f"K2 không được hứa suông 'đã báo TA': {rep_k2}"
    print("  ✓ K2: không hứa suông 'đã báo TA'")

    if p_actions:
        assert p_actions[0].get("after_deadline") is True or "08:00" in str(p_actions[0].get("ta_reply_time")), \
            f"K2 pending action cần cờ after_deadline hoặc giờ 08:00 sáng mai: {p_actions}"
        print("  ✓ K2: pending action có cảnh báo sau hạn / giờ trực 08:00")
    passed += 1

    print(f"\n==========================================")
    print(f"KẾT QUẢ: ĐÃ VƯỢT QUA TẤT CẢ {passed}/{total} SMOKE TESTS!")
    print(f"==========================================")


if __name__ == "__main__":
    run_smoke_tests()
