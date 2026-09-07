# Story-Driven Certification Study Guide — Design

**Date:** 2026-09-07
**Status:** Approved design, pre-implementation

## Problem

I am studying for the Databricks Certified Data Engineer Associate exam and have a
one-hour daily commute. Reading technical documentation on a train does not work —
the material is dry and does not stick. Reading fiction on a phone does work; I
already read web novels that way.

The goal is a study guide that is a novel. Each chapter teaches one slice of the
syllabus through an episodic LitRPG story, so that recalling a technical detail
means recalling a scene. I want to **read**, not write. Generation should be
automated; my only job is to read the output and say whether it is any good as a
story.

Later I will sit AWS Solutions Architect Professional and Google ML Engineer, so
the structure must accommodate more books without a rewrite.

### Success criteria

- A chapter I actually want to read on my phone during a commute.
- All seven exam domains covered, with the syntax nuances and operational
  constraints the exam tests.
- Adding a second certification is "create a folder," not a refactor.
- Generation runs on my Claude Code subscription. No API keys.

### Non-goals

These were considered and deliberately dropped. Each can be added later without
restructuring, because the output is plain Markdown.

| Dropped | Why |
|---|---|
| GitHub Actions as scheduler | Claude Code scheduled tasks run on the subscription; Actions would need a token and buys nothing. |
| Databricks workspace execution verification | Real correctness value, but it is a compliance system bolted onto a book I just want to read. |
| Claim ledger and PR merge gates | Same. Review friction I would stop doing by week two. |
| Cloudflare paywall | Not until there is something worth paying for. |
| Amazon KDP publishing | Markdown converts to EPUB the day I want it to. |

## Architecture

One local routine writes one chapter, commits it, and pushes. Cloudflare Pages
builds on push. I read it on my phone whenever.

```
books/
  databricks-de-associate/
    sources/            ground truth: official exam guide, product docs
    world/
      bible.md          setting, cast, rules of the world
      lexicon.md        technical term <-> story term mapping
      continuity.md     append-only ledger of what has happened
    syllabus.yaml       domains -> chapter map, with status
    chapters/
      001-the-guild-registry.md
      002-...
  aws-sa-pro/           empty; created when book one is done
  gcp-ml-engineer/      empty
site/                   MkDocs Material configuration
scripts/
  check_book.py         structural validation
docs/superpowers/specs/ this document
```

### Two structural decisions

**Folder-per-book from day one.** The generator takes a book id. Adding AWS later
means writing a syllabus and a world bible into a new folder — not reshaping the
pipeline. This costs nothing now.

**A separate story world per certification.** It is tempting to have one
protagonist level up through Databricks, then AWS, then GCP. Do not. Similar
technical material learned in the *same* context interferes in memory — reaching
for a Databricks concept and retrieving an AWS one, because they share retrieval
cues. Distinct worlds give distinct cues. The separation is doing real work for
recall, not merely keeping the code tidy.

**Do not generate AWS content yet.** I can only read one serialised story at a
time. AWS SA Pro is also structurally a different exam — long scenario questions
about architecture and cost tradeoffs, rather than Databricks' syntax nuance and
exact option names — so its chapter template will likely differ. Writing book one
first is what reveals which parts actually vary. Two books is when to abstract,
with evidence.

## Components

### 1. `syllabus.yaml` — the plan and the progress tracker

Single source of truth for what to write and what has been written. The generator
reads it to find the next unwritten chapter and writes back status.

```yaml
book_id: databricks-de-associate
title: "The Lakehouse Guild"
exam:
  name: "Databricks Certified Data Engineer Associate"
  guide_version: "2025-07-25"   # date on the official PDF
  questions: 45
  duration_minutes: 90
  pass_mark: 0.70
world: world/bible.md

domains:
  - id: D1
    name: "Databricks Intelligence Platform"
    weight: 0.06                # PROVISIONAL until verified against sources/
    chapters:
      - id: "001"
        slug: the-guild-registry
        title: "The Guild Registry"
        topics:
          - "Unity Catalog three-level namespace"
          - "metastore vs catalog vs schema"
        sources:
          - sources/exam-guide.pdf
          - sources/unity-catalog-overview.md
        status: unwritten       # unwritten | drafted | approved
```

`status` drives everything: the generator picks the first `unwritten` chapter in
document order. I flip `drafted` to `approved` after reading. Nothing blocks on
approval — it is a bookmark, not a gate.

### 2. `world/` — why the story stays coherent across forty chapters

**`bible.md`** — the setting, the cast, the rules. Written once, by hand, before
chapter one. This is the part that decides whether the book is enjoyable, so it is
not generated.

**`lexicon.md`** — the mapping between technical concept and story element:

| Concept | Story element | First appears |
|---|---|---|
| Auto Loader | The Gate Warden, who logs every crate entering the vault | 003 |
| Unity Catalog | The Guild Registry | 001 |

This file exists because the failure mode of long generated fiction is drift:
Auto Loader becomes "the Gate Warden" in chapter 3 and "the Herald of Arrivals" in
chapter 9, and the metaphor stops aiding recall. **A concept gets one metaphor,
permanently.** The generator must read the lexicon before writing and append to it
when introducing a new concept.

**`continuity.md`** — append-only log of what has happened: characters introduced,
world rules established, unresolved threads. Two or three lines per chapter. Loaded
into context so chapter 12 does not contradict chapter 4.

### 3. Chapter format

Roughly 2,500 words, about a twelve-minute read. YAML front matter, then five
sections:

