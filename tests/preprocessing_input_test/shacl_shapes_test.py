import os.path
import unittest
from pyshacl import validate

data_graph = os.path.join(os.path.dirname(__file__), '..', '..', 'dh2023', 'dh2023_graph.ttl')
shacl_graph = os.path.join(os.path.dirname(__file__), '..', '..', 'inputs', 'example_shacl.ttl')
ont_graph = os.path.join(os.path.dirname(__file__), '..', '..', 'inputs', 'example_onto.ttl')


class MyTestCase(unittest.TestCase):
    def test_validate_files(self):

        conforms, results_graph, results_text = validate(data_graph=data_graph,
                                                         data_graph_format='turtle',
                                                         shacl_graph=shacl_graph,
                                                         ont_graph=ont_graph,
                                                         inference='rdfs',
                                                         abort_on_error=False,
                                                         meta_shacl=False,
                                                         debug=False)
        print(results_graph, results_text)
        self.assertEqual(conforms, True)

    def test_location_geonameID(self):
        data_graph = """
        @prefix : <http://www.example.com/resource/> .
        @prefix nlpg: <http://www.NLPGraph.com/ontology/> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .


        :2562619 a nlpg:Location ;
            nlpg:name "Victoria"@en ;
            owl:sameAs "http://www.wikidata.org/entity/Q20922893"^^xsd:anyURI .

        """

        conforms, results_graph, results_text = validate(data_graph=data_graph,
                                                         data_graph_format='turtle',
                                                         shacl_graph=shacl_graph,
                                                         ont_graph=ont_graph,
                                                         inference='rdfs',
                                                         abort_on_error=False,
                                                         meta_shacl=False,
                                                         debug=False)
        self.assertEqual(conforms, False)

    def test_name_prop_lang_EnOrDEorFA(self):
        data_graph = """
        @prefix : <http://www.example.com/resource/> .
        @prefix nlpg: <http://www.NLPGraph.com/ontology/> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .


        :7285902 a nlpg:Location ;
            nlpg:geoNameID "7285902"^^xsd:string ;
            nlpg:name "Genf"@de,
                      "Geneva"@en,
                       "ژنو"@fa ;
            owl:sameAs "http://www.wikidata.org/entity/Q71"^^xsd:anyURI .

        """

        conforms, results_graph, results_text = validate(data_graph=data_graph,
                                                         data_graph_format='turtle',
                                                         shacl_graph=shacl_graph,
                                                         ont_graph=ont_graph,
                                                         inference='rdfs',
                                                         abort_on_error=False,
                                                         meta_shacl=False,
                                                         debug=False)
        self.assertEqual(conforms, True)

    def test_name_prop_lang_notEnOrDEorFA(self):
        data_graph = """
        @prefix : <http://www.example.com/resource/> .
        @prefix nlpg: <http://www.NLPGraph.com/ontology/> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .


        :7285161 a nlpg:Location ;
                nlpg:geoName "7285161"^^xsd:string ;
                nlpg:name "Basel"@de,
                           "Bale"@fr;
                owl:sameAs "http://www.wikidata.org/entity/Q78"^^xsd:anyURI .

        """

        conforms, results_graph, results_text = validate(data_graph=data_graph,
                                                         data_graph_format='turtle',
                                                         shacl_graph=shacl_graph,
                                                         ont_graph=ont_graph,
                                                         inference='rdfs',
                                                         abort_on_error=False,
                                                         meta_shacl=False,
                                                         debug=False)
        self.assertEqual(conforms, False)

    def test_entity_name_required(self):
        data_graph = """
        @prefix : <http://www.example.com/resource/> .
        @prefix nlpg: <http://www.NLPGraph.com/ontology/> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .


        :2562619 a nlpg:Location ;
            nlpg:geoNameID "2562619"^^xsd:string ;
            owl:sameAs "http://www.wikidata.org/entity/Q20922893"^^xsd:anyURI .

        """

        conforms, results_graph, results_text = validate(data_graph=data_graph,
                                                         data_graph_format='turtle',
                                                         shacl_graph=shacl_graph,
                                                         ont_graph=ont_graph,
                                                         inference='rdfs',
                                                         abort_on_error=False,
                                                         meta_shacl=False,
                                                         debug=False)
        self.assertEqual(conforms, False)


if __name__ == '__main__':
    unittest.main()
