import unittest
from pipes.DependencyParser import DependencyParserDE
from pipes.util.NLP_Parser.spacyParser import SpacyParser


class MyTestCase(unittest.TestCase):
    def test_de_simple(self):
        text = 'Sepideh liebt Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(1, len(found_comp))


if __name__ == '__main__':
    unittest.main()
