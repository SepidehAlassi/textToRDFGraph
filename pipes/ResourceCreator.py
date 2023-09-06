import json
import os
from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import XSD, Namespace, SDO, RDF, RDFS, OWL
from pipes.PreProcessor import Input

# Add namespace
DEFAULT = Namespace("http://www.NLPGraph.com/resource/")
NLPG = Namespace("http://www.NLPGraph.com/ontology/")


def add_resource_to_graph(references, res_iri, type, graph):
    names = {}
    for reference in references:
        name = reference['text']
        lang = reference['language']
        names[lang] = name
        reference['iri'] = res_iri

    graph.add((res_iri, RDF.type, type))
    for lang, name in names.items():
        graph.add((res_iri, NLPG.name, Literal(name, lang=lang)))
    wiki_id = references[0].get('wiki_id')
    graph.add((res_iri, OWL.sameAs, Literal(wiki_id, datatype=XSD.anyURI)))
    if type == NLPG.Location:
        graph.add((res_iri, NLPG.geoName, Literal(references[0].get('geoname_id'), datatype=XSD.string)))
    else:
        graph.add((res_iri, SDO.givenName, Literal(references[0].get('given_name'), datatype=XSD.string)))
        graph.add((res_iri, SDO.familyName, Literal(references[0].get('family_name'), datatype=XSD.string)))
        graph.add((res_iri, NLPG.gnd, Literal(references[0].get('gnd'), datatype=XSD.string)))
        graph.add((res_iri, SDO.gender, Literal(references[0].get('gender'), datatype=XSD.string)))
    return references


def initialize_graph(graph_file):
    entities_graph = Graph()
    if os.path.exists(graph_file):
        entities_graph.parse(graph_file, format='ttl')
    else:
        entities_graph.bind("schema", SDO)
        entities_graph.bind("", DEFAULT)
        entities_graph.bind("nlpg", NLPG)
    return entities_graph


def create_entity_resources(entities_path, project_name):
    graph_file = os.path.join(os.getcwd(), project_name, project_name + '_graph.ttl')
    entities_graph = initialize_graph(graph_file)

    with open(entities_path) as input_file:
        entities_dict = json.load(input_file)
    locations = entities_dict.get('Locations')
    persons = entities_dict.get('Persons')

    for res_id, references in locations.items():
        iri = URIRef(DEFAULT + res_id)
        updated_loc = add_resource_to_graph(references=references, res_iri=iri, type=NLPG.Location,
                                            graph=entities_graph)

        entities_dict['Locations'][res_id] = updated_loc

    for res_id, references in persons.items():
        iri = URIRef(DEFAULT + res_id.lstrip('(DE-588)'))
        updated_loc = add_resource_to_graph(references=references, res_iri=iri, type=NLPG.Person,
                                            graph=entities_graph)

        entities_dict['Persons'][res_id] = updated_loc

    with open(entities_path, 'w') as output_file:
        json.dump(entities_dict, output_file, indent=4)

    entities_graph.serialize(destination=graph_file, format='turtle')


def generate_document_resource(doc_iri, doc_label, text, graph):
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


def add_references(entities_json, text_res_iri, doc_name, graph):
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


def create_document_resource(entities_json, inputs):
    graph_file = os.path.join(os.getcwd(), inputs.project_name, inputs.project_name + '_graph.ttl')
    document_graph = Graph()
    document_graph.parse(graph_file, format='ttl')
    doc_iri = URIRef(DEFAULT + inputs.doc_name)
    text_iri = generate_document_resource(doc_iri, inputs.doc_name, inputs.text, graph=document_graph)
    document_graph = add_references(entities_json, text_iri, inputs.doc_name, graph=document_graph)

    document_graph.serialize(destination=graph_file, format='turtle')


def create_resources(entities_json, inputs):
    create_entity_resources(entities_path=entities_json,
                            project_name=inputs.project_name)
    create_document_resource(entities_json=entities_json,
                             inputs=inputs)


if __name__ == '__main__':
    entities_json = os.path.join(os.getcwd(), 'dh2023', 'dh2023_entities.json')
    test_input = Input(text_path=os.path.join(os.getcwd(), 'inputs', 'test_data', 'dh2023', 'fa_swiss.txt'),
                       onto_path=os.path.join(os.getcwd(), 'inputs', 'ner_onto.ttl'),
                       project_name='dh2023')
    create_document_resource(entities_json, test_input)
