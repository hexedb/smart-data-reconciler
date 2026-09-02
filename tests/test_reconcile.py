import unittest

from data_reconciler.reconcile import reconcile


class ReconcileTests(unittest.TestCase):
    def test_exact_email_match(self) -> None:
        master = [{"name": "Ada Lovelace", "email": "ada@example.com", "phone": "", "company": "Analytical Engines"}]
        incoming = [{"name": "A. Lovelace", "email": "ADA@example.com", "phone": "", "company": "Analytical Engines Ltd"}]
        result = reconcile(master, incoming)
        self.assertEqual(result.matched, 1)
        self.assertIn("exact email", result.rows[0].reasons)

    def test_low_evidence_is_unmatched(self) -> None:
        master = [{"name": "Ada Lovelace", "email": "ada@example.com", "phone": "", "company": "Analytical Engines"}]
        incoming = [{"name": "Grace Hopper", "email": "grace@navy.example", "phone": "", "company": "US Navy"}]
        result = reconcile(master, incoming)
        self.assertEqual(result.unmatched, 1)

    def test_near_tie_is_ambiguous(self) -> None:
        master = [
            {"name": "Sam Lee", "email": "", "phone": "", "company": "Acme"},
            {"name": "Sam Lee", "email": "", "phone": "", "company": "Acme"},
        ]
        incoming = [{"name": "Sam Lee", "email": "", "phone": "", "company": "Acme"}]
        result = reconcile(master, incoming)
        self.assertEqual(result.ambiguous, 1)

    def test_phone_normalization_matches(self) -> None:
        master = [{"name": "John Smith", "email": "", "phone": "+1 415 555 0123", "company": "Northwind"}]
        incoming = [{"name": "Jon Smith", "email": "", "phone": "(415) 555-0123", "company": "Northwind LLC"}]
        result = reconcile(master, incoming)
        self.assertEqual(result.matched, 1)
        self.assertIn("exact phone", result.rows[0].reasons)


if __name__ == "__main__":
    unittest.main()

