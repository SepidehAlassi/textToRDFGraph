import unittest
import os
from pipes.WikiInformationRetriever import get_required_wiki_props, make_wiki_person_query_sparql
import rdflib.term

from pipes.PreProcessor import parse_ontology

test_onto_path = os.path.join('..', '..', 'inputs', 'example_onto.ttl')
graph = parse_ontology(test_onto_path)
namespaces = dict(graph.namespaces())


class CustomOntoTest(unittest.TestCase):
    def test_existence_of_custom_property(self):
        sparql_statement = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                PREFIX nlpg:     <http://www.NLPGraph.com/ontology/>  
                PREFIX owl: <http://www.w3.org/2002/07/owl#> 
                ASK {
                    ?prop a owl:DatatypeProperty ;
                          rdfs:subPropertyOf ?wikiProp .   
                    FILTER (strstarts(str(?wikiProp), 'http://www.wikidata.org/prop/direct/'))
                }
            """

        bool_answer = graph.query(sparql_statement).askAnswer
        self.assertTrue(bool_answer)

    def test_getting_custom_wiki_location_properties(self):
        props = get_required_wiki_props(graph, "Location")
        expected_dict = {'geoName': {'wikidata': 'wdt:P1566', 'prop_QName': 'nlpg:geoName'},
                         'population': {'wikidata': 'wdt:P1082', 'prop_QName': 'ex:population'}
                         }

        self.assertEqual(props, expected_dict)

    def test_getting_custom_wiki_person_properties(self):
        props = get_required_wiki_props(graph, "Person")
        expected_dict = {'gnd': {'wikidata': 'wdt:P227', 'prop_QName': 'nlpg:gnd'},
                         'birthDate': {'wikidata': 'wdt:P569', 'prop_QName': 'ex:birthDate'},
                         'deathDate': {'wikidata': 'wdt:P570', 'prop_QName': 'ex:deathDate'},
                         }
        self.assertEqual(props, expected_dict)

    def test_person_query(self):
        wiki_props = {'gender': {'wikidata': 'wdt:P21', 'prop_QName': "schema:gender"},
                      'givenName': {'wikidata': 'wdt:P735', 'prop_QName': "schema:givenName"},
                      'familyName': {'wikidata': 'dt:P734', 'prop_QName': "schema:familyName"}}
        extra_props = get_required_wiki_props(graph, "Person")
        wiki_props.update(extra_props)
        sparql_statement = make_wiki_person_query_sparql(name="Leonhard Euler", lang="de", wiki_props=wiki_props)
        self.assertTrue(len(sparql_statement) != 0)


if __name__ == '__main__':
    unittest.main()
