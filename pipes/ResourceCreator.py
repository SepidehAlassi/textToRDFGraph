import json
import os
from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import XSD, Namespace, SDO, RDF, RDFS, OWL
from pipes.PreProcessor import Input
from langcodes import *
from pipes.util.sparql_tools import find_prop_range_statement

# Add namespace
NLPG = Namespace("http://www.NLPGraph.com/ontology/")

def get_prop_range(graph, prop_iri):
    sparql_statement = find_prop_range_statement(prop_iri)
    query_result = list(graph.query(sparql_statement))
    row = query_result[0]
    return row.range

def add_resource_to_graph(entity_references, res_iri, ne_type, data_graph, onto_graph):
    """
    Add a new resource node to the graph to represent the named entities found in the text
    :param entity_references: Various references to a named entity; i.e. in different languages
    :param res_iri: the IRI of the resource
    :param ne_type: type of the named entity
    :param data_graph: output data graph
    :param onto_graph: ontology graph
    :return: Make a resource representing a named entity and all its representations in different langs extracted from
    the inputs of the pipeline.
    """
    names = {}
    for reference in entity_references:
        name = reference['text']
        lang = reference['language']
        names[lang] = name
        reference['iri'] = res_iri

    data_graph.add((res_iri, RDF.type, ne_type))
    namespaces = dict(data_graph.namespaces())
    for lang, name in names.items():
        data_graph.add((res_iri, NLPG.name, Literal(name, lang=lang)))
    wiki_id = entity_references[0].get('wiki_id')
    data_graph.add((res_iri, OWL.sameAs, Literal(wiki_id, datatype=XSD.anyURI)))
    props={}
    for key, val in reference.items():
        if ':' in key:
            prefix, prop_label = key.split(':')
            ns = namespaces[prefix]
            prop_iri = URIRef(ns+prop_label)
            range = get_prop_range(onto_graph, prop_iri)
            if str(range).startswith(namespaces['xsd']):
                props[prop_iri] = {'value': val, 'datatype': range}
            else:
                props[prop_iri] = {'value': val}

    for prop in props.keys():
        object_val = props[prop]
        if 'datatype' in object_val:
            data_graph.add((res_iri, prop, Literal(object_val['value'], datatype=object_val['datatype'])))
        else:
            data_graph.add((res_iri, prop, URIRef(object_val['value'])))
    return entity_references


def initialize_graph(graph_file, onto_graph):
    """
    Initial construction of an output graph
    :param graph_file: the path to the output graph file
    :return: If there is a graph file for the project parse it otherwise make an empty graph with namespaces.
    """
    entities_graph = Graph()
    if os.path.exists(graph_file):
        entities_graph.parse(graph_file, format='ttl')
    else:
        entities_graph.namespace_manager = onto_graph.namespace_manager
    return entities_graph


def construct_graph_with_NEs(entities_path, onto_graph, project_name):
    """
    Construct the output graph with nodes representing the named entities. Write the graph to a turtle file.
    :param entities_path: path to the json file containing extracted named entity records
    :param project_name: name of the project
    """
    graph_file = os.path.join(os.getcwd(), project_name, project_name + '_graph.ttl')
    entities_graph = initialize_graph(graph_file, onto_graph)

    with open(entities_path) as input_file:
        entities_dict = json.load(input_file)
    locations = entities_dict.get('Locations')
    persons = entities_dict.get('Persons')
    namespaces = dict(entities_graph.namespaces())
    if '' in namespaces.keys():
        DEFAULT = Namespace(namespaces[''])
    else:
        DEFAULT = Namespace("http://www.NLPGraph.com/resource/")
    for res_id, references in locations.items():
        iri = URIRef(DEFAULT + res_id)
        updated_loc = add_resource_to_graph(entity_references=references,
                                            res_iri=iri,
                                            ne_type=NLPG.Location,
                                            data_graph=entities_graph,
                                            onto_graph=onto_graph)

        entities_dict['Locations'][res_id] = updated_loc

    for res_id, references in persons.items():
        iri = URIRef(DEFAULT + res_id)
        updated_loc = add_resource_to_graph(entity_references=references,
                                            res_iri=iri,
                                            ne_type=NLPG.Person,
                                            data_graph=entities_graph,
                                            onto_graph=onto_graph)

        entities_dict['Persons'][res_id] = updated_loc

    with open(entities_path, 'w') as output_file:
        json.dump(entities_dict, output_file, indent=4)

    entities_graph.serialize(destination=graph_file, format='turtle')


