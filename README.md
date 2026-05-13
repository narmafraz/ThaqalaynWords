# ThaqalaynWords

Per-word Arabic dictionary for the Thaqalayn hadith corpus. Each surface
form in the corpus has a JSON page; each lemma it maps to has a richer
lemma page with cross-references to classical Arabic lexicons; each
shared root collects its sibling lemmas.

**Live API:** <https://thaqalaynwords.netlify.app/>

Example endpoints:
- `/index/roots.json` — all 2,769 roots sorted by total corpus frequency
- `/index/lemmas.json` — all 13K lemmas with cross-reference flags
- `/index/surfaces.json` — all 102K unique diacritized surfaces
- `/lemmas/{slug}.json` — full lemma page (paradigm, root_link, definition, etymology, IPA, cross-refs)
- `/roots/{slug}.json` — root page with sibling lemma list
- `/surfaces/{slug}.json` — surface page with occurrence paths + lemma_link

All Arabic in URLs is percent-encoded UTF-8. Root slugs use `_` for
weak/hollow radicals (`ق-_-ل` for ق-و-ل).

See **`Thaqalayn/docs/WORDS_PROJECT_PLAN.md`** for the master plan and
the next-steps roadmap.

## Directory layout

```
ThaqalaynWords/
├── surfaces/          one JSON per unique surface form in the corpus
│   ├── قَالَ.json
│   ├── وَقَالَ.json
│   └── ...
├── lemmas/            one JSON per unique lemma
│   ├── قالَ.json
│   └── ...
├── roots/             one JSON per unique three-radical root, listing
│   ├── ق-_-ل.json     all lemmas derived from it (avoids per-lemma
│   ├── ك-ت-ب.json     duplication of the sibling list)
│   └── ...
├── index/             browse / autocomplete indexes
│   ├── surfaces.json  flat list (slug, count, lemma, pos)
│   ├── lemmas.json    flat list (slug, root, root_slug, pos, frequency, refs)
│   └── roots.json     flat list (slug, root, lemma_count, total_frequency)
├── serve.py           CORS-enabled dev HTTP server on :8889
└── netlify.toml       deployment config (CORS + immutable cache)
```

**Why a separate `roots/` directory.** Many lemmas share the same root
but each has its own paradigm (e.g. for root ق-و-ل: قالَ "to say"
Form I, قاوَلَ "to negotiate" Form III, أَقالَ "to dismiss" Form IV,
قَوْل "saying" noun — totally different inflected forms each). The
*paradigm* lives on the lemma; the *list of sibling lemmas* lives on
the root page. Lemmas point to their root via `root_link` rather than
inlining the sibling list.

Slugs are diacritized Arabic NFC. URLs use percent-encoded UTF-8.

## Page shapes

### Surface page (`surfaces/{slug}.json`)

A surface form is the exact word as it appears in a hadith chunk
(e.g. `وَقَالَهُ` = "and he said it"). Each unique surface gets one
JSON page.

```json
{
  "surface": "وَقَالَهُ",
  "slug": "وَقَالَهُ",
  "occurrence_count": 42,
  "occurrence_paths": ["/books/al-kafi:1:1:1:1", "..."],
  "morphology": {
    "lemma_slug": "قالَ",
    "root": "ق.#.ل",
    "pos": "V",
    "pos_camel": "verb",
    "clitics": {"prc2": "wa_conj", "enc0": "3ms_dobj"}
  },
  "lemma_link": "/words/lemmas/قالَ"
}
```

#### Field reference — surface page

