"""讲解页的自检：本地链接不能断，每课提到的代码文件和测试文件都要存在。"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = sorted((ROOT / "lessons").glob("*.html"))


def test_local_links_resolve():
    for page in LESSONS:
        for href in re.findall(r'href="([^"#:]+)"', page.read_text(encoding="utf-8")):
            assert (page.parent / href).exists(), f"{page.name} 链接坏了：{href}"


def test_referenced_code_exists():
    for page in LESSONS:
        text = page.read_text(encoding="utf-8")
        for path in re.findall(r"(dsa/\w+\.py|tests/test_\w+\.py)", text):
            assert (ROOT / path).exists(), f"{page.name} 提到的 {path} 不存在"
