"""Checker regression tests; these do not execute a model or test a UI."""
from pathlib import Path
import importlib.util
import json
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_skill', ROOT / 'scripts/check_skill.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('README.md', 'SKILL.md', 'tests/behavior_cases.json'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def append(self, text):
        with (self.root / 'SKILL.md').open('a', encoding='utf-8') as out:
            out.write('\n' + text + '\n')

    def test_current_package_passes(self):
        self.assertEqual(checker.check(self.root), [])

    def test_missing_skill(self):
        (self.root / 'SKILL.md').unlink()
        self.assertIn('Missing SKILL.md', checker.check(self.root))

    def test_missing_frontmatter(self):
        (self.root / 'SKILL.md').write_text('# Skill\n', encoding='utf-8')
        self.assertTrue(any('frontmatter' in e for e in checker.check(self.root)))

    def test_invalid_name(self):
        p = self.root / 'SKILL.md'
        p.write_text(p.read_text(encoding='utf-8').replace('name: ui-ux-web-guidelines', 'name: Invalid_Name'), encoding='utf-8')
        self.assertTrue(any('invalid or missing name' in e for e in checker.check(self.root)))

    def test_duplicate_metadata(self):
        p = self.root / 'SKILL.md'
        p.write_text(p.read_text(encoding='utf-8').replace('name: ui-ux-web-guidelines', 'name: ui-ux-web-guidelines\nname: duplicate'), encoding='utf-8')
        self.assertTrue(any('duplicate metadata' in e for e in checker.check(self.root)))

    def test_tool_grant_rejected(self):
        p = self.root / 'SKILL.md'
        p.write_text(p.read_text(encoding='utf-8').replace('name: ui-ux-web-guidelines', 'name: ui-ux-web-guidelines\nallowed-tools: Bash'), encoding='utf-8')
        self.assertTrue(any('tool grants' in e for e in checker.check(self.root)))

    def test_missing_file(self):
        self.append('[missing](absent.md)')
        self.assertTrue(any('missing local file' in e for e in checker.check(self.root)))

    def test_bad_anchor(self):
        self.append('[missing](README.md#does-not-exist)')
        self.assertTrue(any('missing local anchor' in e for e in checker.check(self.root)))

    def test_escape_rejected(self):
        self.append('[escape](../outside.md)')
        self.assertTrue(any('escapes package' in e for e in checker.check(self.root)))

    def test_fenced_links_ignored(self):
        self.append('```md\n[example](absent.md)\n```')
        self.assertEqual(checker.check(self.root), [])

    def test_unicode_and_duplicate_anchors(self):
        self.assertEqual(checker.anchors('# 測試：標題\n# 測試：標題\n'), {'測試標題', '測試標題-1'})

    def test_duplicate_case_rejected(self):
        p = self.root / 'tests/behavior_cases.json'
        cases = json.loads(p.read_text(encoding='utf-8'))
        cases.append(cases[0])
        p.write_text(json.dumps(cases), encoding='utf-8')
        self.assertTrue(any('duplicate IDs' in e for e in checker.check(self.root)))

    def test_empty_rubric_rejected(self):
        p = self.root / 'tests/behavior_cases.json'
        cases = json.loads(p.read_text(encoding='utf-8'))
        cases[0]['required_behaviors'] = []
        p.write_text(json.dumps(cases), encoding='utf-8')
        self.assertTrue(any('nonempty strings' in e for e in checker.check(self.root)))

    def test_missing_case_rejected(self):
        p = self.root / 'tests/behavior_cases.json'
        cases = json.loads(p.read_text(encoding='utf-8'))
        p.write_text(json.dumps(cases[:-1]), encoding='utf-8')
        self.assertTrue(any('five approved' in e for e in checker.check(self.root)))

    def test_bad_json_rejected(self):
        (self.root / 'tests/behavior_cases.json').write_text('{', encoding='utf-8')
        self.assertTrue(any('Behavior cases:' in e for e in checker.check(self.root)))


if __name__ == '__main__':
    unittest.main()
