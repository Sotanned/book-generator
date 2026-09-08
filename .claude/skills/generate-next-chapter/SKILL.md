---
name: generate-next-chapter
description: Use when writing the next chapter of a certification study novel in this repo, or when the user says "generate the next chapter" or "write chapter N"
---

# Generate Next Chapter

Write one chapter of a certification study novel, grounded in the book's sources.

## Steps

1. **Resolve the target.**

   ```bash
   python scripts/next_chapter.py <book-id>
   ```

   - Exit 2 means every chapter is written. Say so and stop. This is not an error.
   - Exit 3 means a source file is missing. Stop and report it. Never write a
     chapter whose sources are absent — an ungrounded chapter is worse than no
     chapter.

2. **Read every file in `context_files`.** All of them, before writing anything.
   `bible.md` sets voice and cast, `lexicon.md` fixes the metaphors you must reuse,
   `continuity.md` says what has already happened, the sources are your ground
   truth, and the previous chapter sets the rhythm you are continuing.

3. **Write the chapter** to `output_path`, in this shape:

   ```markdown
   ---
   chapter: "<id from manifest>"
   title: "<title from manifest>"
   domain: <domain_id from manifest>
   topics: <topics from manifest>
   sources: <the chapter's sources>
   status: drafted
   generated: <today's date, YYYY-MM-DD>
   ---
   ```

   Then five sections:

   - **Cold open** — a problem the characters face. Story, not exposition.
   - **The mechanism** — the story resolves, and the technical concept is the
     resolution. Exact syntax, real option names, and actual error text appear as
     story artifacts: a scroll, a ward inscription, a warden's complaint. These
     details are what the exam tests, so they must be exact, not paraphrased.
   - **Diagram** — a Mermaid block, but only if the concept is genuinely
     structural. A decorative diagram is noise. Skipping it is fine and valid.
   - **Status Window** — a boxed cheat sheet in LitRPG style. This is the revision
     surface, re-read the morning of the exam. Dense and scannable.
   - **Field Test** — 3 to 5 exam-style MCQs. Each is a question, options A-D, then:

     ```markdown
     <details><summary>Answer</summary>

     B. Because ...

     </details>
     ```

   Target 2000-3000 words, excluding code blocks.

4. **Ground every technical claim in the sources.** Where you cannot, mark it:

   ```markdown
   !!! warning "Unverified"
       No source in this book confirms the default value of `maxFilesPerTrigger`.
   ```

   Use the marker honestly. It is cheap, and it is the only accuracy mechanism
   this pipeline has. A chapter with three honest markers is more useful than one
   with none and a fabrication.

5. **Reuse metaphors; never invent a second one.** If `lexicon.md` maps a concept
   to a story element, use that element. When you introduce a genuinely new
   concept, append one row to `lexicon.md`. Never add a second row for a concept
   that already has one — `check_book.py` fails on drift.

6. **Append to `continuity.md`**: two or three lines — characters introduced,
   world rules established, threads left open.

7. **Validate.**

   ```bash
   python scripts/check_book.py <book-id>
   ```

   If it fails, fix the chapter and re-run. Do not edit the checker to pass, and
   do not commit a failing chapter.

8. **Mark it drafted**, only after validation passes:

   ```bash
   python -c "import sys; sys.path.insert(0,'scripts'); from bookgen.syllabus import set_status; set_status('books/<book-id>/syllabus.yaml','<id>','drafted')"
   ```

   The file is written before the syllabus is updated, so an interrupted run
   leaves the chapter `unwritten` and simply retries next time.

9. **Commit and push.**

   ```bash
   git add books/<book-id>/
   git commit -m "content: chapter <id> - <title>"
   git push
   ```

## Do not

- Write from memory when a source exists. Read the source.
- Invent Databricks behaviour to make a scene work. Mark it unverified instead.
- Generate more than one chapter per run.
- Skip validation.
