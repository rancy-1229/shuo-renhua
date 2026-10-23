# -*- coding: utf-8 -*-
"""renhua 检测器测试：跑 python3 -m pytest tests/ 或 python3 tests/test_detector.py"""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENHUA = os.path.join(ROOT, "renhua")
sys.path.insert(0, ROOT)


def run(*args):
    return subprocess.run([sys.executable, RENHUA] + list(args),
                          capture_output=True, text=True)


class TestSamples(unittest.TestCase):
    """同一信息的两个版本，评分必须有强区分度。"""

    @classmethod
    def setUpClass(cls):
        r_bad = run("check", os.path.join(ROOT, "tests/samples/bad_sample.md"), "--json")
        r_good = run("check", os.path.join(ROOT, "tests/samples/good_sample.md"), "--json")
        cls.bad = json.loads(r_bad.stdout)
        cls.good = json.loads(r_good.stdout)

    def test_bad_sample_is_heavy(self):
        self.assertGreaterEqual(self.bad["score"], 70, "AI 腔样例应判为重度(≥70)")

    def test_good_sample_is_human(self):
        self.assertLess(self.good["score"], 25, "人话样例应判为人味(<25)")

    def test_gap_is_large(self):
        self.assertGreater(self.bad["score"] - self.good["score"], 40)


class TestDetector(unittest.TestCase):

    def test_rules_file_is_valid(self):
        """每条规则必须是 8 字段且正则可编译。"""
        import re
        path = os.path.join(ROOT, "rules", "patterns.txt")
        n = 0
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("||")
                self.assertEqual(len(parts), 8, "第 %d 行字段数不是 8" % lineno)
                re.compile(parts[4].strip())  # 正则必须可编译
                self.assertIn(parts[2].strip(), {"syntax", "structure", "lexicon", "rhythm", "decor"})
                self.assertIn(int(parts[3]), (1, 2, 3))
                n += 1
        self.assertGreaterEqual(n, 20, "病灶规则应至少 20 条，当前 %d" % n)

    def test_short_text_no_score(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("太短了。")
            tmp = f.name
        try:
            r = run("check", tmp, "--json")
            d = json.loads(r.stdout)
            self.assertIsNone(d["score"])
        finally:
            os.unlink(tmp)

    def test_clean_text_low_score(self):
        import tempfile
        text = ("机器开机要四十秒，风扇声像直升机。我拆开清了灰，换了个硅脂，"
                "开机降到十五秒。没什么技术含量，就是脏。修完顺手把系统也重装了，"
                "旧盘里的照片先拷出来再动手，别学我上次直接格盘。") * 3
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(text)
            tmp = f.name
        try:
            r = run("check", tmp, "--json")
            d = json.loads(r.stdout)
            self.assertLess(d["score"], 25, "朴素口语应判为人味")
        finally:
            os.unlink(tmp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
