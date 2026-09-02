import unittest

from data_reconciler.normalize import company, email, phone, text


class NormalizeTests(unittest.TestCase):
    def test_unicode_and_spacing(self) -> None:
        self.assertEqual(text("  José   García "), "jose garcia")

    def test_email(self) -> None:
        self.assertEqual(email(" Ada@Example.COM "), "ada@example.com")

    def test_phone(self) -> None:
        self.assertEqual(phone("(415) 555-0123"), "14155550123")

    def test_company_suffixes(self) -> None:
        self.assertEqual(company("Northwind Trading, LLC"), "northwind trading")


if __name__ == "__main__":
    unittest.main()

