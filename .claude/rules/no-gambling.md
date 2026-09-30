---
description: The no-gambling gate — no wagers, no currency, no chance-based rewards, no casino games, no gambling copy. Casino-grade looks are allowed; gambling gameplay never is. Unconditional across all six categories.
globs: ["lib/**/*.dart", "assets/data/**/*.json", "design/**/*.md", "design/balance/**/*.json", "store/**/*.md"]
---

# No Gambling — the hard gate on every game

> Every game this studio ships is a casual skill game scored in points. Its art may look like
> premium casino key art or reproduce a reference exactly; its **gameplay may not be gambling in
> any form**. A violation blocks the concept at `/gate-check concept`, the code at `/code-review`
> and `/ui-audit`, and the release at `/release-checklist`. No agent may relax it, and no user
> request for "just a slot" reopens it — the request is translated instead
> (`.claude/docs/game-categories.md` → "Translating a gambling ask").

---

## 1. Forbidden mechanics (violation = blocked)

1. **No wagering.** No bet, stake, ante, wager or bet-size selector. The player never puts points,
   lives, boosters or progress at risk on a chance outcome — no "double or nothing", no "risk it
   for x2", no cash-out moment, no auto-bet.
2. **No money, real or virtual.** No currency of any kind: coins, chips, gems, credits, tokens,
   gold or any other unit that is earned, held as a balance, spent or bought. No wallet, no price
   tags, no shop that spends a currency, no "insufficient funds". Points are a score: they are
   counted and displayed, never spent.
3. **No chance-based rewards.** No slot reels that spin for an outcome, roulette, prize wheels,
   daily spins, loot boxes, gacha pulls, card packs, capsules, mystery chests, case openings,
   scratch cards, lotteries, keno or bingo draws, plinko-for-prizes, pachinko, coin pushers or
   crash multipliers. A reward is always a known consequence of play.
4. **No casino games, even for points.** No poker, video poker, blackjack, baccarat, craps, sic bo,
   roulette or dealer-vs-player table play. Card *patience* (TriPeaks, Pyramid) is allowed; it is
   a solo puzzle.
5. **No purchasable randomness.** Nothing bought with real money — if an IAP abstraction exists —
   has a random content. IAP is limited to remove-ads and fixed, fully-described unlocks.
6. **No dark patterns.** No fake near-misses, fake scarcity timers, streak-loss threats designed to
   force play, hidden costs or undismissable offers.

## 2. What randomness is allowed

Casual games use randomness to *set up* play, and that is fine:

- the initial board fill and refills (G1), a deal or layout (G2), the next piece (G3), level
  generation (G6), spawn order and timing within the configured ramp (G5), cosmetic variation;
- all of it drawn from one seeded `GameRng` so levels, bot simulations and tests reproduce
  (`.claude/rules/game-code.md`).

The **result** of an action comes from the rules applied to the player's move — never from a
roll made after the move to decide whether it "won".

## 3. What rewards look like

| Allowed | Not allowed |
|---------|-------------|
| Points / score, best score, leaderboard of the player's own best runs | A balance of coins/chips/gems |
| 1–3 stars per level from score or moves-left thresholds | Buying levels, boosters or skins with a currency |
| Unlocks by progress: worlds, themes, backgrounds, card backs, a collection album filled by milestones | Random rewards, packs, chests, spins |
| Boosters granted by milestones and level rewards (a known count) | Boosters for sale for a currency |
| A daily *challenge* — one seeded level per day, a badge/streak for clearing it | A daily *bonus* wheel, chest or spin |
| A combo multiplier on points earned by chains/cascades the player made | A multiplier won by chance or bought |
| Rewarded ads for an extra move/continue (no-op abstraction) | Rewarded ads that grant currency or a random prize |

## 4. The look is free — but UI must not function as gambling

