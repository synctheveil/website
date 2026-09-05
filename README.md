# Sync the Veil website

Static Hugo site for the Sync the Veil card game.

The presentation is packaged as the reusable `themes/sync-the-veil` Hugo theme.

## Local development

```sh
mise exec -- hugo server
```

## Production build

```sh
mise exec -- hugo --minify
```

The generated site is written to `public/`.

## Card directory

`/cards/` renders the committed `data/cards.json` snapshot. Cards remain readable
without JavaScript; search and faction/type/set filters progressively enhance
the page. Filter URLs and individual card heading links can be shared.

Update the snapshot from the sibling design repo:

```sh
python3 scripts/import_cards.py
python3 scripts/import_cards.py --check
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

Pass a different design checkout as the positional argument if needed. The importer
reads `docs/08-starter-decks.md`, `docs/11-four-faction-playtest-decks.md`,
`docs/12-candidate-card-pool.md`, and the textless Junction definition in
`scripts/generate_physical_playtest_kit.py`. It validates unique identifiers,
Operative stats, and each faction's 30-card deck total. Hugo builds need only the
snapshot, not the design checkout or Python.

The directory distinguishes starter decks (0.2), four-faction decks (0.3), and
experimental candidates (0.3). Leader anchors for Ashen Court and Null Assembly
are local identifiers; those source documents do not assign printed card IDs.
