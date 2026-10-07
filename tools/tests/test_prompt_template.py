from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools/prompt_template.py"
TEMPLATES = REPO / ".claude/skills/store-screenshots/references/campaign-prompts.md"
SPEC = importlib.util.spec_from_file_location("prompt_template", SCRIPT)
assert SPEC and SPEC.loader
prompt_template = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prompt_template)

BANNER_VALUES = {
    "environment": "a violet-to-magenta gradient with a gold radial glow, light streaks and confetti bokeh",
    "character": "a belled-cap jester in a red and gold striped costume",
    "gameplay": "a 7x8 match board of jester, crown, lute and gem tiles with a cleared three-tile match",
    "label_color": "warm gold",
    "accent": "magenta",
    "ball_fx": "confetti sparkle ring",
    "objects": "a red faceted gem, a cyan faceted gem, a blue orb, a gold crown, a lute",
    "foreground_pieces": "glossy gem tiles",
    "palette": "purple, gold and cyan under a warm golden glow",
}


class TemplateFileTests(unittest.TestCase):
    def test_the_campaign_file_defines_every_template_the_runbooks_name(self) -> None:
        templates = prompt_template.load_templates(TEMPLATES)
        self.assertEqual(
            set(templates),
            {"panorama-character", "panorama-object", "banner-character", "banner-object",
             "background-character", "background-object", "background-mechanic"})

    def test_panorama_templates_carry_the_store_panorama_contract(self) -> None:
        # The concept carousel the user approves is the store's panorama: same rules, same words.
        templates = prompt_template.load_templates(TEMPLATES)
        for tid in ("panorama-character", "panorama-object"):
            body = templates[tid]
            for phrase in ('"x5", "x10", "x25", "x50", "x100"',
                           "with at least one ball in each of the {{panels}} portrait panels",
                           "At least two balls fly in front of the board and cover part of it",
                           "three-quarter/3D angle",
                           "never appears as a flat pasted picture",
                           "this is the game's field as players will see it",
                           "cropped by the bottom edge",
                           "No floor, fabric, tabletop, podium or drape"):
                with self.subTest(template=tid, phrase=phrase):
                    self.assertIn(phrase, body)
        character = templates["panorama-character"]
        self.assertIn("torso-to-head bust", character)
        self.assertIn("no legs, knees, hips or feet are visible", character)
        self.assertIn("keep every ball clear of the character's silhouette", character)
        obj = templates["panorama-object"]
        self.assertIn("do not add a person, hand, animal, mascot", obj)
        self.assertIn("leads the first two portrait panels", obj)

    def test_panorama_templates_are_composed_on_the_composition_guide(self) -> None:
        # Placement and the panel cuts travel as a picture, so no value has to carry them.
        templates = prompt_template.load_templates(TEMPLATES)
        for tid in ("panorama-character", "panorama-object"):
            with self.subTest(template=tid):
                body = templates[tid]
                self.assertIn("on the attached composition guide, a layout diagram rather than art",
                              body)
                self.assertIn("its red bands mark where the picture is cut", body)
                self.assertIn("never draw the guide's bands, outlines or flat background", body)

    def test_a_value_that_repeats_the_templates_own_words_is_refused(self) -> None:
        # The values a real concept run sent: each prompt read "a glowing a glowing …".
        template = prompt_template.load_templates(TEMPLATES)["panorama-character"]
        values = {**BANNER_VALUES, "panels": "three"}
        for name, echo in (("ball_fx", "a glowing water-ripple halo"),
                           ("ball_fx", "water-ripple halo, and a short motion trail"),
                           ("label_color", "warm pale gold with a dark outline and inner highlight")):
            with self.subTest(name=name, value=echo):
                with self.assertRaises(prompt_template.TemplateError) as raised:
                    prompt_template.render(template, {**values, name: echo})
                self.assertIn("repeats the template's own words", str(raised.exception))
        clean = prompt_template.render(template, values)
        self.assertEqual(prompt_template.check(template, clean)["ball_fx"], values["ball_fx"])
        # A prompt saved before the check existed is caught by `check` too.
        echoed = clean.replace("a glowing confetti sparkle ring",
                               "a glowing a glowing confetti sparkle ring")
        with self.assertRaises(prompt_template.TemplateError):
            prompt_template.check(template, echoed)

    def test_banner_and_background_are_rendered_in_the_approved_panoramas_world(self) -> None:
        templates = prompt_template.load_templates(TEMPLATES)
        for tid in ("banner-character", "banner-object", "background-character",
                    "background-object", "background-mechanic"):
            with self.subTest(template=tid):
                self.assertIn("the world of the attached panorama", templates[tid])
                self.assertNotIn("attached banner", templates[tid])
        for tid in ("banner-character", "background-character"):
            with self.subTest(template=tid):
                self.assertIn("the panorama is world context, not the character reference",
                              templates[tid])

    def test_banner_templates_carry_the_store_banner_contract(self) -> None:
        templates = prompt_template.load_templates(TEMPLATES)
        for tid in ("banner-character", "banner-object"):
            body = templates[tid]
            for phrase in ('"x5", "x10", "x25", "x50", "x100"',
                           "At least two balls fly in front of the board and cover part of it",
                           "none in the right third",
                           "cropped by the bottom edge",
                           "No floor, fabric, tabletop, podium or drape",
                           "No other text, title, logo, wordmark, tagline, device, UI or empty "
                           "copy space"):
                with self.subTest(template=tid, phrase=phrase):
                    self.assertIn(phrase, body)
        character = templates["banner-character"]
        self.assertIn("torso-to-head bust", character)
        self.assertIn("no legs, knees, hips or feet are visible", character)
        self.assertIn("keep every ball clear of the character's silhouette", character)
        self.assertIn("do not add a person, hand, animal, mascot", templates["banner-object"])

    def test_background_templates_fit_the_lead_and_carry_no_marketing_objects(self) -> None:
        templates = prompt_template.load_templates(TEMPLATES)
        character = templates["background-character"]
        self.assertIn("fits entirely inside the frame", character)
        self.assertIn("Nothing of the head, headwear, shoulders, hands or held objects is cut by "
                      "an edge of the image", character)
        self.assertIn("no legs, knees, hips or feet are visible", character)
        for tid in ("background-character", "background-object", "background-mechanic"):
            with self.subTest(template=tid):
                body = templates[tid]
                self.assertIn("9:19.5", body)
                self.assertIn("labelled coins or multiplier balls anywhere", body)
                self.assertIn("Do not paint a game board", body)
                self.assertNotIn('"x100"', body)


class RenderCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.template = prompt_template.template_for(TEMPLATES, "banner-character")

    def test_a_rendered_prompt_passes_check_and_returns_its_values(self) -> None:
        prompt = prompt_template.render(self.template, BANNER_VALUES)
        self.assertNotIn("{{", prompt)
        values = prompt_template.check(self.template, prompt)
        self.assertEqual(values["objects"], BANNER_VALUES["objects"])

    def test_check_ignores_line_wrapping(self) -> None:
        prompt = prompt_template.render(self.template, BANNER_VALUES)
        rewrapped = prompt.replace(". ", ".\n\n   ")
        prompt_template.check(self.template, rewrapped)

    def test_a_reworded_sentence_fails_and_is_named(self) -> None:
        prompt = prompt_template.render(self.template, BANNER_VALUES)
        drifted = prompt.replace("At least two balls fly in front of the board",
                                 "Some balls may fly near the board")
        with self.assertRaises(prompt_template.TemplateError) as ctx:
            prompt_template.check(self.template, drifted)
        self.assertIn("departs from the template", str(ctx.exception))

    def test_an_extra_instruction_appended_fails(self) -> None:
        prompt = prompt_template.render(self.template, BANNER_VALUES)
        with self.assertRaises(prompt_template.TemplateError):
            prompt_template.check(self.template, prompt + " Also add the game's title at the top.")

    def test_missing_unknown_empty_and_oversized_values_are_refused(self) -> None:
        values = dict(BANNER_VALUES)
        values.pop("palette")
        with self.assertRaises(prompt_template.TemplateError):
            prompt_template.render(self.template, values)
        with self.assertRaises(prompt_template.TemplateError):
            prompt_template.render(self.template, {**BANNER_VALUES, "title": "Joker"})
        with self.assertRaises(prompt_template.TemplateError):
            prompt_template.render(self.template, {**BANNER_VALUES, "accent": "  "})
        with self.assertRaises(prompt_template.TemplateError):
            prompt_template.render(self.template, {**BANNER_VALUES, "objects": "x" * 501})

    def test_cli_render_then_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "banner-prompt.txt"
            args = [sys.executable, str(SCRIPT), "render", "--template", str(TEMPLATES),
                    "--id", "banner-character", "--out", str(out)]
            for name, value in BANNER_VALUES.items():
                args += ["--set", f"{name}={value}"]
            subprocess.run(args, check=True, capture_output=True, text=True, timeout=30)
            check = subprocess.run(
                [sys.executable, str(SCRIPT), "check", "--template", str(TEMPLATES),
                 "--id", "banner-character", "--prompt", str(out)],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(check.returncode, 0, check.stderr)
            wrong = subprocess.run(
                [sys.executable, str(SCRIPT), "check", "--template", str(TEMPLATES),
                 "--id", "banner-object", "--prompt", str(out)],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(wrong.returncode, 1)


if __name__ == "__main__":
    unittest.main()
