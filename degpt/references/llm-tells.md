# Key Indicators That an LLM Wrote Documentation

## 1. Telltale Vocabulary

Certain words appear with dramatically higher frequency in LLM output
than in human writing. Frequency data from corpus analysis of ~500K
documents (human baseline vs GPT-4/Claude outputs, 2023-2025):

### Tier 1 — Strongest signals (10x+ overrepresentation in LLM text)

These words appear in LLM output at 10-50x the rate of human writing.
Any ONE of these in a prose paragraph is a weak signal; two or more in
the same paragraph is a strong vocabulary signal.

- **"delve"** — 40x overrepresented in early GPT-4 (2023-2024); dropped
  to ~8x by mid-2025 after widespread mockery. Still a strong signal in
  older or untuned outputs.
- **"tapestry"** — ~25x overrepresented. Almost never appears in
  technical documentation written by humans.
- **"testament"** — ~20x. "This is a testament to..." is a near-certain
  LLM construction in technical contexts.
- **"vibrant"** — ~15x. Humans use it for colors; LLMs use it for
  communities, ecosystems, and discussions.
- **"foster"** — ~12x. "Foster collaboration/innovation/growth" is a
  signature LLM phrase.
- **"intricate"** — ~10x. Used by LLMs to describe anything with more
  than two moving parts.

### Tier 2 — Strong signals (5-10x overrepresentation)

- **"crucial," "pivotal," "essential"** — LLMs over-qualify importance.
  Humans say "important" or just let the context speak.
- **"landscape"** (non-geographic) — "the AI landscape," "the threat
  landscape." ~7x overrepresented in non-geographic contexts.
- **"meticulous"** — ~6x. "Meticulous attention to detail" is a stock
  LLM phrase.
- **"underscore," "enhance," "bolster"** — ~5-6x each.

### Tier 3 — Moderate signals (3-5x overrepresentation)

These are common in human writing too but appear notably more often in
LLM output. Only count as a vocabulary signal when clustered (2+ in a
single paragraph).

- **Filler verbs**: "leverage," "unlock," "navigate," "harness,"
  "embark," "utilize," "facilitate," "streamline," "spearhead"
- **Generic nouns**: "ecosystem," "framework," "dynamic," "interplay,"
  "synergy," "paradigm"
- **Dramatic openers**: "unleash the power of," "at the forefront of,"
  "pave the way for," "bridging the gap between," "in the realm of"

### Era-specific shifts

LLM vocabulary tells evolve as models are updated and fine-tuned:

- **2023 (early GPT-4)**: "delve," "tapestry," "testament," "vibrant"
  at peak frequency. "Certainly!" and "Great question!" as openers.
- **2024 (GPT-4-turbo, Claude 3)**: "delve" usage drops ~60% after
  public awareness. "Crucial," "landscape," "foster" remain strong.
  Claude introduces "I'd be happy to" as a signature opener.
- **2025 (GPT-4o, Claude 3.5/4)**: Models trained to suppress the most
  mocked words. "Delve" rare. But "foster," "enhance," "streamline"
  persist. New tells emerge: "straightforward," "robust," "seamless."
- **2026 (current)**: Watch for: "comprehensive," "walkthrough,"
  "hands-on," "step-by-step" in contexts where humans would just write
  instructions without labeling them.

## 2. Structural Patterns

- **Rule of Three**: AI defaults to grouping things in triplets
  (adjectives, benefits, examples) with unnatural consistency. In human
  writing, lists of 2, 4, or 5 are equally common. A document where
  every bullet list has exactly 3 items is suspicious.
  - **Threshold**: 3+ triplet lists in a single document, or a triplet
    pattern in >50% of bullet lists.
  - **Example**: "fast, reliable, and scalable" / "simplicity, power,
    and flexibility" / "developers, teams, and organizations" — three
    triplets in one page is a strong structural signal.
- **"Not X, but Y" constructions**: Variations of "not just X, but Y"
  appeared in ~6% of LLM messages in one dataset vs <0.5% in human
  writing — a 12x overrepresentation for a single rhetorical device.
- **False ranges**: "From intimate gatherings to global movements"
  implies a spectrum where none exists. LLMs use this to sound
  comprehensive without saying anything specific.
