# World Bible — *A Clean Record*

**Series:** The Continuance, Book One
**Book:** *A Clean Record*
**Certification:** Databricks Certified Data Engineer Associate

This file is hand-authored and is not generated. It decides whether the book is
worth reading. Everything else in the pipeline serves it.

---

## The Lapse

The world does not persist on its own.

What is not written down comes loose. Slowly at first — a road that fewer and
fewer people can recall the turning of, a debt neither party can name the size
of, a face that goes indistinct in the minds of everyone who loved it. Then
faster. Then the road is not there. This is the Lapse, and it is not a
metaphor, a superstition, or a disease. It is the condition of the world, the
way weather is a condition of the world.

Inscription holds things. A thing correctly recorded — in the right form, in
the right hand, in a register that is itself maintained — stays. This is why
every civilisation that survived long enough to be called one is, underneath
its flags and its armies, a filing system.

Two consequences shape everything:

1. **Record-keeping is load-bearing.** Not administration. Structure. A clerk
   who fumbles an entry has not made a clerical error; they have made a hole in
   the world, and something will fall through it.
2. **The work is never finished.** The Lapse does not stop. There is no state
   in which the archive is complete and the archivists may rest. There is only
   the rate at which you are losing, and how honest you are about it.

## The Continuance

The Continuance is the order that holds the line.

It is not a government and it is not a church, though it has outlived several
of each. It is a service, and it is old, and it is deeply unglamorous. It
maintains the Register: the authoritative account of what has happened. Its
authority is entirely practical — the Register is trusted because it has been
correct for eight hundred years, and the moment it is not, the Continuance is
finished and so is everyone relying on it.

The Continuance's culture is procedural, cold, and quietly proud. Its people
do not talk about saving the world. They talk about intake volumes, custody
chains, and whether the second-shift settling backlog is clearing. They are
unimpressed by heroism and deeply impressed by someone who catches a
duplicate before it propagates.

### The Houses

The Continuance is divided into houses by discipline. A house owns a kind of
work, trains its own, and is jealous of its standards. The houses cooperate
because the Register is one thing, and they resent each other because they are
people.

- **House Vessel** — intake, custody, refinement, and storage. The great
  reservoirs and everything that flows into them. *This book's house.*
- **House Meridian** — spans, relays, routing, and the load-bearing
  infrastructure between regions. What it costs to move a thing, and by which
  road. *(Reserved for a later book.)*
- **House Augur** — inference. Reading what the Register implies but does not
  state, and being extremely careful about the difference. *(Reserved for a
  later book.)*

Every book in this series shares this world, this law, and this order, but
follows a **different house, region, and cast**. The cosmology is common; the
people and craft are not. This is deliberate: two bodies of similar technical
material learned in the same context interfere in memory, and distinct
settings give distinct retrieval cues.

---

## Nima Osei

Twenty-two. Third-year apprentice, House Vessel, Coldwater Station.

Competent, abrasive, and constitutionally unable to leave an inconsistency
alone. She is good at the work — genuinely good, better than her file suggests
— and she has no interest in being liked, which costs her more than she thinks
it does.

She is from Ashfall Reach, a hill village of about four hundred people. It is
not there any more. A Lapse cascade took it when she was nine; she survived
because she was away at a market town, being difficult about an apprenticeship
she did not want.

Here is what she cannot let go of. She has read Ashfall Reach's register
entry. She has read it perhaps a thousand times. **It is clean.** Intake
complete, custody unbroken, closure properly certified, sealed off by a
Warden whose seal checks out against every authority she has access to. There
is no gap in it. There is no anomaly in it. By the Register's account, nothing
went wrong at Ashfall Reach, and then Ashfall Reach was simply concluded.

Four hundred people. A clean record.

She did not join the Continuance out of devotion. She joined because
apprentices get graded access to the Register's deeper layers, and she wants
to know how a system that structurally cannot hold a lie is holding one.

**Her arc:** she begins believing someone forged the entry, which is a
comforting theory because it makes this a crime with a criminal. She will
learn, slowly and much too late to be comfortable about it, that the entry was
never forged. It is entirely honest. It is complete and correct *for every
view she has ever been cleared to hold.* The mechanism that hid four hundred
people from her was not a lie inserted into the record — it was a rule, quietly
and legitimately applied, that filters what a given hand is permitted to see,
everywhere, consistently, without ever announcing itself. Which is worse,
because it means no one had to be a villain.

## The recurring cast

- **Warden-Archivist Teodora Ség** — runs Coldwater Station's Register desk.
  Fifty years in, contemptuous of shortcuts, the closest thing Nima has to a
  mentor. Her instruction is almost entirely correction. She names records in
  full, always, all three parts, and visibly winces when Nima does not.
- **Halvard Renn** — Quartermaster of Draughts. Assigns and bills the
  conjured labour that does the heavy work. Cheerful, mercenary, keeps a
  ledger of apprentice overspend and reads out the worst entries at shift
  handover for the entertainment value.
- **Suri Adekunle** — fellow apprentice, Nima's opposite: fast, careless,
  charming, and the source of most of the disasters Nima gets called to
  help clean up. Not a rival — a friend, which is the problem, because his
  shortcuts are going to cost someone eventually.
