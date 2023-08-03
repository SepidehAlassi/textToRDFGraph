import pandas as pd
from rdflib import Graph, URIRef
from rdflib.namespace import Namespace
from pipes.preprocess_pipe import Input
import os

# Add namespace
DEFAULT = Namespace("http://www.NLPGraph.com/resource/")
MYONTO = Namespace("http://www.NLPGraph.com/ontology/")


def update_graph(links_to_add, document_label, project_name):
    graph = Graph()
    graph_file_path = os.path.join(project_name, project_name + '_graph.ttl')
    graph.parse(graph_file_path, format='ttl')
    star_statements = ""
    for link in links_to_add:
        graph.add((URIRef(link['subj_iri']), URIRef(link['prop_iri']), URIRef(link['obj_iri'])))
        star_statements += "<< <" + link['subj_iri'] + "> <" + link['prop_iri'] + "> <" + link[
            'obj_iri'] + "> >> myOnto:mentionedIn <" + DEFAULT + document_label + "> .\n"
    graph.serialize(destination=graph_file_path, format='turtle')

    with open(graph_file_path, 'a') as graph_file:
        graph_file.write(star_statements)


def extract_entity_relations(graph):
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
        extracted_relations[r['prop_label'].lower()] = {'prop': r['prop']}
    return extracted_relations


def add_entity_relations(sentences, inputs: Input):
    relations = extract_entity_relations(graph=inputs.onto_graph)
    links_to_add = []
    for sent_num, sent_instances in sentences.items():
        for sent_inst in sent_instances:

            subj = sent_inst.subj
            obj = sent_inst.object
            if subj.token.pos_ != "PRON" and obj.token.pos_ != 'PRON':
                subject_iri = subj.entity.iri

                predicate = relations[sent_inst.verb.text]['prop']

                object_iri = obj.entity.iri
                links_to_add.append({'subj_iri': subject_iri, 'prop_iri': predicate, 'obj_iri': object_iri})
    update_graph(links_to_add, inputs.doc_name, inputs.project_name)


if __name__ == '__main__':
    pass
