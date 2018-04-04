from unittest import TestCase

from pastebiner.syntax_formats import SyntaxHighlighting


class TestSyntaxHighlighting(TestCase):
    def setUp(self):
        self.syntax = SyntaxHighlighting()

    def test_format_python_variable(self):
        """Should be possible to use FORMAT_PYTHON to get python value"""
        self.assertEqual(self.syntax.FORMAT_PYTHON, 'python')

    def test_format_6502acme_variable(self):
        """Should be possible to use FORMAT_6502ACME to get 6502acme value"""
        self.assertEqual(self.syntax.FORMAT_6502ACME, '6502acme')
