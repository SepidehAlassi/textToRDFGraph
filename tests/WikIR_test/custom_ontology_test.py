import unittest
import os
from pipes.WikiInformationRetriever import *
import rdflib.term

from pipes.PreProcessor import parse_ontology, parse_shacl

test_onto_path = os.path.join(os.path.dirname(__file__), '..', '..', 'inputs', 'beol_onto.ttl')
test_shacl_path = os.path.join(os.path.dirname(__file__), '..', '..', 'inputs', 'beol_shacl.ttl')
onto_graph = parse_ontology(test_onto_path)
shapes_graph = parse_shacl(test_shacl_path)
namespaces = dict(onto_graph.namespaces())


class CustomOntoTest(unittest.TestCase):
    def test_existence_of_custom_property(self):
        sparql_statement = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                PREFIX nlpg: <http://www.NLPGraph.com/ontology/>  
                PREFIX owl: <http://www.w3.org/2002/07/owl#> 
                ASK {
                    ?prop a owl:DatatypeProperty ;
                          rdfs:subPropertyOf ?wikiProp .   
                    FILTER (strstarts(str(?wikiProp), 'http://www.wikidata.org/prop/direct/'))
                }
            """

        bool_answer = onto_graph.query(sparql_statement).askAnswer
        self.assertTrue(bool_answer)

    def test_getting_custom_wiki_location_properties(self):
        props = get_required_wiki_props_from_ontology(onto_graph=onto_graph,
                                                      shapes_graph=shapes_graph,
                                                      entity_type="Location")
        expected_dict = {'geoNameID': {'wikidata': 'wdt:P1566', 'prop_QName': 'nlpg:geoNameID', 'optional': False},
                         'population': {'wikidata': 'wdt:P1082', 'prop_QName': 'ex:population', 'optional': True}
                         }

        self.assertEqual(expected_dict, props)

    def test_getting_wiki_person_properties(self):
        props = get_required_wiki_props_from_ontology(onto_graph=onto_graph,
                                                      shapes_graph=shapes_graph,
                                                      entity_type="Person")
        expected_dict = {'gender': {'wikidata': 'wdt:P21', 'prop_QName': "nlpg:gender", 'optional': False},
                         'givenName': {'wikidata': 'wdt:P735', 'prop_QName': "nlpg:givenName", 'optional': True},
                         'familyName': {'wikidata': 'wdt:P734', 'prop_QName': "nlpg:familyName", 'optional': True},
                         'gnd': {'wikidata': 'wdt:P227', 'prop_QName': 'nlpg:gnd', 'optional': False},
                         'birthDate': {'wikidata': 'wdt:P569', 'prop_QName': 'ex:birthDate', 'optional': False},
                         'deathDate': {'wikidata': 'wdt:P570', 'prop_QName': 'ex:deathDate', 'optional': True},
                         }
        self.assertEqual(expected_dict, props)

    def test_getting_wiki_loc_properties(self):
        props = get_required_wiki_props_from_ontology(onto_graph=onto_graph,
                                                      shapes_graph=shapes_graph,
                                                      entity_type="Location")
        expected_dict = {'geoNameID': {'wikidata': 'wdt:P1566', 'prop_QName': "nlpg:geoNameID", 'optional': False},
                         'population': {'wikidata': 'wdt:P1082', 'prop_QName': "ex:population", 'optional': True}
                         }
        self.assertEqual(expected_dict, props)

    def test_person_query(self):
        wiki_props = get_required_wiki_props_from_ontology(onto_graph=onto_graph,
                                                           shapes_graph=shapes_graph,
                                                           entity_type="Person")
        sparql_statement = make_wiki_query_sparql(name="Leonhard Euler",
                                                  lang="de",
                                                  wiki_props=wiki_props,
                                                  entity_type='person')
        self.assertTrue(len(sparql_statement) != 0)

    def test_location_query(self):
        wiki_props = get_required_wiki_props_from_ontology(onto_graph=onto_graph,
                                                           shapes_graph=shapes_graph,
                                                           entity_type="Location")
        sparql_statement = make_wiki_query_sparql(name="Strait of Magellan",
                                                  lang="en",
                                                  wiki_props=wiki_props,
                                                  entity_type='place')
        self.assertTrue(len(sparql_statement) != 0)


if __name__ == '__main__':
    unittest.main()
