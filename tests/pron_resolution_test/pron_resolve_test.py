import unittest
from pipes.PronounResolver import is_resolvable, resolve_pers_pronoun
from Entitiy import PersonEntity
from pipes.util.NLP_Parser.spacyParser import SpacyParser
from pipes.DependencyParser import SentenceComp

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

persons_en = {0: [john, jane]}

en_test_text = "John is born in Basel. Jane is born in Zurich. She met him 2 years ago."
doc_en = SpacyParser().spacy_parse(en_test_text, disable=['ner'])
pronouns_en = [token for token in doc_en if token.pos_ == 'PRON']

john_de = PersonEntity(text="John Doe",
                     label="PERSON",
                     start_char=0,
                     end_char=4,
                     wiki_id="",
                     lang="de",
                     iri="",
                     document="de_swiss",
                     gnd="118509950",
                     given_name="John",
                     family_name="Doe",
                     gender="männlich")

persons_de = {0: [john_de]}
de_test_text = "John wohnte in Basel. Er ist ein junger Mann. Jane hat ihn gestern getroffen."
# de_test_text = "Sepideh arbeitet in Basel. Sie ist eine Große Stadt."
doc_de = SpacyParser().spacy_parse(de_test_text, lang='de', disable=['ner'])
pronouns_de = [token for token in doc_de if token.pos_ == 'PRON']

# dep_svg = displacy.render(doc_de, style="dep")
# filepath = os.path.join(os.getcwd(), '..', '..', "dh2023", "dh2023" + "_dep_vis.svg")
# with open(filepath, "w", encoding="utf-8") as file:
#     file.write(dep_svg)


class PronResolve(unittest.TestCase):
    def test_isResolvable_en_nom(self):
        for token in pronouns_en:
            morphology = token.morph.to_dict()
            self.assertTrue(is_resolvable(morphology))

    def test_isResolvable_de(self):
        for token in pronouns_de:
            if token.pos_ == 'PRON':
                morphology = token.morph.to_dict()
                self.assertTrue(is_resolvable(morphology))

    def test_isNotResolvable_en(self):
        text = "Jammie Fraser lived in Edinburgh. It is a big city."
        doc = SpacyParser().spacy_parse(text)
        for token in doc:
            if token.pos_ == 'PRON':
                morphology = token.morph.to_dict()
                self.assertFalse(is_resolvable(morphology))

    def test_isNotResolvable_de(self):
        text = "John ist in Basel geboren. Jane ist auch in Basel geboren. Sie sind seit Jahren verheiratet."
        doc = SpacyParser().spacy_parse(text)
        for token in doc:
            if token.pos_ == 'PRON':
                morphology = token.morph.to_dict()
                self.assertFalse(is_resolvable(morphology))

    def test_resolve_pron_en_nom(self):
            pronoun1 = pronouns_en[0]
            component = SentenceComp(text=pronoun1.text, token=pronoun1)
            resolve_pers_pronoun(pronoun1.morph.to_dict(), component, 2, persons_en, 'en')
            self.assertEqual(jane, component.entity)

    def test_resolve_pron_de_nom(self):
            pronoun1 = pronouns_de[0]
            component = SentenceComp(text=pronoun1.text, token=pronoun1)
            resolve_pers_pronoun(pronoun1.morph.to_dict(), component, 1, persons_de, 'de')
            self.assertEqual(john_de, component.entity)

    def test_resolve_pron_en_acc(self):
            pronoun2 = pronouns_en[1]
            component = SentenceComp(text=pronoun2.text, token=pronoun2)
            resolve_pers_pronoun(pronoun2.morph.to_dict(), component, 2, persons_en, 'en')
            self.assertEqual(john, component.entity)

    def test_resolve_pron_de_acc(self):
            pronoun2 = pronouns_de[1]
            component = SentenceComp(text=pronoun2.text, token=pronoun2)
            resolve_pers_pronoun(pronoun2.morph.to_dict(), component, 2, persons_de, 'de')
            self.assertEqual(john_de, component.entity)


if __name__ == '__main__':
    unittest.main()
