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

    def test_lower_edge_is_a_close_up_band_of_actual_game_pieces(self) -> None:
        for phrase in (
            "overlapping one another in depth, cropped by the bottom edge",
            "continuous glittering layer of the game's actual tiles, gems, balls or other pieces",
            "no floor, fabric, tabletop, podium, platform or velvet drape",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.phase1)

    def test_phone_slides_sit_on_the_game_background(self) -> None:
        phase5 = " ".join(
            self.guidance.split("## Phase 5 — showcases and feature graphic", 1)[1]
            .split("## Phase 6", 1)[0].split())
        for phrase in (
            "**Phone slides sit on the game background.**",
            '--bg "$ART_DIR/shared-background.png"',
            "with no `--bg-panel`, `--bg-gutter` or `--bg-subject`",
            "the character whole inside the frame",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, phase5)

    def test_keep_runtime_background_falls_back_to_the_opening_panel(self) -> None:
        phase5 = " ".join(
            self.guidance.split("## Phase 5 — showcases and feature graphic", 1)[1]
            .split("## Phase 6", 1)[0].split())
        for phrase in (
            "**Fallback with `--keep-runtime-background` only.**",
            "pass `--bg-panel 1`",
            "`--bg-subject LEFT,RIGHT`",
            "slides right only as far as the whole character needs",
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


class CampaignArtGuidanceTest(unittest.TestCase):
    """Finalization and the store kit make the banner from one template and share one background."""

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[2]
        refs = repo / ".claude/skills/store-screenshots/references"
        cls.store = " ".join((repo / ".claude/skills/store-screenshots/SKILL.md")
                             .read_text(encoding="utf-8").split())
        cls.finalize = " ".join((repo / ".claude/skills/autocreate-finalize/SKILL.md")
                                .read_text(encoding="utf-8").split())
        cls.art = " ".join((refs / "campaign-art.md").read_text(encoding="utf-8").split())
        cls.handoff = " ".join((refs / "campaign-handoff.md").read_text(encoding="utf-8").split())

    def test_both_runbooks_render_the_banner_from_the_shared_template(self) -> None:
        for name, text in (("store-screenshots", self.store), ("autocreate-finalize", self.finalize)):
            with self.subTest(runbook=name):
                self.assertIn("campaign-prompts.md", text)
                self.assertIn("tools/prompt_template.py check", text)
                self.assertIn("campaign-art.md", text)
        self.assertIn("`banner-character` or `banner-object`", self.finalize)

    def test_the_game_background_keeps_the_character_whole_and_is_wired_into_the_game(self) -> None:
        self.assertIn("with the main character **whole inside the frame**", self.finalize)
        for phrase in ("--confirm-game-background-replacement",
                       "bg_campaign_menu.png",
                       "bg_campaign_game.png",
                       "alignment: Alignment.topCenter",
                       "**the character does not fit**",
                       "background-crops.png"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.art)
        self.assertNotIn("Remove promotional multiplier balls/inscriptions, baked gameplay, character",
                         self.finalize)

    def test_the_store_kit_reuses_a_valid_handoff_and_otherwise_makes_campaign_art(self) -> None:
        for phrase in ("**Valid** → copy `long-banner.png` and `shared-background.png` unchanged",
                       "**Missing or stale** → run [campaign-art.md](campaign-art.md) now",
                       "prompt_template.py check`"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.handoff)
        self.assertIn("**Campaign art comes first.**", self.store)
        self.assertIn("V22", self.finalize)

    def test_repairs_do_not_compound_generation_loss(self) -> None:
        # Every image-model edit re-paints the whole frame; stacking them is what turned a
        # panorama mushy. Local defects are repaired as regions, composition gets a fresh render.
        for phrase in ("**Repairs must not compound.**",
                       "tools/region_repair.py cut",
                       "tools/region_repair.py merge",
                       "**At most one whole-frame edit per lineage.**",
                       "--size like:<candidate.png>",
                       "never the 1536x1024 default",
                       "--offset-y",
                       "tools/region_repair.py upscale",
                       "merge --mode detail"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.store)
        self.assertNotIn("targeted edits use the closest candidate", self.store)
        self.assertIn("tools/region_repair.py", self.art)
        self.assertNotIn("continue targeted image-tool edits", self.art)

    def test_campaign_art_never_renders_from_its_previous_version(self) -> None:
        # The banner and background were remade and re-edited run after run, each time from the
        # last output; the artifacts compounded and spread to everything that used the banner.
        repo = Path(__file__).resolve().parents[2]
        refs = repo / ".claude/skills/store-screenshots/references"
        prompts = " ".join((refs / "campaign-prompts.md").read_text(encoding="utf-8").split())
        lineage = " ".join((repo / ".claude/docs/art-lineage.md")
                           .read_text(encoding="utf-8").split())
        for phrase in ("tools/art_lineage.py record", "--role banner", "--role background",
                       "the game's **original** background", "$ORIGINAL_GAME_BACKGROUND",
                       "A changed template alone does not remake it"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.art)
        self.assertNotIn("$CURRENT_GAME_BACKGROUND", self.art)
        self.assertNotIn("the current game background", prompts)
        self.assertIn("A template change alone triggers that one review, not a remake", self.handoff)
        self.assertIn("never as edits of the stale picture", self.handoff)
        self.assertIn("art-lineage.md", self.finalize)
        self.assertIn("lineage.json", self.store)
        for phrase in ("**At most one whole-frame edit per lineage, and only of a fresh render.**",
                       "**Template drift is reviewed, not regenerated.**",
                       "never `bg_campaign_*` or `shared-background.png`"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lineage)
        for doc in ("CLAUDE.md", "AGENTS.md"):
            with self.subTest(doc=doc):
                self.assertIn(".claude/docs/art-lineage.md",
                              (repo / doc).read_text(encoding="utf-8"))


class MobileOnlyGuidanceTest(unittest.TestCase):
    """The studio designs portrait phone games; no rule may ask for a desktop/tablet layout."""

    RETIRED_MATRIX = ("844×390", "844x390", "768×1024", "768x1024", "1024×768", "1024x768",
                      "expanded matrix", "expanded viewport", "expanded reflow",
                      "full-host responsive")

    def test_no_studio_rule_or_skill_requires_an_expanded_layout(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        roots = [repo / ".claude", repo / ".gemini", repo / ".codex", repo / ".github"]
        files = [p for root in roots for p in root.rglob("*.md")]
        files += [repo / "CLAUDE.md", repo / "agents.md", repo / "GEMINI.md", repo / "README.md"]
        for path in files:
            text = path.read_text(encoding="utf-8")
            for phrase in self.RETIRED_MATRIX:
                with self.subTest(file=str(path.relative_to(repo)), phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_the_contract_is_portrait_phone_only_with_a_phone_column(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        contract = (repo / ".claude/docs/mobile-first-contract.md").read_text(encoding="utf-8")
        for phrase in ("# Mobile-Only Phone Contract", "class PhoneColumn",
                       "DeviceOrientation.portraitUp", "UIRequiresFullScreen",
                       "| 360×640 |", "| 430×932 |"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, contract)
        layout = (repo / ".claude/docs/layout-archetypes.md").read_text(encoding="utf-8")
        self.assertIn("### P — phone-height adaptation", layout)
        self.assertNotIn("### R — expanded-viewport reflow", layout)


if __name__ == "__main__":
    unittest.main()
