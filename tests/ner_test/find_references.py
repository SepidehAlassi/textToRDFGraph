import unittest
from pipes.NamedEntityResognizer import FlairNERParser
from pipes.PreProcessor import Input


class ReferenceTests(unittest.TestCase):
    def test_ner_locations(self):
        parser = FlairNERParser()
        inputs = Input(text="""In 1684 Jacob Bernoulli travelled to Geneva together with Mr Federich Frey. 
                         Mr. Frey was a nobel man from Geneva. They first rode with horse from Sassel to Liestal.""")
        locations, persons = parser.extract_ne(inputs)
        self.assertEqual(len(locations), 4)  # add assertion here

    def test_ner_persons(self):
        parser = FlairNERParser()
        inputs = Input(text="""In 1684 Jacob Bernoulli travelled to Geneva together with Mons. Johann Jakob Frey. 
                         Mr. Frey was a nobel man from Geneva. They first rode with horse from Sassel to Liestal.""")
        locations, persons = parser.extract_ne(inputs)
        self.assertEqual(len(persons), 3)  # add assertion here


if __name__ == '__main__':
    unittest.main()
