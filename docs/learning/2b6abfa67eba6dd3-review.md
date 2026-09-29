# Structured review: panorama reference count

- The existing banner instruction attaches five inputs and is unchanged.
- The panorama instruction formerly required six inputs. Its first five are the character identity, accepted campaign banner, multiplier model, real gameplay capture and shipped symbol sprites. Those all remain attached in the revised instruction.
- The matching previews remain required visual context. The revised instruction attaches them when six inputs are supported and otherwise directs the agent to inspect them separately. It does not loosen the separate requirement to compare reference games or real gameplay.
- The scope is one paragraph in the existing store-screenshots skill. No RNG, math, compliance, image-review, release, or approval gate changes.
- The skill-creator quick validator was tried but cannot validate this existing Claude-style skill frontmatter because it rejects the pre-existing `argument-hint` and `user-invocable` fields. Structural review and `git diff --check` were used for this documentation-only correction.
