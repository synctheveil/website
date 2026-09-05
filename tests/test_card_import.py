"""Verify the source snapshot and reject corruption in the prototype tables."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('import_cards', ROOT / 'scripts/import_cards.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CardImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.design = Path(self.temp.name)
        for source in [f'docs/{name}' for name, _, _ in module.SOURCES] + ['scripts/generate_physical_playtest_kit.py']:
            destination = self.design / source
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT.parent / 'design' / source, destination)

    def test_expected_sets_and_source_rules(self):
        cards = module.import_cards(self.design)
        self.assertEqual(len(cards), 86)
        self.assertEqual(sum(c['collection'] == 'Candidate pool' for c in cards), 23)
        self.assertEqual(sum(c['type'] == 'Leader' for c in cards), 4)
        self.assertEqual(sum(c['type'] == 'Junction' for c in cards), 3)
        indexed = {card['id']: card for card in cards}
        self.assertEqual(indexed['NS-O-007']['text'], 'When deployed, you may Shift another friendly ready Operative.')
        self.assertEqual(indexed['HD-P-004']['timing'], 'Action')
        self.assertEqual(indexed['NE-O-002']['entry'], 'Either')
        self.assertNotIn('cost', indexed['leader-ac'])
        self.assertEqual(indexed['leader-ac']['name'], 'Lady Veyra Sorn, Last Creditor')

    def test_rejects_wrong_deck_total(self):
        path = self.design / 'docs/08-starter-decks.md'
        path.write_text(path.read_text().replace('Shrinewire Courier | 3 |', 'Shrinewire Courier | 2 |'))
        with self.assertRaisesRegex(ValueError, 'expected 30 deck cards'):
            module.import_cards(self.design)

    def test_rejects_duplicate_candidate_ids(self):
        path = self.design / 'docs/12-candidate-card-pool.md'
        path.write_text(path.read_text().replace('NE-O-002 |', 'NE-O-001 |'))
        with self.assertRaisesRegex(ValueError, 'Duplicate card identifiers'):
            module.import_cards(self.design)

    def test_rejects_malformed_table(self):
        path = self.design / 'docs/12-candidate-card-pool.md'
        path.write_text(path.read_text().replace('Block Captain | 1 | Street |', 'Block Captain | 1 | Street | unexpected |'))
        with self.assertRaisesRegex(ValueError, 'Unexpected table shape'):
            module.import_cards(self.design)


if __name__ == '__main__':
    unittest.main()