- **Mathematically even cadence**: Paragraphs follow textbook patterns,
  transitions are frictionless, sentence lengths are suspiciously
  uniform (typically 15-25 words per sentence with low variance). Human
  writing has higher variance — short punchy sentences mixed with long
  complex ones.
  - **Threshold**: Compute the coefficient of variation (CV) of sentence
    lengths in a paragraph. CV < 0.25 across 5+ sentences is suspicious.
    Human prose typically has CV > 0.35.
- **Formulaic section structure**: Neat headers, bullet points, and
  parallel constructions throughout. Every section follows the same
  pattern: topic sentence, 3 bullets, concluding sentence.
- **Suspiciously balanced pros/cons**: When listing advantages and
  disadvantages, LLMs tend to produce exactly equal numbers of each.
  Humans are usually biased toward one side.

## 3. Punctuation and Formatting

- **Em dash overuse**: LLMs use em dashes (—) at 3-5x the rate of
  typical human technical writers. Often appears where commas,
  parentheses, or colons would be more natural.
  - **Threshold**: More than 2 em dashes per 500 words of prose in a
    technical document is elevated. More than 4 per 500 words is a
    strong signal.
  - **Exception**: Some human writers (especially those influenced by
    journalism or literary nonfiction) use em dashes heavily. Check
    whether the frequency is consistent across the whole document or
    concentrated in specific sections.
- **Markdown in non-Markdown contexts**: Fenced code blocks or Markdown
  syntax (bold, headers, links) appearing in plain text files, emails,
  or contexts where Markdown is not rendered.
- **Overly clean formatting**: Perfect consistency in bullet styles,
  heading levels, and whitespace throughout a long document. Human-
  written docs accumulate inconsistencies over time as multiple people
  edit them.
- **Exclamation mark avoidance**: LLMs in "professional" mode almost
  never use exclamation marks. Human technical writers occasionally do,
  especially in warnings, tips, or informal docs.

## 4. Tone and Register

- **HR-speak friendliness**: "It's understandable that...,"
  "Great question!," gentle summarizing endings ("Ultimately...,"
  "In conclusion..."). This register is appropriate in customer support
  but jarring in technical documentation.
  - **Example**: "We understand that getting started can feel
    overwhelming, but rest assured that..." — no human engineer writes
    this in a README.
- **Hedging padding**: "It's worth noting," "it's important to
  remember," "one might argue," "it should be mentioned that" add
  nothing but word count. In a 500-word section, 3+ hedging phrases
  is a strong signal.
  - **Threshold**: Count hedging phrases per 500 words. Human baseline:
    0-1. LLM typical: 3-6.
- **Overemphasis of importance**: Everything is "fascinating,"
  "captivating," "remarkable," or "a pivotal moment." When every
  feature is "crucial" and every update is "exciting," nothing actually
  stands out.
- **Emotional flatness**: Text reads as polished but objective; lacks
  the subjective punctuation patterns (exclamation marks, ellipses,
  rhetorical questions, parenthetical asides) that humans naturally
  use. The voice never wavers, never shows frustration or humor.
- **Compulsive revision, no improvisation**: Reads like it was endlessly
  edited but never spontaneous. Every sentence is grammatically perfect.
  Human first drafts (even published ones) have rough edges.
- **Uniform register across topics**: LLMs maintain the same level of
  formality whether describing a critical security patch or a minor
  whitespace fix. Humans naturally shift register based on stakes.

## 5. Transitional Phrases

Overuse of formal transitions. In human technical writing, most
paragraphs start with the subject or a short connector ("But," "So,"
"Also,"). LLMs default to academic-style transitions:

**High-signal transitions** (rare in human tech docs, common in LLM output):

- "Moreover," "Furthermore," "Additionally," "Indeed," "Notably,"
  "Consequently," "Subsequently," "Accordingly," "Conversely"

**Medium-signal transitions** (used by humans too, but at lower density):

- "It is worth noting," "In terms of," "With regard to," "In light of,"
  "As such," "To that end," "In particular"

**Threshold**: More than 2 high-signal transitions per 500 words is
suspicious. More than 4 is a strong signal. Count only prose paragraphs,
not bullet lists or headers.

