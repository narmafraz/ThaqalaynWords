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
├── index/             browse / autocomplete indexes
│   ├── surfaces.json  flat list (slug, count, lemma, pos)
│   └── lemmas.json    flat list (slug, root, pos, frequency, refs)
├── serve.py           CORS-enabled dev HTTP server on :8889
└── netlify.toml       deployment config (CORS + immutable cache)
```

Slugs are diacritized Arabic NFC. URLs use percent-encoded UTF-8.

## Page shapes

### Surface page (`surfaces/{slug}.json`)

```json
{
  "surface": "وَقَالَ",
  "slug": "وَقَالَ",
  "occurrence_count": 1515,
  "occurrence_paths": ["/books/al-kafi:1:1:1:1", "..."],
  "morphology": {
    "lex": "قال",
    "lemma_slug": "قالَ",
    "root": "ق.#.ل",
    "pos": "V",
    "pos_camel": "verb",
    "clitics": {"prc2": "wa_sub"}
  },
  "lemma_link": "/words/lemmas/قالَ"
}
```

`morphology` is null for unanalyzable surfaces (proper nouns / Latin
gibberish / completely unknown tokens) — typically ~3% of the corpus.

### Lemma page (`lemmas/{slug}.json`)

```json
{
  "lemma": "قالَ",
  "slug": "قالَ",
  "root": "ق.#.ل",
  "pos": "V",
  "pos_camel": "verb",
  "paradigm": [
    {"role": "past_3ms", "form": "قالَ", "diacritized": "قالَ",
     "in_corpus": true, "count": 14, ...},
    ...
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
  "definition": null,
  "etymology": null
}
```

The three nullable fields are filled by a separate LLM phase
(`translations`, `definition`, `etymology`). The deterministic part of
the pipeline writes them as `null`.

`root` uses CAMeL Tools' notation, with `#` standing in for hollow / weak
radicals (`ق.#.ل` = root ق-و-ل for the verb "to say"). UI should map this
to a friendlier display form before rendering.

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
