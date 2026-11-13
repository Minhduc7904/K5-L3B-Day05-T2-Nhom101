"""STUB do Bước 0 đặt. Agent B (Khoa) thay thân hàm; KHÔNG đổi chữ ký / tên tool / schema.

run_tool trả: {"ok", "blocked", "reason", "data", "events", "citations"}
"""
from __future__ import annotations


def _fn(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


_S = {"type": "string"}

TOOL_SCHEMAS: list[dict] = [
    _fn("tra_cuu_tai_lieu",
        "Tìm trong tài liệu buổi 1–3 của khoá, trả đoạn kèm mã mục (§3.x). Chỉ đọc.",
        {"query": {**_S, "description": "Từ khoá hoặc câu hỏi cần tra"}}, ["query"]),
    _fn("goi_y_buoc_dau",
        "Gợi ý làm bài tập ĐANG MỞ theo từng nấc (1 công thức, 2 tự kiểm, 3 câu hỏi gợi mở). Không có nấc đáp số.",
        {"exercise_id": {**_S, "description": "Ví dụ bt3"}}, ["exercise_id"]),
    _fn("giai_thich_bai_het_han",
        "Giải thích đầy đủ bài tập ĐÃ HẾT HẠN và đã có đáp án công bố (ví dụ bt2).",
        {"exercise_id": {**_S, "description": "Ví dụ bt2"}}, ["exercise_id"]),
    _fn("chuyen_TA",
        "Soạn câu hỏi chuyển cho TA. Chỉ soạn chờ học viên bấm xác nhận, chưa gửi. Trả giờ TA trả lời thật và cờ sau hạn.",
        {"question": _S, "exercise_id": {**_S, "description": "Tuỳ chọn, ví dụ bt3"}}, ["question"]),
    _fn("soan_FAQ",
        "Soạn BẢN NHÁP FAQ ẩn danh (bỏ tên, bỏ lời tự chê, không chứa gợi ý bài đang mở). Không đăng.",
        {"question": _S, "answer": _S,
         "section_refs": {"type": "array", "items": _S, "description": "Mã mục được trích, ví dụ [\"§3.2\"]"}},
        ["question", "answer", "section_refs"]),
    _fn("dang_FAQ",
        "Đưa bản nháp FAQ vào hàng chờ giảng viên/TA duyệt. Không bao giờ tự đăng. Bị khoá nếu mục tài liệu đang bị gắn cờ.",
        {"faq_id": _S}, ["faq_id"]),
    _fn("bao_loi_tai_lieu",
        "Tạo ticket ẩn danh cho giảng viên khi nghi một câu trong tài liệu sai; gắn cờ mục đó.",
        {"section": {**_S, "description": "Ví dụ §3.3"}, "claim": {**_S, "description": "Câu nghi sai"},
         "counterexample": {**_S, "description": "Phản ví dụ"}},
        ["section", "claim", "counterexample"]),
]


def run_tool(name: str, args: dict, session) -> dict:
    # STUB: B thay bằng logic thật (xem PLAN.md mục 7).
    return {"ok": True, "blocked": False, "reason": None,
            "data": {"stub": True, "tool": name, "args": args}, "events": [], "citations": []}
