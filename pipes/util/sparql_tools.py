import rdflib


def find_wiki_props_statement(entity_type: str) -> str:
    sparql_statement = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX nlpg:     <http://www.NLPGraph.com/ontology/>  
            PREFIX owl: <http://www.w3.org/2002/07/owl#> 
            SELECT DISTINCT ?prop ?wikiProp ?minCard 
            WHERE {
                ?prop rdfs:subPropertyOf ?wikiProp ; """ + \
                       "rdfs:domain nlpg:" + entity_type + """ .\n   
                optional {
                    ?prop owl:minCardinality ?minCard .
                    FILTER(?minCard >0)
                }
                FILTER (strstarts(str(?wikiProp), 'http://www.wikidata.org/prop/direct/'))
            }
            """
    return sparql_statement


def get_NonOptional_props_from_shapesGraph() -> bool:
    sparql_statement = """
                PREFIX sh: <http://www.w3.org/ns/shacl#> 
                SELECT DISTINCT ?prop
                WHERE {
                ?shapes a sh:PropertyShape ;
                        sh:path ?prop ;
                        sh:minCount ?minCount .
                FILTER(?minCount >0)        
                }
                """
    return sparql_statement


def find_prop_range_statement(prop_iri: rdflib.URIRef) -> str:
    sparql_statement = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            
            SELECT ?range 
            WHERE {
                BIND(""" + prop_iri.n3() + """ AS ?prop)
                ?prop rdfs:range ?range .
            }
            """
    return sparql_statement


def make_wiki_query_sparql(name: str, lang: str, wiki_props={}, entity_type="person") -> str:
    main_var = "?"+entity_type
    variables = " "+main_var
    for key in wiki_props.keys():
        key_var = " ?" + key + "Label"
        variables += key_var
    select_block = "SELECT DISTINCT" + variables + '\n'
    if entity_type == 'person':
        where_block = "WHERE {\n\t?person wdt:P31 wd:Q5 . \n"
    else:
        where_block = "WHERE {\n\t"
    where_block += "\t{" + main_var + " rdfs:label '" + name + "'@" + lang + " . }\n\tUNION \n\t{" + main_var + " rdfs:label '" + name.title() + "'@" + lang + " . }\n"
    non_optional_props = {key: prop_val for key, prop_val in wiki_props.items() if not wiki_props[key]['optional']}
    optional_props = {key: prop_val for key, prop_val in wiki_props.items() if wiki_props[key]['optional']}

    for key, prop_val in non_optional_props.items():
        where_block += "\t" + main_var + " " + prop_val['wikidata'] + " ?" + key + " .\n"
    optional_block = "OPTIONAL {\n"
    for key, prop_val in optional_props.items():
        optional_block += "\t" + main_var + " " + prop_val['wikidata'] + " ?" + key + " .\n"
    optional_block += "}"
    if len(optional_props) != 0:
        where_block += optional_block

    where_block += '\tSERVICE wikibase:label { bd:serviceParam wikibase:language "' + lang + '". }\n}'
    sparql_statement = select_block + where_block
    return sparql_statement


if __name__ == '__main__':
    pass
