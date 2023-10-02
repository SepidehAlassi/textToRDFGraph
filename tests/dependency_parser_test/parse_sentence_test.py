import unittest
from pipes.DependencyParser import DependencyParser
from pipes.util.NLP_Parser.spacyParser import SpacyParser
from pipes.util.vis_dependency import visualize_pos


class MyTestCase(unittest.TestCase):
    def test_advpl_in_sentence(self):
        text = 'Ferdinand Magellan left Spain on 20 September 1519, sailing west across the Atlantic toward South America.'
        sent = SpacyParser().spacy_parse(text=text, lang='en')
        parser = DependencyParser(text, 'en')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(3, len(found_comp))

    def test_conj_objects(self):
        text = 'Ferdinand Magellan traveled to Argentina, Portugal, Brazil, and United States.'
        sent = SpacyParser().spacy_parse(text=text, lang='en')
        parser = DependencyParser(text, 'en')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(4, len(found_comp))

    def test_conj_subjects(self):
        text = 'Ferdinand Magellan and Jose Julius traveled to Argentina.'
        sent = SpacyParser().spacy_parse(text=text, lang='en')
        parser = DependencyParser(text, 'en')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(2, len(found_comp))

    def test_conj_subjects_and_objects(self):
        text = 'Ferdinand Magellan and Jose Julius traveled to Argentina, Brazil, and Spain.'
        sent = SpacyParser().spacy_parse(text=text, lang='en')
        parser = DependencyParser(text, 'en')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(6, len(found_comp))

    def test_conj_verb(self):
        text = 'Ferdinand Magellan met and talked to Jose Julius.'
        sent = SpacyParser().spacy_parse(text=text, lang='en')
        parser = DependencyParser(text, 'en')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(2, len(found_comp))

    def test_conj_subjects_objects_verb(self):
        text = 'Ferdinand Magellan and Jose Julius met and talked to Julian Demier.'
        sent = SpacyParser().spacy_parse(text=text, lang='en')
        parser = DependencyParser(text, 'en')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(4, len(found_comp))


if __name__ == '__main__':
    unittest.main()
