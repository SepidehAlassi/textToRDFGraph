from qwikidata.sparql import return_sparql_query_results

from constants import FEMALE_ADDRESS_WORDS, MALE_ADDRESS_WORDS
from pipes.PreProcessor import Input
from pipes.util.sparql_tools import *
from Entitiy import *
import time
import os
import uuid

text_attributes = ['text', 'label', 'start_char', 'end_char', 'document', 'language', '__len__']


def retrieve_wiki_info(found_locations, found_persons, existing_entities, inputs: Input):
    """
    Retrieve further information about extracted named entities from Wikidata
    :param found_locations: location entities found in the text
    :param found_persons: person entities found in the text
    :param existing_entities: a dictionary containing the already existing entities
    :param inputs: collection of the inputs of the pipeline
    :return: updated collection of extracted named entities
    """
    location_entities, wiki_props_loc = add_wiki_info_location(found_locations, inputs)
    existing_entities = unify_locations(location_entities, existing_entities)
    person_entities, wiki_props_pers = add_wiki_info_person(found_persons, inputs)
    existing_entities = unify_persons(person_entities, existing_entities)
    return existing_entities, {**wiki_props_loc, **wiki_props_pers}


def get_required_wiki_props_from_ontology(onto_graph: rdflib.Graph,
                                          shapes_graph: rdflib.Graph,
                                          entity_type="Person") -> {}:
    """
    Get the wiki properties specified in the ontology
    :param onto_graph: input ontology graph
    :param shapes_graph: input shapes graph
    :param entity_type: type of the entity we retrieve properties for
    :return: a dictionary containing properties, their wiki super-property and qName in the current ontology as well as optional info
    """
    namespaces = dict(onto_graph.namespaces())
    sparql_statement = find_wiki_props_statement(entity_type)
    query_result = onto_graph.query(sparql_statement)
    props = {}
    wdt_namespace = namespaces.get('wdt')
    for row in query_result:
        prop_Qname = row.prop.n3(onto_graph.namespace_manager)
        prop_label = prop_Qname.split(':')[1]
        props[prop_label] = {'wikidata': 'wdt:' + str(row.wikiProp).strip(wdt_namespace),
                             'prop_QName': prop_Qname,
                             'optional': row.minCard is None}
    sparql_statement = get_NonOptional_props_from_shapesGraph()
    query_result_shacl = shapes_graph.query(sparql_statement)
    for row in query_result_shacl:
        prop_Qname = row.prop.n3(shapes_graph.namespace_manager)
        prop_label = prop_Qname.split(':')[1]
        if prop_label in props.keys():
            props[prop_label]['optional'] = False
    return props


def retrieve_wiki_info_location(name: str, lang: str, onto_graph: rdflib.Graph, shapes_graph: rdflib.Graph):
    """
    retrieve information form Wikidata for a location entity
    :param name: name of the entity
    :param lang: text language
    :param onto_graph: the ontology graph
    :param shapes_graph: the shapes graph
    :return: retrieved location information and wiki properties found in the ontology
    """

    wiki_props = get_required_wiki_props_from_ontology(onto_graph=onto_graph,
                                                       shapes_graph=shapes_graph,
                                                       entity_type="Location")
    sparl_statements = make_wiki_query_sparql(name=name,
                                              lang=lang,
                                              wiki_props=wiki_props,
                                              entity_type='place')
    results = make_wiki_query(sparl_statements)
    wiki_info = {}
    if len(results) == 0:
        msg = "No records found for location " + name + " in language " + lang + "."
        print(msg)
        pass
    else:
        record = results[0]
        if len(results) > 1:
            msg = "Multiple records found for location " + name + " in language " + lang + ". Top one is chosen."
            # TODO: show options to user, ask for choice!
            print(msg)
        for key in record.keys():
            if key == 'place':
                wiki_info['wiki_id'] = record['place']['value']
            else:
                wiki_info[key.replace('Label', "")] = record[key]['value']
    return wiki_info, wiki_props


def retrieve_wiki_info_person(name: str, lang: str, onto_graph: rdflib.Graph, shapes_graph: rdflib.Graph):
    """
    Retrieve information from Wikidata for a person NE
    :param name: name of the person entity as found in the text
    :param lang: language of the text
    :param onto_graph: the ontology graph
    :param shapes_graph: the shapes graph
    :return: information extracted from wikidata for the person and the corresponding wiki properties extracted from the ontology
    """

    wiki_props = get_required_wiki_props_from_ontology(onto_graph=onto_graph,
                                                       shapes_graph=shapes_graph,
                                                       entity_type="Person")
    sparql_statement = make_wiki_query_sparql(name=name,
                                              lang=lang,
                                              wiki_props=wiki_props,
                                              entity_type='person')
    results = make_wiki_query(sparql_statement)

    wiki_info = {}
    if len(results) == 0:
        msg = "No records found for person " + name + " in language " + lang + " on wikidata."
        print(msg)
        pass
    else:
        record = results[0]
        if len(results) > 1:
            msg = "Multiple records found for person " + name + " in language " + lang + ". Top one is chosen."
            # TODO: show options to user, ask for choice!
            print(msg)
        for key in record.keys():
            if key == 'person':
                wiki_info['wiki_id'] = record['person']['value']
            else:
                wiki_info[key.replace('Label', "")] = record[key]['value']
    return wiki_info, wiki_props


def make_wiki_query(sparql_statement):
    """
    Send the query to SPARQL endpoint of the wikidata and get the results
    :param sparql_statement: SPARQL query as string
    :return: query results
    """
    results = {}
    try:
        res = return_sparql_query_results(sparql_statement)
        results = res["results"]["bindings"]
    except:

        print(sparql_statement)

    return results


