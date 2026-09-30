from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from validate_skill import validate


class SkillValidationTests(unittest.TestCase):
    def test_repository_claude_skills_validate_with_invocation_metadata_intact(self):
        for skill in (REPO / ".claude/skills").iterdir():
            if (skill / "SKILL.md").is_file():
                with self.subTest(skill=skill.name):
                    self.assertEqual(validate(skill), [])

    def fixture(self, fields: str, body: str = "Instructions.") -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "SKILL.md"
        path.write_text("---\nname: example\ndescription: A useful skill.\n" + fields + "---\n" + body)
        return path

    def test_claude_fields_are_accepted_only_by_the_claude_schema(self):
        path = self.fixture('argument-hint: "[options]"\nuser-invocable: true\n')
        self.assertEqual(validate(path, "claude"), [])
        self.assertTrue(any("argument-hint" in e for e in validate(path, "codex")))

    def test_malformed_duplicate_unknown_and_wrong_type_fields_still_fail(self):
        for fields in ("user-invocable: 'true'\n", "typo: true\n",
                       "name: duplicate\n", "metadata: [broken\n"):
            with self.subTest(fields=fields):
                self.assertTrue(validate(self.fixture(fields), "claude"))
        self.assertTrue(validate(self.fixture("", ""), "claude"))

    def test_codex_metadata_is_preserved(self):
        self.assertEqual(validate(self.fixture("metadata:\n  short-description: Helpful.\n"), "codex"), [])


if __name__ == "__main__":
    unittest.main()
