import unittest
from pipes.DependencyParser import DependencyParser
from pipes.util.NLP_Parser.spacyParser import SpacyParser
from pipes.util.vis_dependency import visualize_pos


class MyTestCase(unittest.TestCase):
    def test_one(self):
        text = 'The fleet left Spain on 20 September 1519, sailing west across the Atlantic toward South America.'
        sent = SpacyParser().spacy_parse(text=text, lang='en')
        parser = DependencyParser(text, 'en')
        visualize_pos(sent, 'magellan', '1')
        found_comp = parser.parse_sentence(sent)
        self.assertEqual(len(found_comp), 1)


if __name__ == '__main__':
    unittest.main()
