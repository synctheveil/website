#!/usr/bin/env python3
"""Import prototype card tables without requiring the design repo at Hugo build time."""
import argparse
import ast
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FACTIONS = {'NS': 'Neon Saints', 'HD': 'Helix Dominion', 'AC': 'Ashen Court', 'NA': 'Null Assembly', 'NE': 'Neutral'}
TYPES = {'O': 'Operative', 'P': 'Protocol', 'A': 'Asset'}
SOURCES = [
    ('08-starter-decks.md', 'Starter decks', '0.2'),
    ('11-four-faction-playtest-decks.md', 'Four-faction decks', '0.3'),
    ('12-candidate-card-pool.md', 'Candidate pool', '0.3'),
]


def clean(value):
    return re.sub(r'\s+', ' ', value.replace('**', '').replace('`', '')).strip()


def import_cards(design):
    cards = []
    for filename, collection, version in SOURCES:
        source = f'docs/{filename}'
        lines = (design / source).read_text().splitlines()
        headers = []
        faction = None
        for index, line in enumerate(lines):
            if line.startswith('## '):
                faction = next((name for name in FACTIONS.values() if line.startswith('## ' + name)), None)
            if line.startswith('**Leader:**'):
                rules = []
                for following in lines[index + 1:]:
                    if following.startswith('>'):
                        rules.append(following.lstrip('> '))
                    elif rules:
                        break
                if not rules or not faction:
                    raise ValueError(f'Missing leader rules or faction in {source}')
                prefix = next(key for key, value in FACTIONS.items() if value == faction)
                # Only the printed starter Leaders have source-assigned IDs.
                identifier = f'L-{prefix}-001' if prefix in ('NS', 'HD') else f'leader-{prefix.lower()}'
                cards.append(dict(id=identifier, name=clean(line.split('**Leader:**', 1)[1]), faction=faction,
                                  type='Leader', text=clean(' '.join(rules)), collection=collection,
                                  version=version, source=source))
            if line.startswith('| ID |'):
                headers = [cell.strip() for cell in line.strip('|').split('|')]
            if not re.match(r'^\| (NS|HD|AC|NA|NE)-[OPA]-\d{3} \|', line):
                continue
            cells = [clean(cell) for cell in line.strip('|').split('|')]
            if len(cells) != len(headers):
                raise ValueError(f'Unexpected table shape in {source}: {line}')
            row = dict(zip(headers, cells))
            identifier = row['ID']
            card = dict(id=identifier, name=row['Card'], faction=FACTIONS[identifier[:2]],
                        type=TYPES[identifier.split('-')[1]], collection=collection, version=version,
                        source=source, text=row.get('Rules text', row.get('Timing / rules text', '')))
            for key in ('Cost', 'Power', 'Integrity', 'Copies'):
                if row.get(key, '—') != '—':
                    card[key.lower()] = int(row[key])
            for key in ('Entry', 'Timing'):
                if row.get(key, '—') != '—':
                    card[key.lower()] = row[key]
            # Combined candidate columns retain their full rules text verbatim.
            if card['type'] == 'Protocol' and 'timing' not in card:
                match = re.match(r'^(Action|Reaction) — ', card['text'])
                if match:
                    card['timing'] = match[1]
            cards.append(card)

    # Read the print-kit Junction definition as data; never execute the generator.
    source = 'scripts/generate_physical_playtest_kit.py'
    tree = ast.parse((design / source).read_text())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'junction')
    call = next(node.value for node in function.body if isinstance(node, ast.Return))
    text = ast.literal_eval(next(keyword.value for keyword in call.keywords if keyword.arg == 'text'))
    for number in range(1, 4):
        cards.append(dict(id=f'J-TL-{number:03}', name=f'Textless Junction {number}', faction='Shared',
                          type='Junction', text=text, collection='Starter decks', version='0.2', source=source))

    ids = [card['id'] for card in cards]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate card identifiers')
    for faction in ('Neon Saints', 'Helix Dominion', 'Ashen Court', 'Null Assembly'):
        count = sum(card.get('copies', 0) for card in cards if card['faction'] == faction)
        if count != 30:
            raise ValueError(f'{faction}: expected 30 deck cards, found {count}')
    for card in cards:
        if card['type'] == 'Operative' and not all(key in card for key in ('cost', 'power', 'integrity', 'entry')):
            raise ValueError(f'Missing Operative stats: {card["id"]}')
        if not card['text']:
            raise ValueError(f'Missing rules text: {card["id"]}')
    return sorted(cards, key=lambda card: card['name'].casefold())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('design', nargs='?', type=Path, default=ROOT.parent / 'design')
    parser.add_argument('--check', action='store_true', help='Check the committed snapshot against the source')
    args = parser.parse_args()
    cards = import_cards(args.design)
    output = json.dumps(cards, ensure_ascii=False, indent=2) + '\n'
    target = ROOT / 'data/cards.json'
    if args.check:
        if target.read_text() != output:
            raise SystemExit('Card snapshot differs; run scripts/import_cards.py to update it.')
    else:
        target.write_text(output)
    print(f'{"Verified" if args.check else "Imported"} {len(cards)} card designs.')