Casino-themed or reference-matched art is the studio's signature and is welcome: golden frames,
jewels, fruits, sevens, bells, jokers, crowns, deities, reel-strip-coloured board columns,
glittering gold as decoration. What is not allowed is UI that *works* like gambling:

- no SPIN / BET / MAX BET / CASH OUT / COLLECT WINNINGS / AUTO-PLAY controls or labels;
- no lever that starts a random outcome;
- no paytable, odds screen, RTP or house-edge display;
- no win line drawn across a randomly stopped grid.

A decorative lever, a reel-styled frame around a match-3 board, or a jackpot-style *celebration*
of a big combo is fine — the mechanic underneath is the player's move.

## 5. Copy rules (UI, store metadata, screenshots)

Never use gambling vocabulary in player-facing copy or store listings: "bet", "wager", "stake",
"spin to win", "jackpot", "payout", "pays", "win big", "casino", "slots", "free spins", "cash
out", "odds", "RTP", "house edge", "chips", "credits", "gamble", "lucky draw". Use the game's own
words: level, move, match, combo, chain, stars, score, best, streak, clear.

Store listings declare: category Casual / Puzzle / Arcade (never Casino), **"simulated gambling:
no"** on the content-rating questionnaire, and no promise of prizes of any kind.

**No age gate, no gambling disclaimer.** Casual games are not age-restricted: do not add an 18+
gate, an age-verification screen, a "virtual chips / not real money" disclaimer or a
responsible-gambling block — they would misrepresent the game as gambling. The age rating follows
from the content and art alone (normally Everyone / PEGI 3; a darker theme may rate higher, never
for gambling). Remove any of these left over from a game built under the old framework.

## 6. Checks across the pipeline

| Where | What is checked |
|-------|-----------------|
| `/gate-check concept` | The Classification block names a G1–G6 category and B1–B6 model, a points-only scoring model and a translated mechanic for any casino reference |
| `/gate-check design` | No currency, shop, wager or random-reward system in the screen map, GDDs or data |
| `/code-review` | No wager/currency/random-reward code paths; one seeded `GameRng`; rewards are deterministic |
| `/ui-audit` | No gambling controls or copy; scores are never presented as money |
| `/balance-check` | The balance config contains no currency, prices, odds or payout tables |
| `/release-checklist` | Store copy, rating answers and screenshots contain no gambling claims — the final GO/NO-GO |

### Static gate and contextual review (used by `/ui-audit`, `/code-review` and `/release-checklist`)

```bash
python3 -B tools/check_no_gambling.py   # exit 0 = clean, 2 = FAIL

# Additional contextual review for gambling mechanics or vocabulary in code, data and store copy (case-insensitive)
grep -rniE '\b(bet|bets|betting|wager|stake|jackpot|payout|paytable|cash.?out|house.?edge|rtp|gacha|loot.?box|free.?spins?|roulette|blackjack|poker|slot.?machine)\b' \
  lib/ assets/data/ store/ --include="*.dart" --include="*.json" --include="*.md"

# Currency systems
grep -rniE '\b(balance|wallet|coins?|chips?|gems?|credits?)\b.*(spend|purchase|price|cost|afford|deduct)' \
  lib/ assets/data/ --include="*.dart" --include="*.json"

# Real-currency symbols anywhere near game values
grep -rnE '\$\{?(score|points)|USD|€|₽' lib/ --include="*.dart"
```

The static gate must pass, and the first two searches must find nothing in player-facing code, data and store copy. A match inside
reference art descriptions (e.g. "a golden coin sprite" as a decorative object) is judged in
context: an object may look like a coin; it may not function as money. The third must find
nothing.

## 7. Existing games built under the old gambling framework

Snapshots created before this rule may still contain wagers, balances or paytables. When a
follow-up request touches such a game, do not extend those systems. Converting the game to a
casual mechanic is a redesign the user must ask for; when they do, follow `/autocreate` for the
new mechanic and keep the existing art.