```markdown
---
chapter: "001"
title: "The Guild Registry"
domain: D1
topics: ["Unity Catalog three-level namespace"]
sources: ["sources/exam-guide.pdf", "sources/unity-catalog-overview.md"]
words: 2480
status: drafted
generated: 2026-09-08
---
```

1. **Cold open** — story. A problem the characters face.
2. **The mechanism** — the story resolves; the technical concept is the resolution.
   Exact syntax, real option names, and actual error text appear as story artifacts
   (a scroll, a ward inscription, a warden's complaint), because those are what the
   exam tests.
3. **Diagram** — a Mermaid diagram, but only where the concept is genuinely
   structural. Not every chapter needs one; a decorative diagram is noise.
4. **Status Window** — a boxed cheat sheet in LitRPG style. The revision surface:
   the thing I re-read the morning of the exam.
5. **Field Test** — three to five exam-style multiple-choice questions with answers
   in a collapsed `<details>` block.

### 4. Grounding — accuracy at zero friction cost

I am studying because I do not know the material, so I cannot be the fact-checker.
The answer is not to build a review process I will abandon. It is two rules:

- **Chapters are written from `sources/`, not from model memory.** The relevant
  official documents are pulled into the repo and loaded into context at generation
  time. This alone eliminates most fabrication.
- **Anywhere the model is not grounded in a source, it emits an inline warning
  marker.** The marker is a blockquote, so it is greppable and renders visibly:

  ```markdown
  !!! warning "Unverified"
      No source found for the default value of `maxFilesPerTrigger`.
  ```

  This is MkDocs Material admonition syntax rather than GitHub alert syntax,
  because the site is the reading surface and Material does not render
  `> [!WARNING]`. It stays greppable via the literal `!!! warning "Unverified"`.

  I read past it or I check it. No ledger, no gate, no merge ceremony.

### 5. `generate-next-chapter` — the entry point

One command, implemented as a Claude Code skill so it runs on the subscription:

```
generate-next-chapter <book-id>
```

1. Read `syllabus.yaml`; find the first chapter with `status: unwritten`.
2. Load `world/bible.md`, `world/lexicon.md`, `world/continuity.md`, the previous
   chapter, and the `sources` listed for this chapter.
3. Write the chapter to `chapters/<id>-<slug>.md`.
4. Append new terms to `lexicon.md` and new events to `continuity.md`.
5. Set `status: drafted` in `syllabus.yaml`.
6. Run `check_book.py`; abort the commit if it fails.
7. Commit and push.

**Scheduler-agnostic by design.** A local Claude Code scheduled task, a remote
trigger, or me typing the command all call the same entry point. Which scheduler I
use is a one-line decision I can change at any time.

**Do not automate on day one.** Chapters 1–3 get generated by hand so I can say the
voice is wrong before a routine produces forty chapters in that voice. The
scheduled task is worth setting up only once the prompt reliably produces something
I would keep.

### 6. `site/` — reading surface

MkDocs Material. Mermaid support is built in, mobile reading is good, search and
dark mode come free, and configuration is a single YAML file. Deploys to Cloudflare
Pages from the repo with no build shims.

## Error handling

The pipeline is a nightly unattended job writing to a git repo, so failures must be
loud and must never corrupt state.

- **No unwritten chapters left.** Exit zero with a message. Not an error.
- **A listed source file is missing.** Abort before generating. Writing an
  ungrounded chapter is worse than writing none.
- **Validation fails after generation.** Leave the chapter file on disk, leave
  `status: unwritten`, do not commit. The next run retries the same chapter and I
  can inspect what went wrong.
- **Push fails.** Commit stands locally; the next run pushes both.

State changes are ordered so that an interrupted run is always resumable: the file
is written first, `syllabus.yaml` is updated last.

## Testing

Prose cannot be unit-tested, but structure can, and structure is where an
unattended generator actually breaks. `scripts/check_book.py` validates:

- Front matter present, parseable, and matching the syllabus entry (chapter id,
  domain, slug).
- Word count within range (2,000–3,000).
- Between three and five MCQs, each with an answer block.
- Any Mermaid blocks parse.
- Every `sources` path referenced in front matter exists.
- Chapter ids unique across the syllabus; filenames match `<id>-<slug>.md`.
- Every lexicon term maps to exactly one story element (drift detection).

The generator runs this on the new chapter before committing. Run without
arguments, it validates every chapter in every book — useful after editing a
lexicon or syllabus by hand.

Everything else is human: I read the chapter on the commute and say whether it is
good. That judgement is not automatable and is the only quality bar that matters.

## Open question — task one

The domain weightings in my original blueprint (6 / 21 / 22 / 16 / 10 / 10 / 15)
could not be confirmed from search. The live official exam guide PDF is dated
**25 July 2025**, not 2026 as I had assumed — my "2026 syllabus" is probably that
revision.

The domain *names* broadly matched, so the blueprint is not fabricated. But the
weightings drive how many chapters each domain gets, so they must be verified rather
than guessed.

**Therefore the first implementation task is: download the official exam guide into
`books/databricks-de-associate/sources/`, extract the real domain names and
weightings, and write `syllabus.yaml` from the PDF.** Every later task depends on it.

## Phasing

| Phase | Work | Done when |
|---|---|---|
| 0 | Ground truth: exam guide into `sources/`, verified `syllabus.yaml` | Weightings match the official PDF |
| 1 | World bible and lexicon, written by hand | I like the premise |
| 2 | Chapters 1–3 generated manually; tune voice and density | I would read chapter 4 |
| 3 | MkDocs site, Cloudflare Pages deploy | Readable on my phone |
| 4 | Scheduled task automation | Chapters appear without me |
| 5 | Second book (AWS SA Pro) | Abstract with evidence, not before |
