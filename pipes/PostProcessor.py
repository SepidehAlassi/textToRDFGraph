from rdflib import Graph, URIRef
from rdflib.namespace import Namespace
from pipes.PreProcessor import Input
from pipes.ResourceCreator import initialize_graph
from pyshacl import validate
import os
import pandas as pd
from nltk.corpus import wordnet


def write_to_excel(sent_comps, project_name):
    """
    Write the extract relations between named entities given in the text to an Excel file for verification.
    :param sent_comps: the relations between named entities extracted from sentences of input text
    :param project_name: the name of the input project
    """
    pos_info = pd.DataFrame(data={'Sentence Num': [], 'Subject': [], 'Verb': [], 'Object': []})
    for sent_num, sent_instances in sent_comps.items():
        for relation in sent_instances:
            pos_info = pd.concat([pos_info, pd.DataFrame([{'Sentence Num': sent_num,
                                                           'Subject': relation.subj.entity.text,
                                                           'Verb': relation.verb.text,
                                                           'Object': relation.obj.entity.text
                                                           }])], ignore_index=True)
    excel_file = project_name + '_pos_info.xlsx'
    file_path = os.path.join(project_name, excel_file)
    with pd.ExcelWriter(file_path) as writer:
        pos_info.to_excel(writer, sheet_name='POS info')


def add_new_edges(links_to_add, inputs: Input):
    """
    Add new edges to the graph that represent links between two named entities.
    :param links_to_add: new edges to be added to the graph
    :param inputs: collection of input items
    """
    def make_embeded_triple(triple_part):
        part = URIRef(triple_part).n3(graph.namespace_manager)
        prefix = part.split(':')[0]
        used_namespaces[prefix] = namespaces[prefix]
        return part + " "

    graph = Graph()
    graph_file_path = os.path.join(inputs.project_name, inputs.project_name + '_graph.ttl')
    graph.parse(graph_file_path, format='ttl')
    namespaces = dict(graph.namespaces())
    if '' in namespaces.keys():
        DEFAULT = Namespace(namespaces[''])
    else:
        DEFAULT = Namespace(namespaces['nlpg'])

    NLPG = Namespace(namespaces['nlpg'])
    used_namespaces = {}
    star_statements = ""
    for link in links_to_add:
        subj_iri=link['subj_iri']
        prop_iri = link['prop_iri']
        obj_iri = link['obj_iri']

        graph.add((URIRef(subj_iri), URIRef(prop_iri), URIRef(obj_iri)))

        embedded_triple = "<< "
        embedded_triple += make_embeded_triple(subj_iri)
        embedded_triple += make_embeded_triple(prop_iri)
        embedded_triple += make_embeded_triple(obj_iri)
        embedded_triple += ">> "

        used_namespaces['nlpg'] = NLPG

        star_statements += embedded_triple + \
                           URIRef(NLPG + 'mentionedIn').n3(graph.namespace_manager) + " " +\
                           URIRef(DEFAULT + inputs.doc_name).n3(graph.namespace_manager) + " .\n"
    graph.serialize(destination=graph_file_path, format='turtle')

    star_graph_path = os.path.join(inputs.project_name, inputs.project_name + '_graph_metadata.ttl')

    with open(star_graph_path, 'w') as star_graph_file:
        for prefix, namespace in used_namespaces.items():
            star_graph_file.write('@prefix '+prefix+": <"+namespace+"> .\n")
        star_graph_file.write('\n' + star_statements)


def validate_graph(inputs: Input):
    data_graph_file = os.path.join(inputs.project_name, inputs.project_name + '_graph.ttl')
    conforms, results_graph, results_text = validate(data_graph=data_graph_file,
                                                     data_graph_format='turtle',
                                                     shacl_graph=inputs.shacl_graph.serialize(format='turtle'),
                                                     ont_graph=inputs.onto_graph.serialize(format='turtle'),
                                                     inference='rdfs',
                                                     abort_on_error=False,
                                                     meta_shacl=False,
                                                     debug=False)

    if not conforms:
        print(results_graph)


def extract_entity_relations(onto_graph):
    """
    From the input ontology, extract the properties with named entities given in their domain and range
    :param onto_graph: ontology graph
    :return: properties that describe links between two named entities
    """
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
    for r in onto_graph.query(link_props):
        extracted_relations[r['prop_label'].lower()] = {'prop': r['prop']}
    return extracted_relations


def post_process_graph(sentence_comps, inputs: Input):
    """
    1. Write relations between entities extracted from text to Excel,
    2. extract relations from the input ontology,
    3. Match the extracted relations from text and ontology, and update the graph accordingly
    4. validate graph with shacl shapes
    :param sentence_comps: the relations between named entities extracted from sentences of input text
    :param inputs: the input data collection
    """
    # Output the extracted sentence components in Excel
    write_to_excel(sentence_comps, inputs.project_name)

    # Extract relations between entities specified in the input ontology
    relation_props = extract_entity_relations(onto_graph=inputs.onto_graph)

    # Enrich the graph with relations
    update_graph(sentence_comps, inputs, relation_props)

    # Validate data graph
    validate_graph(inputs)


def update_graph(sentence_comps, inputs: Input, relation_props):
    """
    Update the graph, i.e. update resources, add edges, add metadata, etc.
    :param sentence_comps: the relations between named entities extracted from sentences of input text
    :param inputs: collection of input data
    :param relation_props: properties given in the ontology relation named entity resources
    """
    links_to_add = []
    for sent_num, sent_instances in sentence_comps.items():
        for sent_inst in sent_instances:

            subj = sent_inst.subj
            obj = sent_inst.obj
            if subj.entity != {} and obj.entity != {}:
                subject_iri = subj.entity.iri

                flag, predicate = is_valid_edge(sent_inst.verb, relation_props)
                if not flag:
                    continue
                object_iri = obj.entity.iri
                links_to_add.append({'subj_iri': subject_iri, 'prop_iri': predicate, 'obj_iri': object_iri})
    add_new_edges(links_to_add, inputs)


def is_valid_edge(verb, onto_relation_props):
    """
    Is a relation extracted from text between two named entity a valid/wanted one according to the ontology?
    :param verb: a verb component extracted from text with named entities in subject and object positions
    :param onto_relation_props: properties between named entities described in the ontology.
    :return: boolean flag and prop_iri
    """
    synonyms = []
    synonyms.append(verb.text)
    verb_stem = verb.token.text

    for syn in wordnet.synsets(verb_stem):
        for l in syn.lemmas():
            synonyms.append(l.name())
    flag = False
    prop_iri = None
    for key in list(onto_relation_props.keys()):
        if key in synonyms:
            flag = True
            prop_iri = onto_relation_props[key]['prop']
            break
    return flag, prop_iri


if __name__ == '__main__':
    pass
