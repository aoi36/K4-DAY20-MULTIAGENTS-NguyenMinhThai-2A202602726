"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file."""
    # ponytail: single-turn prompt distillation; upgrade to iterative multi-turn critique if skill quality drops.
    out_dir = Path(out_dir) if out_dir else ROOT / "skills" / "auto"
    runs = []
    for run_file in sorted((Path(results_dir) / source_condition).glob("*/run.json")):
        r = json.loads(run_file.read_text(encoding="utf-8"))
        if r.get("role") != "learn":
            continue
        failed = [(c["name"], c.get("detail", "")) for c in r.get("checks", []) if not c.get("passed", True)]
        if not failed:
            continue
        trace_file = run_file.parent / "trace.md"
        trace = trace_file.read_text(encoding="utf-8")[-6000:] if trace_file.exists() else ""
        runs.append({"task": r.get("task", run_file.parent.name), "failed": failed, "trace": trace})

    if not runs:
        print("không có check thất bại ở tác vụ học")
        return []

    runs_text = "\n\n".join(
        f"Task: {run['task']}\nFailed checks:\n" +
        "\n".join(f"- {name}: {detail}" for name, detail in run["failed"]) +
        (f"\nTrace:\n{run['trace']}" if run["trace"] else "")
        for run in runs
    )
    prompt = (
        f"Write up to {max_skills} procedural skills avoiding these failure modes on new tasks. "
        "Extract general processes, not task IDs, task-specific filenames, answers, or numbers. "
        "Use a 'Use when ...' description and short actionable checklists.\n\n"
        f"{runs_text}\n\nFormat each skill exactly as:\n"
        "=== SKILL: <name> ===\n---\nname: <name>\ndescription: <when to use>\n---\n<content>\n=== END ==="
    )

    model = model or make_model()
    reply = model.invoke(prompt)
    content = reply.text if hasattr(reply, "text") else (reply.content if hasattr(reply, "content") else str(reply))

    written = []
    for name, text in parse_skill_blocks(str(content)):
        if len(written) >= max_skills:
            break
        if validate_skill(text, expected_name=name):
            continue
        skill_file = out_dir / name / "SKILL.md"
        skill_file.parent.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(text, encoding="utf-8")
        written.append(skill_file)
    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
