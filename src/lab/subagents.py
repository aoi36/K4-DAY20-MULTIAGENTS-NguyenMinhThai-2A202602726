"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {"name": "explorer", "description": "Use to inspect task files and report requirements before editing.",
         "system_prompt": "Read task files and report relevant facts. Do not edit files."},
        {"name": "implementer", "description": "Use to implement requested changes and run relevant checks.",
         "system_prompt": "Implement the delegated task, run checks, and report changed files and results."},
        {"name": "reviewer", "description": "Use to independently verify changes against requirements and edge cases.",
         "system_prompt": "Review the delegated result and report defects. Do not edit files."},
    ]
