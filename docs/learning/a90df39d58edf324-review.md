# Resume dependency preflight review

The observed relocated project had no package_config metadata. Its first current
analyzer invocation exited 3 with 1226 import cascade issues. After flutter pub get,
the same unchanged source analyzed with zero issues. The existing dependency lock
SHA-256 remained cc78bc07cb212dbc207fc7aeef069ffc30b99e05291e2008d390b0d2741d7e61.
The continuation native baseline also remained unchanged.

This proposal adds a missing-metadata condition to the existing resume discovery
path and the finalize preflight, before its analyzer. It uses the already documented
pub get operation. Existing metadata avoids that extra invocation. A hydration
failure stops this preflight and points to its log instead of producing source
import failures. Analyzer and test gates are retained verbatim; no dependency
versions, source app, balance, assets or current checkout rules are edited.

Review findings: both additions apply only to resumed Flutter projects; the continue
instruction preserves dependency locks and native versions; the executable finalize
block keeps failure visible and ordered before analysis. Existing frontmatter is
byte-identical, with the existing name and description fields present. The skill-creator validator does not support this
repository's existing user-invocable/argument-hint keys, so those are preserved.
All former skill text and relative references are retained. Human merge is required
before these instructions become active.
