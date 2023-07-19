from rdflib import Graph


def parse_ontology(file):
    graph = Graph()
    graph.parse(file, format='ttl')


    link_props = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX owl:  <http://www.w3.org/2002/07/owl#> 
        PREFIX myOnto:     <http://www.NLPGraph.com/ontology/>  
    
        SELECT ?prop ?prop_label
        WHERE {
            ?prop a owl:ObjectProperty .
            ?prop rdfs:domain myOnto:Person .    
            ?prop rdfs:range myOnto:Location .
            ?prop rdfs:label ?prop_label .
            FILTER ( lang(?prop_label) = "en" )
        }
    """

    extracted_relations = {}
    for r in graph.query(link_props):
        extracted_relations[r['prop_label'].lower()] = { 'prop': r['prop']}
    return extracted_relations

if __name__ == '__main__':
    print(parse_ontology('../textToRDFGraph/ner_onto.ttl'))
