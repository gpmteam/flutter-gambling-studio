from pathlib import Path
import unittest


class StoreScreenshotTopologyGuidanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[2]
        cls.guidance = (
            repo / ".claude/skills/store-screenshots/SKILL.md"
        ).read_text(encoding="utf-8")
        cls.guidance_flat = " ".join(cls.guidance.split())
        cls.phase1 = " ".join(
            cls.guidance.split("## Phase 1 — banner first, then the complete panorama", 1)[1]
            .split("## Phase 2 — visual review criteria", 1)[0]
            .split()
        )

    def test_panorama_uses_capture_only_as_context_for_one_generated_scene(self) -> None:
        required_contract = (
            "**context only**",
            "complete, coherent image",
            "three-quarter/3D view",
            "must not assemble its gameplay field",
            "Check for a pasted screenshot boundary",
        )
        for phrase in required_contract:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.phase1)

        self.assertNotIn("tools/store_compose.py boardplate", self.phase1)
        self.assertNotIn("--from-shot", self.phase1)

    def test_banner_is_generated_first_and_is_world_context_for_the_panorama(self) -> None:
        banner = self.phase1.index("### 1a — Banner (the first generation call)")
        panorama = self.phase1.index("### 1b — Panorama (banner as world context)")
        self.assertLess(banner, panorama)
        for phrase in (
            "Generation order: banner first, then panorama.",
            "the accepted banner (world context — not a character reference)",
            "not an edit, outpaint or crop of the banner",
            "The character may take a different pose, expression, crop or panel",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.guidance_flat)
        # The original character asset stays the first reference on every call.
        for section in ("### 1a", "### 1b"):
            block = self.phase1.split(section, 1)[1]
            with self.subTest(section=section):
                self.assertIn("Attach, in order: the original character asset", block)

    def test_multiplier_balls_and_labels_are_generated_not_pasted(self) -> None:
        for phrase in (
            "attach that file to every scene-generation call as the **multiplier reference**",
            'each used once: "x5", "x10", "x25", "x50", "x100"',
            "never draw a label with Pillow, the compositor or any other script",
            "Never letter it with a script",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.guidance_flat)
        for retired in ("Use Pillow to copy", "alpha-composite them onto the",
                        "keyart-integrated.png", "long-banner-integrated.png"):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, self.guidance_flat)

    def test_character_is_framed_torso_to_head_in_every_scene(self) -> None:
        for phrase in (
            "**Character framing is mandatory, not a style choice.**",
            "no legs, knees, hips or feet are visible",
            "never standing full length and never flying, floating, leaping or levitating",
            "A full-body, standing, flying or leg-revealing character is an objective failure",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.guidance_flat)
        banner = self.phase1.split("### 1a", 1)[1].split("### 1b", 1)[0]
        self.assertIn("framed from torso to head", banner)
        self.assertIn("neither standing full length nor flying", banner)
        self.assertIn("frame it as a torso-to-head bust", self.phase1)
        self.assertNotIn("the character stands large on the left", self.guidance_flat)

    def test_flying_multiplier_balls_are_mandatory_in_every_scene_and_panel(self) -> None:
        for phrase in (
            "**Flying multiplier balls are mandatory in every scene.**",
            "Every panorama panel carries at least one ball",
            "a panel with no ball is an objective failure",
            "at least one ball in each of the [N] portrait panels",
            "The banner always carries all five multiplier balls",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.guidance_flat)
        banner = self.phase1.split("### 1a", 1)[1].split("### 1b", 1)[0]
        self.assertIn("Include all five labelled multiplier balls", banner)
        for retired in ("slide 1 may have none", "at least two labelled multiplier balls",
                        "all five when `--panels 0`"):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, self.guidance_flat)

    def test_lower_edge_is_a_close_up_object_band_over_coins(self) -> None:
        for phrase in (
            "overlapping one another in depth, cropped by the bottom edge",
            "continuous glittering layer of the game's gold coins",
            "no floor, fabric, tabletop, podium, platform or velvet drape",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.phase1)

    def test_phone_slides_use_the_opening_panel_with_the_whole_character(self) -> None:
        phase5 = " ".join(
            self.guidance.split("## Phase 5 — showcases and feature graphic", 1)[1]
            .split("## Phase 6", 1)[0].split())
        for phrase in (
            "**Real-capture backdrops show the opening panel with the whole character.**",
            "pass `--bg-panel 1`",
            "`--bg-subject LEFT,RIGHT`",
            "slides right only as far as the whole character needs",
            '--bg "$ART_DIR/panorama.png" --bg-panel 1 --bg-subject',
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, phase5)

    def test_feature_graphic_is_text_free_with_one_phone_on_the_right(self) -> None:
        required_contract = (
            "a banner with one phone on the right and no text",
            "no title, tagline, logo, wordmark, caption, badge or call to action",
            "`banner` refuses `--title`, `--tagline` and `--logo`",
            "`--shot` is required",
            "`--frame none` is refused",
            "a left side left blank for text is a failed banner",
        )
        for phrase in required_contract:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.guidance_flat)
        self.assertNotIn("optional typography", self.guidance_flat)


if __name__ == "__main__":
    unittest.main()
