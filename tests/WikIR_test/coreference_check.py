import unittest
from pipes.NamedEntityResognizer import FlairNERParser
from pipes.WikiInformationRetriever import add_wiki_info_person
from pipes.PreProcessor import Input


class MyTestCase(unittest.TestCase):
    def test_checking_vicinity(self):
        parser = FlairNERParser()
        inputs = Input(text="""In 1684 Jacob Bernoulli travelled to Hanover. Mr. Bernoulli was a mathematician. 
                                Jacob travelled in pursue of knowledge.""")
        locations, persons = parser.extract_ne(inputs)
        found_persons, _ = add_wiki_info_person(persons, inputs)
        addressed_ref = found_persons[1]
        firstname_ref = found_persons[2]
        self.assertTrue(addressed_ref.gnd == found_persons[0].gnd and firstname_ref.gnd == found_persons[0].gnd)  # add assertion here

    def testing_vicinity_nearest_neighbour(self):
        parser = FlairNERParser()
        inputs = Input(text="""In 1690s, Jacob Bernoulli taught mathematics to his brother Johann Bernoulli. Mr. Bernoulli was the brightest of mathematicians. """)
        locations, persons = parser.extract_ne(inputs)
        found_persons, _ = add_wiki_info_person(persons, inputs)
        addressed_ref = found_persons[2]

        self.assertTrue(addressed_ref.gnd == found_persons[1].gnd)  # add assertion here

    def testing_person_with_no_wiki(self):
        parser = FlairNERParser()
        inputs = Input(
            text="""Sepideh Alassi is sick of academic politics.""")
        locations, persons = parser.extract_ne(inputs)
        found_persons, _ = add_wiki_info_person(persons, inputs)
        addressed_ref = found_persons[0]
        self.assertTrue(addressed_ref.gnd == '' and addressed_ref.local_id != '')  # add assertion here


if __name__ == '__main__':
    unittest.main()
