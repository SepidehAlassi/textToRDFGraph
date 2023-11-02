import unittest
from pipes.DependencyParser import DependencyParserDE
from pipes.util.NLP_Parser.spacyParser import SpacyParser


class MyTestCase(unittest.TestCase):
    def test_de_simple_subj(self):
        text = 'Sepideh liebt Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_sent_subjects(sent)
        self.assertEqual(sent_comp[0].text, 'Sepideh')

    def test_de_simple_verb(self):
        text = 'Sepideh liebt Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        verbs = parser.get_sent_verb(sent)
        self.assertEqual(verbs[0].text, 'liebt')

    def test_de_simple_subj(self):
        text = 'Sepideh liebt Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_sent_objects(sent)
        self.assertEqual(sent_comp[0].text, 'Basel')

    def test_compound_subject_german_name(self):
        text = 'Albert Einstein wohnte in Zürich.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_sent_subjects(sent)
        self.assertEqual(sent_comp[0].text, 'Albert Einstein')

    def test_dative_object(self):
        text = 'Albert Einstein wohnte in Zürich.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_sent_objects(sent)
        self.assertEqual(sent_comp[0].text, 'Zürich')

    def test_verb_with_prop_german_name(self):
        text = 'Albert Einstein wohnte in Zürich.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_sent_verb(sent)
        self.assertEqual(sent_comp[0].text, 'wohnte in')

    def test_compound_subject_nongerman_name(self):
        text = 'Sepideh Alassi hat in Basel gearbeitet.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_sent_subjects(sent)
        self.assertEqual(sent_comp[0].text, 'Sepideh Alassi')

    def test_complext_verb(self):
        text = 'Sepideh Alassi hat in Basel gearbeitet.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_sent_verb(sent)
        self.assertEqual(sent_comp[0].text, 'hat gearbeitet in')

    def test_parse_complext_verb(self):
        text = 'Sepideh Alassi hat in Basel gearbeitet.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.parse_sentence(sent)
        self.assertEqual(len(sent_comp), 1)

    def test_compound_subject_nongerman_name(self):
        text = 'Sepideh Alassi und Christian Kleinboelting arbeiten in Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.get_sent_subjects(sent)
        self.assertEqual(len(sent_comp), 2)

    def test_parse_compound_subject_nongerman_name(self):
        text = 'Sepideh Alassi und Christian Kleinboelting arbeiten in Basel.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        sent_comp = parser.parse_sentence(sent)
        self.assertEqual(len(sent_comp), 2)

    def test_de_obj_conj(self):
        text = 'Sepideh liebt Basel und Paris.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        self.assertEqual(2, len(found_comp))

    def test_parse_de_obj_conj(self):
        text = 'Sepideh liebt Basel und Paris.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(2, len(found_comp))

    def test_de_obj_conj_dative(self):
        text = 'Sepideh wohnte in Basel und Paris.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        self.assertEqual(2, len(found_comp))

    def test_parse_de_obj_conj_dative(self):
        text = 'Sepideh wohnte in Basel und Paris.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(2, len(found_comp))

    def test_de_obj_conj_dative(self):
        text = 'Sepideh wohnte in Basel und Paris.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        self.assertEqual(2, len(found_comp))

    def test_parse_de_obj_conj_dative(self):
        text = 'Sepideh wohnte in Basel und Paris.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(2, len(found_comp))

    def test_parse_de_obj_dative_comp(self):
        text = 'Euler wohnte in St Petersburg.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        first_obj = found_comp[0]
        self.assertEqual(first_obj.text, 'St Petersburg')

    def test_parse_de_obj_conj_dative_comp(self):
        text = 'Euler wohnte in St Petersburg und Berlin.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        self.assertEqual(len(found_comp), 2)

    def test_de_obj_conj_enumeration(self):
        text = 'Sepideh verzichtet auf Basel, Bern und Genf.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        self.assertEqual(3, len(found_comp))

    def test_de_obj_compound(self):
        text = 'Sepideh wartet auf Christian Kleinbölting.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        first_obj = found_comp[0]
        self.assertEqual(first_obj.text, 'Christian Kleinbölting')

    def test_de_obj_compound_conj(self):
        text = 'Sepideh wartet auf Christian Kleinbölting und Max Bauer.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        expected_object_texts = ['Christian Kleinbölting', 'Max Bauer']
        returned_obj_texts = [component.text for component in found_comp]
        self.assertEqual(expected_object_texts, returned_obj_texts)

    def test_de_obj_compound_conj_enumeration(self):
        text = 'Sepideh wartet auf Christian Kleinbölting, Samira Alassi und Max Bauer.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.get_sent_objects(sent)
        expected_object_texts = ['Christian Kleinbölting', 'Samira Alassi', 'Max Bauer']
        returned_obj_texts = [component.text for component in found_comp]
        self.assertEqual(expected_object_texts, returned_obj_texts)

    def test_parse_de_obj_conj_enumeration(self):
        text = 'Sepideh verzichtet auf Basel, Bern und Genf.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(3, len(found_comp))
    def test_de_subj_and_obj_conj_enumeration(self):
        text = 'Sepideh, Sara und Christian verzichten auf Basel, Bern und Genf.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_objs = parser.get_sent_objects(sent)
        found_subjs = parser.get_sent_subjects(sent)
        self.assertEqual(6, len(found_objs + found_subjs))

    def test_parse_de_subj_and_obj_conj_enumeration(self):
        text = 'Sepideh, Sara und Christian verzichten auf Basel, Bern und Genf.'
        sent = SpacyParser().spacy_parse(text=text, lang='de')
        parser = DependencyParserDE(text, 'de')
        found_sent_comp = parser.parse_sentence(sent)
        self.assertEqual(9, len(found_sent_comp))


if __name__ == '__main__':
    unittest.main()
