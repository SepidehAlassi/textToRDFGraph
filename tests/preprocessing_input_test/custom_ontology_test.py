import unittest
import os

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

    def test_getting_custom_wiki_properties(self):
        sparql_statement = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX nlpg:     <http://www.NLPGraph.com/ontology/>  
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        SELECT ?prop ?wikiProp {
            ?prop a owl:DatatypeProperty ;
                  rdfs:subPropertyOf ?wikiProp .   
            FILTER (strstarts(str(?wikiProp), 'http://www.wikidata.org/prop/direct/'))
        }
        """
        query_result = graph.query(sparql_statement)
        props = {}
        wdt_namespace = namespaces.get('wdt')
        for row in query_result:
            props[row.prop] = 'wdt:' + str(row.wikiProp).strip(wdt_namespace)

        expected_dict = {rdflib.term.URIRef(namespaces['ex']+'birthDate'): 'wdt:P569',
                         rdflib.term.URIRef(namespaces['ex']+'population'): 'wdt:P1082'}
        self.assertEqual(props, expected_dict)


if __name__ == '__main__':
    unittest.main()