| Field | Meaning |
|---|---|
| `surface` | Exact diacritized form as found in a chunk (`arabic_text`). Unicode-NFC-normalized but otherwise untouched. |
| `slug` | The URL/filename slug. Same as `surface` after NFC normalization; kept as a separate field so consumers don't have to re-derive it. |
| `occurrence_count` | How many times this surface appears across the entire hadith corpus (with duplicates). |
| `occurrence_paths` | Every hadith path that contains the surface, e.g. `/books/al-kafi:1:1:1:1`. De-duplicated and sorted. The UI uses this list to build "narrations containing this word" pages. **Not capped** — common words like قَالَ may have 12K+ paths. |
| `morphology` | Object with the CAMeL Tools morphological analysis, or `null` if the surface is unanalyzable (proper nouns, Latin chars, unknown tokens — ~6% of surfaces). |
| `morphology.lemma_slug` | **Diacritized** canonical lemma — same slug as the lemma page (`lemmas/{lemma_slug}.json`). Derived by generating the lemma's citation form (past 3ms for verbs, singular for nouns). |
| `morphology.root` | Arabic root in CAMeL's dotted notation, e.g. `ق.#.ل`. The `#` is CAMeL's placeholder for a weak/hollow radical (in this case و). The UI should display this as `ق-و-ل` or `ق و ل`. |
| `morphology.pos` | Project's compact POS tag: `V` (verb), `N` (noun), `ADJ`, `ADV`, `PREP`, `CONJ`, `PRON`, `DET`, `PART`, `INTJ`, `REL`, `DEM`, `NEG`, `COND`, `INTERR`. |
| `morphology.pos_camel` | CAMeL Tools' more granular POS, e.g. `noun_prop`, `verb`, `adj.act`. Use this when you need the finer distinction; use `pos` for compact UI rendering. |
| `morphology.clitics` | Attached affixes detected by CAMeL Tools. See the **Clitic taxonomy** section below. Empty `{}` when the surface is a bare stem. |
| `lemma_link` | Path the UI navigates to for the underlying lemma page. Same as `/words/lemmas/{morphology.lemma_slug}`. `null` when `morphology` is `null`. |

`morphology` is null for unanalyzable surfaces (proper nouns / Latin
gibberish / completely unknown tokens) — typically ~6% of the corpus.

### Lemma page (`lemmas/{slug}.json`)

A lemma is the dictionary head-word: the form you'd look up in a
classical lexicon (e.g. `قالَ` "to say"). Multiple surface forms
collapse to the same lemma via the paradigm.

```json
{
  "lemma": "قالَ",
  "slug": "قالَ",
  "root": "ق.#.ل",
  "root_slug": "ق-_-ل",
  "root_link": "/words/roots/ق-_-ل",
  "pos": "V",
  "pos_camel": "verb",
  "paradigm": [
    {"role": "past_3ms", "form": "قالَ",
     "in_corpus": true, "count": 14,
     "asp": "p", "per": "3", "gen": "m", "num": "s"},
    {"role": "present_3ms", "form": "يَقُول",
     "in_corpus": true, "count": 2020,
     "asp": "i", "per": "3", "gen": "m", "num": "s"},
    "..."
  ],
  "frequency_in_corpus": 7066,
  "cross_references": {
    "qac": {"found": true, "lemma_key": "قالَ", "root": "قول",
            "pos": "V", "occurrence_count": 1618},
    "wiktextract": {"found": true, "entry_count": 2,
                    "pos_tags": ["verb"], "has_etymology": false,
                    "sense_count": 7},
    "lanes": {"found": true, "entry_ids": ["n42874", "n42933"]}
  },
  "translations": null,
  "definition": {
    "source": "wiktextract",
    "senses": [
      {"pos": "verb", "gloss": "to say", "examples": [
        {"text": "قَالَ", "english": "He said"}
      ]},
      {"pos": "verb", "gloss": "to tell"},
      "..."
    ]
  },
  "etymology": null,
  "ipa": ["/qaː.la/", "/ɡaːl/"]
}
```

#### Field reference — lemma page