def create_document_resource_wo_references(doc_iri, inputs, graph):
    """
    Add a resource representing a text document to the graph without attaching the embedded text references.
    :param doc_iri: IRI of the document resource
    :param inputs: collection of pipeline's input data
    :param graph: output graph
    :return: IRI of the text content resource.
    """
    namespaces = dict(graph.namespaces())
    if '' in namespaces.keys():
        DEFAULT = Namespace(namespaces[''])
    else:
        DEFAULT = Namespace("http://www.NLPGraph.com/resource/")
    def generate_text_resource(text, doc_label):
        text_res_iri = URIRef(DEFAULT + doc_label + '_' + 'text')
        graph.add((text_res_iri, RDF.type, NLPG.Text))
        graph.add((text_res_iri, NLPG.textContent, Literal(text)))
        return text_res_iri

    graph.add((doc_iri, RDF.type, NLPG.Document))
    graph.add((doc_iri, RDFS.label, Literal(inputs.doc_name)))
    language_name = Language.make(language=inputs.lang).display_name()
    graph.add((doc_iri, NLPG.hasLanguage, Literal(language_name, datatype=XSD.string)))
    text_iri = generate_text_resource(inputs.text, inputs.doc_name)
    graph.add((doc_iri, NLPG.hasText, text_iri))
    return text_iri


def add_text_references(entities_json, text_res_iri, doc_name, graph):
    """
    Update the output graph by adding text references to the text content resource as standoff links to NE resources.
    :param entities_json: JSON containing extracted entities
    :param text_res_iri: IRI of the text content resource
    :param doc_name: Name of the text document
    :param graph: output graph
    :return: updated graph
    """
    with open(entities_json) as input_file:
        entities_dict = json.load(input_file)

    entities = {**entities_dict['Locations'], **entities_dict['Persons']}
    count = 0
    for key, references in entities.items():
        for item in references:
            if item['document'] == doc_name:
                doc_label = item['document']
                graph.add((text_res_iri, NLPG.hasReferenceTo, URIRef(item['iri'])))
                reference = BNode(doc_label + '_text_ref_' + str(count))
                graph.add((reference, RDF.type, NLPG.StandOffLink))
                graph.add((reference, NLPG.linkTo, URIRef(item['iri'])))
                graph.add((reference, NLPG.startChar, Literal(item['start_char'], datatype=XSD.integer)))
                graph.add((reference, NLPG.endChar, Literal(item['end_char'], datatype=XSD.integer)))
                graph.add((text_res_iri, NLPG.hasStandoffLink, reference))
                count += 1
    return graph


def add_document_resource_to_graph(entities_json, inputs):
    """
    Add a resource to the graph representing the input document
    :param entities_json: JSON containing already extracted named entities
    :param inputs: collection of pipeline's input data
    """
    graph_file = os.path.join(os.getcwd(), inputs.project_name, inputs.project_name + '_graph.ttl')
    document_graph = Graph()
    document_graph.parse(graph_file, format='ttl')

    namespaces = dict(document_graph.namespaces())
    if '' in namespaces.keys():
        DEFAULT = Namespace(namespaces[''])
    else:
        DEFAULT = Namespace("http://www.NLPGraph.com/resource/")
    doc_iri = URIRef(DEFAULT + inputs.doc_name)
    text_iri = create_document_resource_wo_references(doc_iri, inputs, graph=document_graph)
    document_graph = add_text_references(entities_json, text_iri, inputs.doc_name, graph=document_graph)

    document_graph.serialize(destination=graph_file, format='turtle')


def create_resources(entities_json, inputs: Input):
    construct_graph_with_NEs(entities_path=entities_json,
                             onto_graph=inputs.onto_graph,
                             project_name=inputs.project_name)
    add_document_resource_to_graph(entities_json=entities_json,
                                   inputs=inputs)


if __name__ == '__main__':
    entities_json = os.path.join(os.getcwd(), 'magellan', 'magellan_entities.json')
    test_input = Input(text_path=os.path.join(os.getcwd(), 'inputs', 'test_data', 'magellan_voyage', 'en_magellan_voyage.txt'),
                       onto_path=os.path.join(os.getcwd(), 'inputs', 'example_onto.ttl'),
                       shacl_path=os.path.join(os.getcwd(), 'inputs', 'example_shacl.ttl'),
                       project_name='magellan')
    create_resources(entities_json, test_input)
