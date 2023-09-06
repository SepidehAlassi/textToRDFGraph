import json
import os
from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import XSD, Namespace, SDO, RDF, RDFS, OWL
from pipes.PreProcessor import Input

# Add namespace
DEFAULT = Namespace("http://www.NLPGraph.com/resource/")
NLPG = Namespace("http://www.NLPGraph.com/ontology/")


def add_resource_to_graph(entity_references, res_iri, ne_type, graph):
    """
    Add a new resource node to the graph to represent the named entities found in the text
    :param entity_references: Various references to a named entity; i.e. in different languages
    :param res_iri: the IRI of the resource
    :param ne_type: type of the named entity
    :param graph: output graph
    :return: Make a resource representing a named entity and all its representations in different langs extracted from
    the inputs of the pipeline.
    """
    names = {}
    for reference in entity_references:
        name = reference['text']
        lang = reference['language']
        names[lang] = name
        reference['iri'] = res_iri

    graph.add((res_iri, RDF.type, ne_type))
    for lang, name in names.items():
        graph.add((res_iri, NLPG.name, Literal(name, lang=lang)))
    wiki_id = entity_references[0].get('wiki_id')
    graph.add((res_iri, OWL.sameAs, Literal(wiki_id, datatype=XSD.anyURI)))
    if ne_type == NLPG.Location:
        graph.add((res_iri, NLPG.geoName, Literal(entity_references[0].get('geoname_id'), datatype=XSD.string)))
    else:
        graph.add((res_iri, SDO.givenName, Literal(entity_references[0].get('given_name'), datatype=XSD.string)))
        graph.add((res_iri, SDO.familyName, Literal(entity_references[0].get('family_name'), datatype=XSD.string)))
        graph.add((res_iri, NLPG.gnd, Literal(entity_references[0].get('gnd'), datatype=XSD.string)))
        graph.add((res_iri, SDO.gender, Literal(entity_references[0].get('gender'), datatype=XSD.string)))
    return entity_references


def initialize_graph(graph_file):
    """
    Initial construction of the output graph
    :param graph_file: the path to the output file
    :return: If there is a graph file for the project parse it otherwise make an empty graph with namespaces.
    """
    entities_graph = Graph()
    if os.path.exists(graph_file):
        entities_graph.parse(graph_file, format='ttl')
    else:
        entities_graph.bind("schema", SDO)
        entities_graph.bind("", DEFAULT)
        entities_graph.bind("nlpg", NLPG)
    return entities_graph


def construct_graph_with_NEs(entities_path, project_name):
    """
    Construct the output graph with nodes representing the named entities. Write the graph to a turtle file.
    :param entities_path: path to the json file containing extracted named entity records
    :param project_name: name of the project
    """
    graph_file = os.path.join(os.getcwd(), project_name, project_name + '_graph.ttl')
    entities_graph = initialize_graph(graph_file)

    with open(entities_path) as input_file:
        entities_dict = json.load(input_file)
    locations = entities_dict.get('Locations')
    persons = entities_dict.get('Persons')

    for res_id, references in locations.items():
        iri = URIRef(DEFAULT + res_id)
        updated_loc = add_resource_to_graph(entity_references=references, res_iri=iri, ne_type=NLPG.Location,
                                            graph=entities_graph)

        entities_dict['Locations'][res_id] = updated_loc

    for res_id, references in persons.items():
        iri = URIRef(DEFAULT + res_id.lstrip('(DE-588)'))
        updated_loc = add_resource_to_graph(entity_references=references, res_iri=iri, ne_type=NLPG.Person,
                                            graph=entities_graph)

        entities_dict['Persons'][res_id] = updated_loc

    with open(entities_path, 'w') as output_file:
        json.dump(entities_dict, output_file, indent=4)

    entities_graph.serialize(destination=graph_file, format='turtle')


def create_document_resource_wo_references(doc_iri, doc_label, text, graph):
    """
    Add a resource representing a text document to the graph without attaching the embedded text references.
    :param doc_iri: IRI of the document resource
    :param doc_label: label of the document
    :param text: text of the document
    :param graph: output graph
    :return: IRI of the text content resource.
    """
    def generate_text_resource(text, doc_label):
        text_res_iri = URIRef(DEFAULT + doc_label + '_' + 'text')
        graph.add((text_res_iri, RDF.type, NLPG.Text))
        graph.add((text_res_iri, NLPG.textContent, Literal(text)))
        return text_res_iri

    graph.add((doc_iri, RDF.type, NLPG.Document))
    graph.add((doc_iri, RDFS.label, Literal(doc_label, datatype=XSD.string)))
    text_iri = generate_text_resource(text, doc_label)
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
                graph.add((text_res_iri, NLPG.hasStandoffMarkUp, reference))
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
    doc_iri = URIRef(DEFAULT + inputs.doc_name)
    text_iri = create_document_resource_wo_references(doc_iri, inputs.doc_name, inputs.text, graph=document_graph)
    document_graph = add_text_references(entities_json, text_iri, inputs.doc_name, graph=document_graph)

    document_graph.serialize(destination=graph_file, format='turtle')


def create_resources(entities_json, inputs):
    construct_graph_with_NEs(entities_path=entities_json,
                             project_name=inputs.project_name)
    add_document_resource_to_graph(entities_json=entities_json,
                                   inputs=inputs)


if __name__ == '__main__':
    entities_json = os.path.join(os.getcwd(), 'dh2023', 'dh2023_entities.json')
    test_input = Input(text_path=os.path.join(os.getcwd(), 'inputs', 'test_data', 'dh2023', 'fa_swiss.txt'),
                       onto_path=os.path.join(os.getcwd(), 'inputs', 'ner_onto.ttl'),
                       project_name='dh2023')
    add_document_resource_to_graph(entities_json, test_input)