| Field | Meaning |
|---|---|
| `lemma` | Diacritized lemma (citation form). For verbs: past 3rd-person masculine singular. For nouns: singular nominative. |
| `slug` | NFC-normalized `lemma`. Same as the filename. |
| `root`, `pos`, `pos_camel` | Same semantics as the surface page (see above). |
| `root_slug` | URL-safe form of `root`: `.` → `-` and `#` → `_`. E.g. `ق.#.ل` → `ق-_-ل`. Used as the filename for the root page. |
| `root_link` | Path the UI navigates to for the underlying root page (`/words/roots/{root_slug}`). Use this to fetch the list of sibling lemmas. |
| `paradigm[]` | Full conjugation/declension table generated by CAMeL Tools — **every** form the lemma could produce, regardless of whether it appears in the corpus. Used by the UI to render a complete table while highlighting the attested forms. |
| `paradigm[].role` | Structural role label, e.g. `past_3ms` (past 3rd-person masc sing), `present_3fp` (present 3rd-person fem plur), `imperative_2ms`, `verbal_noun`, `active_participle`, `passive_participle`. |
| `paradigm[].form` | NFC-normalized form (same as the surface-page slug if attested). |
| `paradigm[].in_corpus` | `true` if this form (or a diacritization variant of it) appears anywhere in the hadith corpus. |
| `paradigm[].count` | Total corpus occurrences when `in_corpus` is true; otherwise `null`. |
| `paradigm[].asp` | Aspect: `p` past / `i` present / `c` imperative / `na` (not a verb). |
| `paradigm[].per` | Person: `1`, `2`, `3`, `na`. |
| `paradigm[].gen` | Gender: `m` masculine / `f` feminine / `c` common / `na`. |
| `paradigm[].num` | Number: `s` singular / `d` dual / `p` plural / `na`. |
| `frequency_in_corpus` | Sum of every paradigm form's `count` (where `in_corpus` is true). Equals total corpus occurrences of this lemma across all its inflections. |
| `cross_references.qac` | Lookup in the Quranic Arabic Corpus v0.4. `found`, `lemma_key` (the QAC's spelling), `root`, `pos`, and `occurrence_count` (how often the lemma appears in the Quran). |
| `cross_references.wiktextract` | Lookup in Wiktionary's Arabic dump. `found`, `entry_count`, `pos_tags` (Wiktionary's POS labels), `has_etymology`, `sense_count` (number of distinct definitions). |
| `cross_references.lanes` | Lookup in Lane's Arabic-English Lexicon. `found`, `entry_ids` (Perseus entry IDs), `search_url` (link to a lanelexicon.com WordPress search for this lemma — no stable per-entry deep linking is available on any Lane's viewer). |
| `translations` | **Null for now.** Wiktionary's Arabic-side entries don't carry foreign-language translations; the LLM phase will fill the 10 non-English target languages. |
| `definition` | Populated from Wiktextract when the lemma has a Wiktionary entry (~76% of lemmas). Shape: `{source: "wiktextract", senses: [{pos, gloss, tags?, examples?}, ...]}`. `gloss` is the English definition string; `examples` are capped at 2 per sense; `pos` distinguishes verb/noun senses when the same headword has both. **Null** when no Wiktionary entry — those go to the LLM augmentation pass. |
| `etymology` | Populated from Wiktextract `etymology_text` when present (~50% of Wikt-attested lemmas have etymology). Shape: `{source: "wiktextract", text: "..."}`. Multi-paragraph when different POS entries carry different etymologies. **Null** otherwise. |
| `ipa` | IPA pronunciation strings from Wiktextract `sounds[].ipa`, deduplicated. Multiple entries reflect dialect variation (Egyptian /ɡaːl/, MSA /qaːla/, etc.). **Null** when Wiktionary has no pronunciation data. |
| `lanes_definition` | Populated from Lane's Arabic-English Lexicon (Perseus TEI XML) when the lemma matches at least one Lane's entry (~67% of lemmas). Shape: `{source: "lanes", entries: [{entry_id, headword_ar, root, body, source_refs}, ...]}`. Multiple entries reflect homographs (e.g. قالَ "to say" + قالَ "to nap" are separate Lane's entries). `body` is an **uncapped** ordered list of typed segments (see "Lane's body segments" below); `source_refs` are the abbreviations Lane's used to cite his sources (see "Lane's source-citation legend" below). **Null** when the lemma has no Lane's entry. |
| `classical_definitions` | Populated from hawramani.com which aggregates entries from **38 classical Arabic lexicons** per Arabic word (al-Mufradat of al-Raghib, Lisan al-Arab, Taj al-'Arus, Sihah, Asas al-Balagha, Misbah al-Munir, Qamus, Mughrib, Mufradat (Farahi), and more). Shape: `{source: "hawramani", url, headword_ar, entries: [{lexicon_id, lexicon_en, lexicon_ar, permalink, body_html}, ...]}`. The `body_html` is **sanitized HTML** (allowlist: p/b/i/em/u/span/div/a/ul/ol/li/br/sup/sub — script/style/iframe/event-handlers stripped) safe to render with `[innerHTML]`. The `permalink` field is a deep link to the specific entry on hawramani; `url` is the lemma's hawramani page. `lexicon_id` is a stable code (`dictionary_31` = al-Mufradat, `dictionary_1` = Lisan al-Arab, etc.) — see "hawramani lexicon legend" below for the full mapping. **Null** when no hawramani entry exists for the lemma (after diacritic-strip URL slug lookup). |

`root` uses CAMeL Tools' notation, with `#` standing in for hollow / weak
radicals (`ق.#.ل` = root ق-و-ل for the verb "to say"). UI should map this
to a friendlier display form before rendering. The URL-safe `root_slug`
is what to use as a slug or filename.

### Root page (`roots/{slug}.json`)

A root (e.g. ق-و-ل) is the consonantal backbone shared by a family of
lemmas. The root page lists all lemmas in our corpus derived from it.

```json
{
  "root": "ق.#.ل",
  "slug": "ق-_-ل",
  "lemmas": [
    {"slug": "قالَ", "pos": "V", "frequency": 7066},
    {"slug": "أَقالَ", "pos": "V", "frequency": 123},
    {"slug": "قاوَلَ", "pos": "V", "frequency": 4},
    {"slug": "قَوْل", "pos": "N", "frequency": 200},
    "..."
  ],
  "lemma_count": 18,
  "total_frequency": 7393,
  "translations": null,
  "definition": null,
  "etymology": null
}
```

#### Field reference — root page

| Field | Meaning |
|---|---|
| `root` | CAMeL Tools root string (e.g. `ق.#.ل`), `#` for weak/hollow radicals. |
| `slug` | URL-safe form. `.` → `-`, `#` → `_` (the underscore is safe because it never appears in CAMeL roots and so can't collide with a real root). |
| `lemmas[]` | Every lemma derived from this root in our corpus, sorted by descending corpus frequency. Each entry: `slug`, `pos`, `frequency`. The UI fetches the lemma page for the actual paradigm + cross-references. |
| `lemma_count` | `len(lemmas)`. |
| `total_frequency` | Sum of all lemma corpus frequencies under this root. |
| `translations` / `definition` / `etymology` | **Null for now.** Reserved for a future LLM pass that will produce a "core meaning of the root" gloss shared across all lemmas (cheaper than per-lemma definitions for the rarer derivations). |

### Index files (`index/surfaces.json`, `index/lemmas.json`, `index/roots.json`)

Each is a `{ total: number, items: ItemEntry[] }` envelope (key is `surfaces`/`lemmas`/`roots`). Sorted by descending frequency so paginated or capped views default to the most-useful entries.

**`index/surfaces.json` entry** — `{ slug, count, lemma, pos }`. `lemma` is null for surfaces CAMeL couldn't analyze (proper nouns, foreign chars).

**`index/lemmas.json` entry** — `{ slug, root, root_slug, pos, gloss, frequency, paradigm_size, in_corpus_forms, has_qac, has_wiktextract, has_lanes }`.
- **`gloss`** — *Temporary, English-only.* The first Wiktextract sense gloss aligned with the lemma's POS, truncated to 80 chars (ellipsis on overflow). Picked by `_pick_aligned_gloss` in `scripts/build_word_indexes.py` using a POS-family map so homographs return the right sense (e.g. `إِلَى` returns `""` because no preposition sense exists in Wiktextract — better than returning the verb sense "to promise"). Empty string for function-word lemmas without an aligned sense. **This field will be replaced by a multi-language `glosses: {en, ar, fa, ur, …}` object once the Path B LLM-translation step runs.** Consumers should fall back gracefully when it's empty.
- `has_qac` / `has_wiktextract` / `has_lanes` — boolean availability flags so a UI can pre-filter by source without fetching the lemma page.
- `paradigm_size` / `in_corpus_forms` — gives a quick "how thoroughly attested" feel before opening the page.

**`index/roots.json` entry** — `{ slug, root, lemma_count, total_frequency }`.

### Clitic taxonomy

Arabic words frequently combine a stem with affixes (clitics):
proclitics attached **before** the stem (e.g. `وَ-`, `بِ-`, `الْ-`)
and enclitics attached **after** (e.g. `-هُ`, `-هَا`, `-كَ`). CAMeL Tools
detects up to four proclitic positions and up to two enclitic
positions, ordered by distance from the stem:

```
[prc3] [prc2] [prc1] [prc0]  STEM  [enc0] [enc1]
```

`prc0` is the proclitic nearest the stem (e.g. the definite article
`ال`); `prc3` is furthest. Same convention for enclitics: `enc0`
nearest the stem. A field is omitted from the JSON when no clitic
is present in that slot.

**Proclitic values commonly seen in the corpus:**

| Slot | Code | Form | Meaning |
|---|---|---|---|
| `prc0` | `Al_det` | الْ | definite article |
| `prc0` | `lA_neg` | لَا | negative |
| `prc0` | `mA_neg` | مَا | negative |
| `prc0` | `mA_rel` | مَا | relative "what" |
| `prc1` | `bi_prep` | بِ | preposition "by/with/in" |
| `prc1` | `ka_prep` | كَ | preposition "like" |
| `prc1` | `li_prep` | لِ | preposition "to/for" |
| `prc1` | `li_jus` | لِ | jussive (verbs) |
| `prc1` | `li_sub` | لِ | subordinator |
| `prc1` | `sa_fut` | سَ | future-tense marker |
| `prc2` | `wa_conj` | وَ | conjunction "and" |
| `prc2` | `fa_conj` | فَ | conjunction "and then / so" |
| `prc2` | `wa_sub` | وَ | subordinating "and" |
| `prc2` | `fa_sub` | فَ | subordinating "so/then" |
| `prc3` | `Aa_ques` | أَ | question particle |

**Enclitic values: pronominal suffixes attached to the stem.** The
code form is `{person}{gender}{number}_{role}`:

| Code | Form | Meaning |
|---|---|---|
| `1s_dobj` / `1s_poss` / `1s_pron` | ـنِي / ـِي | "me" / "my" |
| `1p_dobj` / `1p_poss` / `1p_pron` | ـنَا | "us" / "our" |
| `2ms_dobj` / `2ms_poss` / `2ms_pron` | ـكَ | "you" / "your" (m sg) |
| `2fs_dobj` / `2fs_poss` / `2fs_pron` | ـكِ | "you" / "your" (f sg) |
| `2mp_dobj` / `2mp_poss` / `2mp_pron` | ـكُمْ | "you" / "your" (m pl) |
| `2fp_dobj` / `2fp_poss` / `2fp_pron` | ـكُنَّ | "you" / "your" (f pl) |
| `3ms_dobj` / `3ms_poss` / `3ms_pron` | ـهُ | "him/it" / "his" / "him" (after prep) |
| `3fs_dobj` / `3fs_poss` / `3fs_pron` | ـهَا | "her/it" / "her" |
| `3mp_dobj` / `3mp_poss` / `3mp_pron` | ـهُمْ | "them" / "their" (m) |
| `3fp_dobj` / `3fp_poss` / `3fp_pron` | ـهُنَّ | "them" / "their" (f) |
| `3d_dobj` / `3d_poss` / `3d_pron` | ـهُمَا | "them two" (dual) |

The `_dobj` / `_poss` / `_pron` suffix is CAMeL's role label and depends on what the
suffix is attached to:
- on a **verb** → direct object (`_dobj`): `قَالَهُ` "he said it"
- on a **noun** → possessor (`_poss`): `كِتَابُهُ` "his book"
- on a **preposition** → object of preposition (`_pron`): `لَهُ` "to him"

So in the example you asked about:

```json
"clitics": { "enc0": "3ms_dobj" }
```

means the stem has a 3rd-person-masculine-singular pronominal suffix
attached as a direct object — i.e., `-هُ` "him/it" attached to a verb.
For instance `قَالَهُ` ("he said it") would decompose as:
- stem: `قَالَ` (the verb "he said")
- `enc0`: `3ms_dobj` → `-هُ` ("it")

A surface like `وَقَالَهُ` ("and he said it") would have both:

```json
"clitics": {
  "prc2": "wa_conj",   // وَ "and"
  "enc0": "3ms_dobj"   // ـهُ "it"
}
```

The UI uses this decomposition to render each component as a separate
clickable card linking to its respective lemma page (the conjunction
`وَ` has its own lemma, as does the pronoun `هُو`/`هُ`, and the verb
`قالَ`).

## Local development

```bash
python serve.py        # starts http://localhost:8889/
```

Then the Angular UI's `WordsService` (in
`Thaqalayn/src/app/services/`) is wired to read from
`environment.wordsApi = "http://localhost:8889/"` in dev (and
`https://thaqalaynwords.netlify.app/` in prod).

## Regenerating

In `ThaqalaynDataGenerator/`:

```bash
# Build all pages (full corpus, ~102K surfaces, ~30 min)
python scripts/build_word_pages.py --full

# Or a sample for quick iteration
python scripts/build_word_pages.py --top-n 100

# After build: indexes + validation
python scripts/build_word_indexes.py
python scripts/validate_word_pages.py --strict
```

The build is deterministic — no LLM calls. Source data comes from
`ThaqalaynWordSources/`.

## Lane's body segments

When `lanes_definition` is populated, each entry's `body` is an ordered
list of typed segments (no truncation — full content from Lane's TEI XML
is preserved). The UI walks them in order and renders by `kind`:

| `kind` | Shape | Render guidance |
|---|---|---|
| `italic_en` | `{kind: "italic_en", text: "..."}` | English definition / commentary. Display in italics. The semantic body of Lane's entries — i.e., the actual definitions. |
| `arabic` | `{kind: "arabic", text_ar: "...", text_bw: "...", orth_type?: "plain"\|"arrow"}` | Embedded Arabic word (e.g., a derived form or cross-reference). `text_ar` is the NFC Arabic; `text_bw` is the original Buckwalter. `orth_type: "arrow"` means Lane used an ↓ marker preceding the form (he uses this for alternative orthographic forms — the UI can render it with a `↓` prefix or different styling). |
| `text` | `{kind: "text", text: "..."}` | Connective prose between elements, including parenthesized source-citation strings like `(S, K,) or` and `(M:)`. Display as normal text. |
| `quote` | `{kind: "quote", text: "..."}` | Occasional `<quote>` blocks (rare). Display as a quote. |
| `page_break` | `{kind: "page_break", n: 42}` | Marks a printed-page boundary in Lane's 1863 edition. Useful for citations like "see Lane Vol. 3, p. 42". Render inline as a faint page-number marker, or omit visually. |

## Lane's source-citation legend

Throughout the body of each Lane's entry, citations appear in parentheses
like `(S, K, TA:)` or `(Msb:)`. The `source_refs` array on each entry
collects every code mentioned, deduplicated, in order of first appearance.
Here are the most-common codes and what they reference:

| Code | Reference |
|---|---|
| `S` | Sihah — al-Jawhari, *al-Sihah* |
| `K` | Kamoos — al-Firuzabadi, *al-Qamus al-Muhit* |
| `M` | Muhkam — Ibn Sida, *al-Muhkam* |
| `TA` | Taj al-'Arus — al-Zabidi (commentary on Kamoos) |
| `T` | Tahdhib — al-Azhari, *Tahdhib al-Lughah* |
| `L` | Lisan al-'Arab — Ibn Manzur |
| `A` | Asas al-Balaghah — al-Zamakhshari |
| `O` | Ubab — al-Saghani, *al-'Ubab al-Zakhir* |
| `Msb` | Misbah al-Munir — al-Fayyumi |
| `Mgh` | Mughrib — al-Mutarrizi, *al-Mughrib fi Tartib al-Mu'rib* |
| `MA` | Mukhassas — Ibn Sida |
| `JK` | Jamharah — Ibn Durayd, *Jamharat al-Lughah* |
| `IF` | Mu'jam Maqayis al-Lughah — Ibn Faris |
| `Nh` | Nihayah — Ibn al-Athir, *al-Nihayah fi Gharib al-Hadith* |
| `AHn` | Abu Hanifah al-Dinawari |
| `IB` | Ibn Barri |
| `IAar` | Ibn al-A'rabi |
| `IDrd` | Ibn Durayd |
| `ISd` | Ibn al-Sikkit (or Ibn al-Sayyid) |
| `IJ` | Ibn Jinni |
| `IAth` | Ibn al-Athir |
| `Az` | al-Azhari |
| `Fr` | al-Farra' |
| `Akh` | al-Akhfash |
| `Sb` | Sibawayh |
| `Ks` | al-Kisa'i |
| `Lh` | Abu al-Hasan al-Lihyani |
| `AZ` | Abu Zayd |
| `AO` | Abu 'Ubayd |

(The full legend is in
`ThaqalaynDataGenerator/app/words/lanes.py` as
`SOURCE_CITATION_LEGEND`; the UI can import it for display.)

## hawramani lexicon legend

When `classical_definitions.entries[]` is populated, each entry carries
a `lexicon_id` like `dictionary_31`. The full mapping of these IDs to
the underlying classical Arabic lexicons:

| `lexicon_id` | English | Arabic |
|---|---|---|
| `dictionary_1` | Ibn Manẓūr, *Lisān al-ʿArab* (d. 1311 CE) | لسان العرب لابن منظور |
| `dictionary_3` | al-Khalīl b. Aḥmad al-Farāhīdī, *Kitāb al-ʿAin* (d. c. 786 CE) | كتاب العين |
| `dictionary_4` | Abū ʿUbayd, *Gharīb al-Ḥadīth* | غريب الحديث لأبي عبيد |
| `dictionary_5` | Ghulām Thaʿlab, *al-ʿAsharāt fī Gharīb al-Lugha* | العشرات في غريب اللغة |
| `dictionary_6` | al-Jawharī, *Tāj al-Lugha wa Ṣiḥāḥ al-ʿArabiyya* (Sihah) | الصحاح للجوهري |
| `dictionary_7` | Ibn Fāris, *Maqāyīs al-Lugha* (d. 1004 CE) | مقاييس اللغة |
| `dictionary_8` | Ibn Sīda, *al-Muḥkam wa-l-Muḥīṭ al-Aʿẓam* | المحكم |
| `dictionary_9` | al-Zamakhsharī, *Asās al-Balāgha* (d. 1143 CE) | أساس البلاغة |
| `dictionary_10` | Abū Mūsā al-Madīnī, *al-Majmūʿ al-Mughīth* | المجموع المغيث |
| `dictionary_11` | Ibn al-Athīr, *al-Nihāya fī Gharīb al-Ḥadīth* | النهاية في غريب الحديث |
| `dictionary_12` | al-Muṭarrizī, *al-Mughrib fī Tartīb al-Muʿrib* | المغرب |
| `dictionary_13` | al-Ṣaghānī, *al-Shawārid* | الشوارد |
| `dictionary_14` | al-Razī, *Mukhtār al-Ṣiḥāḥ* | مختار الصحاح |
| `dictionary_15` | Ibn Mālik, *al-Alfāẓ al-Mukhtalifa* | الألفاظ المختلفة |
| `dictionary_16` | Abu Ḥayyān al-Gharnāṭī, *Tuḥfat al-Arīb* | تحفة الأريب |
| `dictionary_17` | al-Fayyūmī, *al-Miṣbāḥ al-Munīr* | المصباح المنير |
| `dictionary_18` | al-Sharīf al-Jurjānī, *Kitāb al-Taʿrīfāt* | كتاب التعريفات |
| `dictionary_19` | Firuzabadi, *al-Qāmūs al-Muḥīṭ* (Kamoos) | القاموس المحيط |
| `dictionary_20` | al-Suyūṭī, *Muʿjam Maqālīd al-ʿUlūm* | معجم مقاليد العلوم |
| `dictionary_21` | al-Fattinī, *Majmaʿ Biḥār al-Anwār* | مجمع بحار الأنوار |
| `dictionary_22` | al-Munāwī, *al-Tawqīf ʿalā Muhimmāt al-Taʿārīf* | التوقيف على مهمات التعاريف |
| `dictionary_23` | Aḥmadnagarī, *Dastūr al-ʿUlamāʾ* | دستور العلماء |
| `dictionary_24` | al-Tahānawī, *Kashshāf Iṣṭilāḥāt al-Funūn* | كشاف اصطلاحات الفنون |
| `dictionary_25` | Murtaḍa al-Zabīdī, *Tāj al-ʿArūs* | تاج العروس |
| `dictionary_27` | al-Barakatī, *al-Taʿrīfāt al-Fiqhīya* | التعريفات الفقهية |
| `dictionary_29` | Ibn al-Tustarī, *al-Mudhakkar wa-l-Muʾannath* | المذكر والمؤنث |
| `dictionary_31` | **al-Rāghib al-Isfahānī, *al-Mufradāt fī Gharīb al-Qurʾān*** | المفردات للراغب الأصفهاني |
| `dictionary_32` | Reinhart Dozy, *Supplément aux dictionnaires arabes* | تكملة المعاجم |
| `dictionary_36` | al-Ṣāḥib bin ʿAbbād, *al-Muḥīṭ fī l-Lugha* | المحيط في اللغة |
| `dictionary_37` | al-Ṣaghānī, *al-ʿUbāb al-Dhākhir wa-l-Lubāb al-Fākhir* | العباب الزاخر |
| `dictionary_38` | Hamiduddin Farahi, *Mufradāt al-Qurʾān* (d. 1930 CE) | مفردات القرآن للفراهي |
| `dictionary_39` | ʿAbdullāh ibn ʿAbbās, *Gharīb al-Qurʾān fī Shiʿr al-ʿArab* | غريب القرآن لابن عباس |
| `dictionary_40` | al-Suyūṭī, *al-Muhadhdhib fīmā Waqaʿa fi l-Qurʾān min al-Muʿarrab* | المهذب للسيوطي |
| `dictionary_46` | Dictionary of Arabic Baby Names (2009) | |
| `dictionary_48` | Sultan Qaboos Encyclopedia of Arab Names | موسوعة السلطان قابوس |
| `dictionary_49` | Edward William Lane, *Arabic-English Lexicon* (note: same Lane's as `lanes_definition` above; included here for cross-checking) | معجم لين |
| `dictionary_51` | Habib Anthony Salmone, *An Advanced Learner's Arabic-English Dictionary* | قاموس سالمون |
| `dictionary_52` | Yāqūt al-Ḥamawī, *Muʿjam al-Buldān* | معجم البلدان |

The full programmatic mapping is in
`ThaqalaynDataGenerator/app/words/hawramani.py` as
`LEXICON_LEGEND`. New `dictionary_N` IDs will appear in output even
if not yet in the legend — the legend is purely a display
convenience.

## License & attribution

This repository contains data derived from:

- **Wiktionary** (CC-BY-SA 4.0) via Wiktextract / Kaikki.org
- **Lane's Arabic-English Lexicon** (Perseus Digital Library, public
  domain)
- **Quranic Arabic Corpus v0.4** (free; see source for attribution)
- **CAMeL Tools** morphology (MIT; calima-msa-r13 DB is GPL v2)

Generated content is licensed CC-BY-SA 4.0 for compatibility with the
Wiktionary upstream.