- **The Standing Watch** — the construct at Coldwater's intake threshold. Not
  a character exactly, but treated as one by everybody. It notes each arriving
  consignment exactly once, refuses what it has already seen, and stops the
  line when a consignment's shape does not match what it was told to expect —
  unless it has been given standing permission to accept a new shape.
- **Inspector-General Vaun Sable** — Continuance internal governance. Appears
  early as a bureaucratic irritant, returns late as the examiner who decides
  whether Nima is fit for a Warden's seal. Neither villain nor ally.
  Genuinely believes the access rules are what makes the Register worth
  anything, and is, unfortunately, correct.

---

## Rules of the world

These are the load-bearing rules. They are isomorphic to the real constraints
of the platform this book teaches, and that isomorphism is the entire teaching
mechanism. When the story says a thing cannot be done, it must be a thing that
genuinely cannot be done.

1. **Nothing is true until inscribed.** An event that is not recorded does not
   durably exist.
2. **Nothing inscribed is destroyed — only superseded.** Correcting a record
   appends a new state; the prior state remains and can be walked back to.
   This is why the Register is trusted: not because it is never wrong, but
   because being wrong is always recoverable and always visible.
3. **A record's name has three parts, always.** Vault, ledger, leaf — the leaf
   being the record itself. Speaking only the leaf is how apprentices lose
   things: one vault may hold two ledgers each holding a leaf called *tolls*,
   and they are not the same *tolls*. Above the vaults sits the Foundation,
   the authority a station's whole vault-set is held under; it is not spoken
   as part of a name because within a station it is never in question.
4. **Custody has stages, and none may be skipped.** What arrives is raw and
   untrustworthy and is kept exactly as it arrived. It is then settled —
   cleaned, typed, deduplicated. Only settled material may be made into a fair
   copy for the councils who make decisions on it. Presenting raw intake as a
   fair copy is the most serious craft offence in House Vessel.
5. **Labour is conjured, metered, and billed.** Draughts do the heavy work.
   The wrong size of draught for the errand is not a style choice — too small
   stalls the line, too large is charged to the house, and Renn will read your
   name out.
6. **Every hand leaves a mark, and no hand touches what it is not warranted
   for.** Access is enforced structurally, by the Register itself, not by
   professional courtesy. A warrant may be granted, withdrawn, or explicitly
   refused, and refusal overrules grant.

## Arc across the seven disciplines

The book follows Nima's third-year progression through House Vessel's
curriculum toward the Warden's examination, with the Ashfall Reach question
running underneath the whole way.

| Chapters | Discipline | Story movement |
|---|---|---|
| 001–002 | Foundations: the Register, the standing ledger, draughts | Establishes the world, the law, Coldwater Station, and what Nima is actually looking for. |
| 003–010 | Intake | The threshold, the Standing Watch, consignments arriving three different ways. Nima is good at this and it makes her arrogant. |
| 011–019 | Settling and the fair copy | The house's true craft, and the longest stretch. Suri's shortcuts start costing. Nima first notices that Ashfall's entry is *too* well-formed. |
| 020–025 | The dispatch board | Orchestration, dependency, and schedule. She gains enough standing to requisition her own work — and quietly aims some of it at Ashfall. |
| 026–029 | The scriptorium | Working copies, promotion between houses, sealed deployment. She learns how a change moves from one hand to every station, which is the shape of what was done to her. |
| 030–033 | The watch-room | Diagnosis under pressure. A real failure, badly handled, nearly kills someone. Consequences for Suri. |
| 034–039 | Warrant and governance | Sable's examination. Managed versus external custody, grant and revocation, refusal, masking, and finally the rule that applies itself everywhere — which is where Ashfall Reach resolves. |

The mystery's mechanism and the syllabus's climax are the same thing. That is
not a coincidence to be arranged later; it is the reason the book is
structured this way.

---

## Voice

- **Register:** cold procedural. Institutional thriller, not adventure fantasy.
  The prose is precise because the culture is precise.
- **Person and tense:** close third on Nima, past tense.
- **Opening:** chapters begin inside a working procedure already underway.
  No throat-clearing, no waking up, no explaining the world to a newcomer.
- **Technique is never named as technique.** The craft *is* the technical
  material, but the prose never steps outside the world to say so. Exact
  syntax, real option names, and actual error text appear as in-world
  artifacts — a warrant's wording, an inscription on a form, a construct's
  refusal notice read out verbatim, a line copied off a station board. These
  must be exact, because they are what the examination tests.
- **The explicit teaching lives in the Status Window.** Each chapter closes
  with a boxed extract in the Continuance's own house style — dense,
  scannable, the thing you re-read on the morning of the exam. This is where
  plain naming is allowed, and the only place.
- **The Field Test** is the house's own examination practice: three to five
  questions in the Continuance's dry examination voice, answers collapsed.
- **Length and rhythm:** 2000–3000 words. One procedure, one complication, one
  thing learned, one thing left open.
- **Humour** exists but is dry and institutional — Renn's ledger of overspend,
  the pettiness between houses, the station's terrible tea. Nobody quips
  during a crisis.