def find_matching_entity(elem, collection):
    matching_entities = [existing_elem for existing_elem in collection if existing_elem.wiki_id == '' and existing_elem.text == elem.text and hash(existing_elem) != hash(elem)]
    if len(matching_entities):
        matching_entity = matching_entities.pop()
        attrib_vals = vars(matching_entity)
        for attrib, val in attrib_vals.items():
            if attrib not in text_attributes:
                setattr(elem, attrib, val)
    else:
        elem.local_id = str(uuid.uuid4())


def add_wiki_info_location(found_locations, inputs: Input):
    """
    Add information retrieved from wikidata to location entity records
    :param found_locations: location named entities found in the input text
    :param document: input document
    :return: updated locations
    """
    counter = 0
    wiki_props = {}
    for loc in found_locations:
        loc.document = inputs.doc_name
        same_loc = list(filter(lambda x: x.text == loc.text and x.geoNameID != '', found_locations))
        if len(same_loc) != 0:
            attrib_vals = vars(same_loc[0])
            for attrib, val in attrib_vals.items():
                if attrib not in text_attributes:
                    setattr(loc, attrib, val)
            counter -= 1
        else:
            wiki_info, wiki_props = retrieve_wiki_info_location(name=loc.text,
                                                                lang=loc.language,
                                                                onto_graph=inputs.onto_graph,
                                                                shapes_graph=inputs.shacl_graph)

            for key, val in wiki_info.items():
                setattr(loc, key, val)
            if len(wiki_info) == 0:  # no wiki record found for the location
                find_matching_entity(loc, found_locations)
            else:
                loc.local_id = loc.geoNameID

        if counter == 8:
            time.sleep(90)
            counter = 0
        else:
            counter += 1
    return found_locations, wiki_props


def check_vicinity(person: PersonEntity, found_persons: dict, text: str):
    before_text = text[:person.start_char]
    if len(before_text):
        words = before_text.split()
        last_word = words.pop().strip('.')
        if last_word in FEMALE_ADDRESS_WORDS:
            person.gender = 'female'
        elif last_word in MALE_ADDRESS_WORDS:
            person.gender = 'male'

    before_pers = [pers for pers in found_persons if pers.end_char < person.start_char and person.text in pers.text]
    if len(person.gender):
        before_pers = [pers for pers in before_pers if pers.gender == person.gender]
    if len(before_pers) > 0:
        sorted_list = sorted(before_pers, key=lambda x: x.start_char)
        reference_pers = sorted_list.pop()
        attrib_vals = vars(reference_pers)
        for attrib, val in attrib_vals.items():
            if attrib not in text_attributes:
                setattr(person, attrib, val)

    else:  # person does not have wiki record and does not occur previously in the text
        # check if there is a person with same text without wiki_id in the existing entities, if there is, get its attributes otherwise make new record with random UUI
        find_matching_entity(person, found_persons)
        name = person.text.split()
        if len(name) == 2:
            person.givenName = name[0]
            person.familyName = name[1]


def add_wiki_info_person(found_persons, inputs: Input):
    """
    Add information retrieved from wikidate to person entities
    :param found_persons: the person entities found in the input text
    :param inputs: inputs of the pipeline
    :return: updated persons
    """
    counter = 0
    wiki_props = {}
    for pers in found_persons:
        pers.document = inputs.doc_name
        same_pers = list(filter(lambda x: x.text == pers.text and x.gnd != '', found_persons))
        if len(same_pers) != 0:
            attrib_vals = vars(same_pers[0])
            for attrib, val in attrib_vals.items():
                if attrib not in text_attributes:
                    setattr(pers, attrib, val)
            counter -= 1
        else:
            wiki_info, wiki_props = retrieve_wiki_info_person(name=pers.text,
                                                              lang=pers.language,
                                                              onto_graph=inputs.onto_graph,
                                                              shapes_graph=inputs.shacl_graph)
            for key, val in wiki_info.items():
                setattr(pers, key, val)
            if len(wiki_info) == 0:
                check_vicinity(pers, found_persons, inputs.text)
            else:
                pers.local_id = pers.gnd

        if counter == 8:
            time.sleep(90)
            counter = 0
        else:
            counter += 1
    return found_persons, wiki_props


def unify_locations(found_locations, entities_dict):
    """
    Unify representations of locations in different languages
    :param found_locations: location entities found within texts
    :param entities_dict: the dictionary containing extracted entities enriched with wiki info
    :return: updated dictionary of extracted entities
    """
    for loc in found_locations:
        if loc.local_id not in entities_dict['Locations'].keys():
            entities_dict['Locations'][loc.local_id] = [loc]
        else:
            entities_dict['Locations'][loc.local_id].append(loc)
    return entities_dict


def unify_persons(found_persons, entities_dict):
    """
    Unify representations of persons in different languages
    :param found_persons: person entities found within texts
    :param entities_dict: the dictionary containing extracted entities enriched with wiki info
    :return: updated dictionary of extracted entities
    """
    for pers in found_persons:
        if pers.local_id not in entities_dict['Persons'].keys():
            entities_dict['Persons'][pers.local_id] = [pers]
        else:
            entities_dict['Persons'][pers.local_id].append(pers)
    return entities_dict


if __name__ == '__main__':
    graph = rdflib.Graph()
    graph.parse(os.path.join('..', 'nlpGraph_onto.ttl'), format='turtle')
    wiki_info, wiki_props = retrieve_wiki_info_person("Jacob Bernoulli", "en", graph)
    print(wiki_info)
