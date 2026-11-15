"""讲解页的自检：本地链接不能断，每课提到的代码文件和测试文件都要存在。"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = sorted((ROOT / "lessons").glob("*.html"))


def test_local_links_resolve():
    for page in LESSONS:
        for href in re.findall(r'(?:href|src)="([^"#:?]+)"', page.read_text(encoding="utf-8")):
            assert (page.parent / href).exists(), f"{page.name} 链接坏了：{href}"


def test_anchor_links_resolve():
    """形如 python-basics.html#yield-from 的链接，目标页里必须有 id="yield-from"。"""
    for page in LESSONS:
        for target, anchor in re.findall(r'href="([^"#:?]*)#([^"]+)"', page.read_text(encoding="utf-8")):
            target_page = page.parent / target if target else page
            assert f'id="{anchor}"' in target_page.read_text(encoding="utf-8"), f"{page.name} 锚点坏了：{target}#{anchor}"


def test_every_lesson_has_prerequisites():
    """每一课开头都要有“开始前要会”，告诉读者先回顾哪些内容。"""
    for page in LESSONS:
        if page.name[:2].isdigit():
            assert 'class="prereq"' in page.read_text(encoding="utf-8"), f"{page.name} 缺少“开始前要会”"


def test_referenced_code_exists():
    for page in LESSONS:
        text = page.read_text(encoding="utf-8")
        for path in re.findall(r"(dsa/\w+\.py|examples/\w+\.py|tests/test_\w+\.py)", text):
            assert (ROOT / path).exists(), f"{page.name} 提到的 {path} 不存在"
