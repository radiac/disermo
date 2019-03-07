"""
Test disermo/util.py
"""
from disermo.utils import camel_to_sentence


class TestCamelToSentence:
    def test_none(self):
        # Invalid when type checking, but test it anyway
        assert camel_to_sentence(None) == ''

    def test_empty(self):
        assert camel_to_sentence('') == ''

    def test_word(self):
        assert camel_to_sentence('word') == 'Word'

    def test_two_words(self):
        assert camel_to_sentence('twoWords') == 'Two words'

    def test_first_capitalised(self):
        assert camel_to_sentence('TwoWords') == 'Two words'

    def test_many_words(self):
        assert camel_to_sentence('thisHasManyWords') == 'This has many words'

    def test_acroynm_start(self):
        assert camel_to_sentence('HTTPServer') == 'HTTP server'

    def test_acroynm_middle(self):
        assert camel_to_sentence('theHTTPServer') == 'The HTTP server'

    def test_acroynm_end(self):
        assert camel_to_sentence('servesHTTP') == 'Serves HTTP'
