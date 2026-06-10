"""预生成所有旁白音频（带限流重试），渲染时直接命中缓存。

用法：在仓库根目录运行  python3 warm_voiceovers.py
"""

import ast
import sys
import time
from pathlib import Path

from manim_voiceover.services.gtts import GTTSService


def extract_texts(path="information_geometry.py"):
    tree = ast.parse(Path(path).read_text())
    texts = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "voiceover"):
            for kw in node.keywords:
                if kw.arg == "text" and isinstance(kw.value, ast.Constant):
                    texts.append(kw.value.value)
    return texts


def main():
    texts = extract_texts()
    print(f"共 {len(texts)} 段旁白")
    svc = GTTSService(lang="zh-CN")
    for i, t in enumerate(texts, 1):
        for attempt in range(7):
            try:
                svc._wrap_generate_from_text(t)
                print(f"[{i}/{len(texts)}] ok: {t[:18]}…", flush=True)
                break
            except Exception as e:
                wait = 8 * 2 ** attempt
                print(f"[{i}/{len(texts)}] 失败，{wait}s 后重试: {e}",
                      flush=True)
                time.sleep(wait)
        else:
            print("多次重试仍失败，放弃")
            sys.exit(1)
        time.sleep(3)
    print("全部旁白已缓存")


if __name__ == "__main__":
    main()
