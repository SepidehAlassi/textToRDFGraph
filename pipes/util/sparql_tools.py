def find_wiki_props_statement(entity_type: str) -> str:
    sparql_statement = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX nlpg:     <http://www.NLPGraph.com/ontology/>  
            PREFIX owl: <http://www.w3.org/2002/07/owl#> 
            SELECT ?prop ?wikiProp {
                ?prop rdfs:subPropertyOf ?wikiProp ; """ + \
                       "rdfs:domain nlpg:" + entity_type + """ .\n   
                FILTER (strstarts(str(?wikiProp), 'http://www.wikidata.org/prop/direct/'))
            }
            """
    return sparql_statement


def make_wiki_location_query_sparql(name: str, lang: str, wiki_props={}) -> str:
    variables = "?place"
    for key in wiki_props.keys():
        key_var = " ?" + key + "Label"
        variables += key_var
    select_block = "SELECT " + variables + '\n'
    where_block = """WHERE {\n\t?place rdfs:label '""" + name.title() + "'@" + lang + " . \n"
    for key, prop_val in wiki_props.items():
        where_block += "\t?place " + prop_val['wikidata'] + " ?" + key + " .\n"
    where_block += '\tSERVICE wikibase:label { bd:serviceParam wikibase:language "' + lang + '". }\n}'
    sparql_statement = select_block + where_block
    return sparql_statement


def make_wiki_person_query_sparql(name: str, lang: str, wiki_props={}) -> str:
    variables = " ?person"
    for key in wiki_props.keys():
        key_var = " ?" + key + "Label"
        variables += key_var
    select_block = "SELECT" + variables + '\n'
    where_block = """WHERE {\n?person wdt:P31 wd:Q5 ; \n""" + \
                  '\t\t rdfs:label "' + name.title() + '"@' + lang + " . \n"
    for key, prop_val in wiki_props.items():
        where_block += "\t?person " + prop_val['wikidata'] + " ?" + key + " .\n"
    where_block += '\tSERVICE wikibase:label { bd:serviceParam wikibase:language "' + lang + '". }\n}'
    sparql_statement = select_block + where_block
    return sparql_statement


if __name__ == '__main__':
    pass
