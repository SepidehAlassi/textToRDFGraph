import unittest
from pipes.pron_resolution_pipe import is_resolvable, resolve_pronoun
from Entitiy import PersonEntity
from pipes.NLP_Parsers.spacyParser import SpacyParser
from pipes.dep_parsing_pipe import SentenceComp

jane = PersonEntity(text="Jane Doe",
                     label="PERSON",
                     start_char=19,
                     end_char=34,
                     wiki_id="",
                     lang="en",
                     iri="",
                     document="en_swiss",
                     gnd="118509950",
                     given_name="Jane",
                     family_name="Doe",
                     gender="female")
john = PersonEntity(text="John Doe",
                     label="PERSON",
                     start_char=19,
                     end_char=34,
                     wiki_id="",
                     lang="en",
                     iri="",
                     document="en_swiss",
                     gnd="118509950",
                     given_name="John",
                     family_name="Doe",
                     gender="male")

pers_stack = {0: [john, jane]}

en_test_text = "John is born in Basel. Jane is born in Zurich. She met him 2 years ago."

de_test_text = "Jacob Bernoulli wohnte in Basel. Er reiste nach Lyon."
doc = SpacyParser().spacy_parse(en_test_text)
pronouns = [token for token in doc if token.pos_ == 'PRON']

class PronResolve(unittest.TestCase):
    def test_isResolvable_en_nom(self):
        for token in pronouns:
            morphology = token.morph.to_dict()
            self.assertTrue(is_resolvable(morphology))

    def test_isResolvable_de(self):
        doc = SpacyParser().spacy_parse(de_test_text)
        for token in doc:
            if token.pos_ == 'PRON':
                morphology = token.morph.to_dict()
                self.assertTrue(is_resolvable(morphology))

    def test_isNotResolvable(self):
        text = "Jacob Bernoulli lived in Basel. It is a big city."
        doc = SpacyParser().spacy_parse(text)
        for token in doc:
            if token.pos_ == 'PRON':
                morphology = token.morph.to_dict()
                self.assertFalse(is_resolvable(morphology))

    def test_resolve_pron_en_nom(self):
            pronoun1 = pronouns[0]
            component = SentenceComp(text=pronoun1.text, token=pronoun1)
            resolve_pronoun(pronoun1.morph.to_dict(), component, 2, pers_stack, 'en')
            self.assertEqual(component.entity, jane)

    def test_resolve_pron_en_acc(self):
            pronoun2 = pronouns[1]
            component = SentenceComp(text=pronoun2.text, token=pronoun2)
            resolve_pronoun(pronoun2.morph.to_dict(), component, 2, pers_stack, 'en')
            self.assertEqual(component.entity, john)

if __name__ == '__main__':
    unittest.main()
