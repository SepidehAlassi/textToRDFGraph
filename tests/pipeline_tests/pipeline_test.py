import unittest
import os
from stage2 import entities_fromJson
from pipes.NamedEntityResognizer import FlairNERParser
from pipes.PreProcessor import Input


json_file = os.path.join(os.getcwd(), 'test.json')


class PipelineTest(unittest.TestCase):
    def test_read_entities(self):
        output = entities_fromJson(json_file)
        pers = output['Persons']['118509950'][0]
        self.assertEqual('Jakob', pers.givenName)  # add assertion here

    def find_previous_occurence(self):
        parser = FlairNERParser()
        inputs = Input(text="""In 1684 Jacob Bernoulli travelled to Geneva together with Mr Federich Frey. 
                    Mr. Frey was a nobel man from Geneva. They first rode with horse from Sassel to Liestal.""")
        locations, persons = parser.extract_ne(inputs)
        self.assertEqual(True, True)  # add assertion here

if __name__ == '__main__':
    unittest.main()
