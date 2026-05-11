# ThaqalaynWords

Per-word Arabic dictionary for the Thaqalayn hadith corpus. Each surface
form in the corpus has a JSON page; each lemma it maps to has a richer
lemma page with cross-references to classical Arabic lexicons.

See **`Thaqalayn/docs/WORDS_PROJECT_PLAN.md`** for the master plan.

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
| `cross_references.lanes` | Lookup in Lane's Arabic-English Lexicon. `found`, `entry_ids` (Perseus `n` IDs that can be deep-linked to the full lexicon entry). |
| `translations` | **Null for now.** Wiktionary's Arabic-side entries don't carry foreign-language translations; the LLM phase will fill the 10 non-English target languages. |
| `definition` | Populated from Wiktextract when the lemma has a Wiktionary entry (~76% of lemmas). Shape: `{source: "wiktextract", senses: [{pos, gloss, tags?, examples?}, ...]}`. `gloss` is the English definition string; `examples` are capped at 2 per sense; `pos` distinguishes verb/noun senses when the same headword has both. **Null** when no Wiktionary entry — those go to the LLM augmentation pass. |
| `etymology` | Populated from Wiktextract `etymology_text` when present (~50% of Wikt-attested lemmas have etymology). Shape: `{source: "wiktextract", text: "..."}`. Multi-paragraph when different POS entries carry different etymologies. **Null** otherwise. |
| `ipa` | IPA pronunciation strings from Wiktextract `sounds[].ipa`, deduplicated. Multiple entries reflect dialect variation (Egyptian /ɡaːl/, MSA /qaːla/, etc.). **Null** when Wiktionary has no pronunciation data. |

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

## License & attribution

This repository contains data derived from:

- **Wiktionary** (CC-BY-SA 4.0) via Wiktextract / Kaikki.org
- **Lane's Arabic-English Lexicon** (Perseus Digital Library, public
  domain)
- **Quranic Arabic Corpus v0.4** (free; see source for attribution)
- **CAMeL Tools** morphology (MIT; calima-msa-r13 DB is GPL v2)

Generated content is licensed CC-BY-SA 4.0 for compatibility with the
Wiktionary upstream.
