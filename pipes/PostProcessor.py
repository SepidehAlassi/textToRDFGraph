from rdflib import Graph, URIRef
from rdflib.namespace import Namespace
from pipes.PreProcessor import Input
import os
import pandas as pd
from nltk.corpus import wordnet

# Add namespace
DEFAULT = Namespace("http://www.NLPGraph.com/resource/")
NLPG = Namespace("http://www.NLPGraph.com/ontology/")


def write_to_excel(tags_dict, project_name):
    pos_info = pd.DataFrame(data={'Sentence Num': [], 'Subject': [], 'Verb': [], 'Object': []})
    for sent_num, sent_info in tags_dict.items():
        for info_item in sent_info:
            pos_info = pd.concat([pos_info, pd.DataFrame([{'Sentence Num': sent_num,
                                                           'Subject': info_item.subj.entity.text,
                                                           'Verb': info_item.verb.text,
                                                           'Object': info_item.obj.entity.text
                                                           }])], ignore_index=True)
    excel_file = project_name + '_pos_info.xlsx'
    file_path = os.path.join(project_name, excel_file)
    with pd.ExcelWriter(file_path) as writer:
        pos_info.to_excel(writer, sheet_name='POS info')


def add_new_edges(links_to_add, document_label, project_name):
    graph = Graph()
    graph_file_path = os.path.join(project_name, project_name + '_graph.ttl')
    graph.parse(graph_file_path, format='ttl')
    star_statements = ""
    for link in links_to_add:
        graph.add((URIRef(link['subj_iri']), URIRef(link['prop_iri']), URIRef(link['obj_iri'])))
        star_statements += "<< <" + link['subj_iri'] + "> <" + link['prop_iri'] + "> <" + link[
            'obj_iri'] + "> >> nlpg:mentionedIn <" + DEFAULT + document_label + "> .\n"
    graph.serialize(destination=graph_file_path, format='turtle')

    with open(graph_file_path, 'a') as graph_file:
        graph_file.write(star_statements)


def extract_entity_relations(graph):
    link_props = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX owl:  <http://www.w3.org/2002/07/owl#> 
        PREFIX nlpg:     <http://www.NLPGraph.com/ontology/>  

        SELECT ?prop ?prop_label
        WHERE {
            ?prop a owl:ObjectProperty .
            ?prop rdfs:domain ?domain_class .
            ?domain_class rdfs:subClassOf nlpg:NamedEntity .    
            ?prop rdfs:range ?range_class .
            ?range_class rdfs:subClassOf nlpg:NamedEntity . 
            ?prop rdfs:label ?prop_label .
            FILTER ( lang(?prop_label) = "en" )
        }
    """

    extracted_relations = {}
    for r in graph.query(link_props):
        extracted_relations[r['prop_label'].lower()] = {'prop': r['prop']}
    return extracted_relations


def post_process_graph(sentences, inputs: Input):
    # Output the extracted relations in Excel
    write_to_excel(sentences, inputs.project_name)

    # enrich the graph with relations
    update_graph(sentences, inputs)


def update_graph(sentences, inputs: Input):

    relations = extract_entity_relations(graph=inputs.onto_graph)
    links_to_add = []
    for sent_num, sent_instances in sentences.items():
        for sent_inst in sent_instances:

            subj = sent_inst.subj
            obj = sent_inst.obj
            if subj.entity != {} and obj.entity != {}:
                subject_iri = subj.entity.iri

                flag, predicate = is_valid_edge(sent_inst.verb, relations)
                if not flag:
                    continue
                object_iri = obj.entity.iri
                links_to_add.append({'subj_iri': subject_iri, 'prop_iri': predicate, 'obj_iri': object_iri})
    add_new_edges(links_to_add, inputs.doc_name, inputs.project_name)


def is_valid_edge(verb, onto_edges):
    synonyms = []
    synonyms.append(verb.text)
    verb_stem = verb.token.text

    for syn in wordnet.synsets(verb_stem):
        for l in syn.lemmas():
            synonyms.append(l.name())
    flag = False
    prop_iri = None
    for key in list(onto_edges.keys()):
        if key in synonyms:
            flag = True
            prop_iri = onto_edges[key]['prop']
            break
    return flag, prop_iri



if __name__ == '__main__':
    pass