**Not a signal**: "However," "For example," "That said," "In practice"
— these are common in both human and LLM writing.

## 6. Technical Documentation-Specific Tells

- **"Correct but useless" descriptions**: Restating what the code does
  without explaining why. "The `processData` function processes the
  data" tells the reader nothing they could not see from the function
  name.
  - **Example of LLM-style**: "This function takes a configuration
    object and returns a validated configuration." (just restates the
    signature)
  - **Example of human-style**: "Validates config before the server
    starts — catches typos in field names that would otherwise cause
    a cryptic panic 30 seconds into startup."
- **Missing business context**: The "why" behind decisions is absent;
  only the "what" is documented. LLMs describe mechanisms well but
  cannot explain motivations they were never told.
- **Knowledge-cutoff disclaimers**: Statements that information is
  accurate "as of" a certain date, or "at the time of writing." Humans
  rarely add these to project docs.
- **Suspiciously complete boilerplate**: Perfect JSDoc/docstrings that
  describe parameters mechanically but add no insight beyond what the
  type signature already says.
- **Generic README prose under standard headers**: Standard section
  headers like "Installation," "Usage," "Contributing," and "License"
  are human convention — virtually every project uses them, and their
  presence is NOT a tell. The signal is in the **prose under those
  headers**: if the Installation section says "Getting started is
  straightforward — simply follow these steps to leverage the full
  potential of this framework," that is LLM slop. If it says
  `pip install foo`, that is human.
  - **Rule**: NEVER flag a document solely because it has standard
    README section headers. Only flag when the prose content under those
    headers exhibits 3+ tell categories.
- **Artificially comprehensive scope**: LLMs tend to cover every
  possible sub-topic even when the user asked about one thing. A
  "Getting Started" guide that covers installation, configuration,
  deployment, monitoring, and troubleshooting in exhaustive detail
  is suspicious — humans write focused docs.

## 7. Model-Specific Opening Words

These apply to the first sentence of a response or document section:

- **ChatGPT** tends to start with: "As," "Sure," "Certainly," "Here,"
  "Creating," "To," "Let's." The "Certainly!" opener was extremely
  common in GPT-3.5 and early GPT-4 but has been suppressed in later
  versions.
- **Claude** tends to start with: "I'd," "Based," "Here," "This,"
  "How," "Looking." The "I'd be happy to help" pattern is a strong
  Claude signal, especially in technical contexts where no help was
  requested.
- **Gemini** tends to start with: "Absolutely," "Great," "Here,"
  "That's a great question."
- **General LLM pattern**: Starting a document or section with a
  meta-statement about what the document will cover ("In this guide,
  we'll explore...") rather than just starting the content.

## 8. Caveats and Operationalization

### False positive risks

- No single indicator is conclusive. LLMs learned from human writing,
  so humans use these patterns too — especially humans who read a lot
  of LLM output and unconsciously adopt its style.
- Academic and formal business writing naturally uses many of the
  transitions and structures that flag as LLM tells. Context matters:
  "Moreover" in a physics paper is normal; "Moreover" in a CLI tool's
  README is suspicious.
- Non-native English speakers sometimes produce text that triggers
  vocabulary and structure tells because they learned formal English
  from textbooks (which LLMs also learned from).

### Detection accuracy

- Heavy LLM users can detect AI text ~90% of the time (per a 2025
  study of 500 participants).
- Automated detection using the tell-category convergence approach
  (3+ categories) achieves ~85% precision and ~70% recall on mixed
  corpora.
- Recall drops to ~40% on text that was prompted with specific style
  instructions or heavily edited post-generation.

### Temporal drift

- These tells evolve as models are updated. What screams "AI" today
  may not tomorrow.
- Paraphrasing, editing, or prompting for a specific style can mask
  most of these signals.
- The strongest long-term signal is not any single word but the
  combination of uniform cadence + absence of genuine opinion +
  suspiciously complete coverage of a topic.

### Operationalization

Operational scoring rules (paragraph-level analysis, minimum text
length, cluster scoring, document-level context) are defined in
`system.md` hard rules. They are the authoritative source. This
section is intentionally kept minimal to avoid redundant context in
the assembled prompt.
