import unittest
from pipes.DependencyParser import DependencyParserDE
from pipes.util.NLP_Parser.spacyParser import SpacyParser


class MyTestCase(unittest.TestCase):
    def test_de_simple(self):
        text = 'Sepideh liebt Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_compound_subjects(sent)
        self.assertEqual(sent_comp[0].text, 'Sepideh')

    def test_compound_subject_german_name(self):
        text = 'Albert Einstein wohnte in Zürich.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_compound_subjects(sent)
        self.assertEqual(sent_comp[0].text, 'Albert Einstein')

    def test_compound_subject_nongerman_name(self):
        text = 'Sepideh Alassi arbeitet in Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_compound_subjects(sent)
        self.assertEqual(sent_comp[0].text, 'Sepideh Alassi')

    def test_compound_subject_nongerman_name(self):
        text = 'Sepideh Alassi und Christian Kleinboelting arbeiten in Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_compound_subjects(sent)
        self.assertEqual(len(sent_comp), 2)

    # def test_de_simple(self):
    #     text = 'Sepideh liebt Basel und Paris.'
    #     sent = SpacyParser().spacy_parse(text=text, lang='de')
    #     parser = DependencyParserDE(text, 'de')
    #     found_comp = parser.parse_sentence(sent)
    #     self.assertEqual(2, len(found_comp))



if __name__ == '__main__':
    unittest.main()
