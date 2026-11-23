"""讲解页的自检：本地链接不能断，每课提到的代码文件和测试文件都要存在。"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = sorted((ROOT / "lessons").rglob("*.html"))  # 含 lessons/cs/ 计算机基础系列


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


def test_every_listed_problem_has_statement():
    """题单表格（表头含“题号”）里的每道 LeetCode 题，页面上都要有 id="lc-题号" 的题意块。"""
    for page in LESSONS:
        text = page.read_text(encoding="utf-8")
        for table in re.findall(r"<table>(.*?)</table>", text, flags=re.S):
            header = table.split("</tr>", 1)[0]
            if "题号" not in header:
                continue
            for cell in re.findall(r"<tr><td>(.*?)</td>", table):
                match = re.fullmatch(r"(?:LeetCode )?(LCR )?(\d+)", cell)
                if not match:
                    # “牛客”这类不是具体题目的行可以没有题意；带数字却认不出的（如“203 / 82”）要拆成一题一行
                    assert not re.search(r"\d", cell), f"{page.name} 题号格式认不出：{cell}，请一题一行"
                    continue
                anchor = f"lc-lcr-{match[2]}" if match[1] else f"lc-{match[2]}"
                assert f'id="{anchor}"' in text, f"{page.name} 题单里的 {cell} 没有题意"
