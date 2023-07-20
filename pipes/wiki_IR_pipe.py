from qwikidata.sparql import return_sparql_query_results
import warnings
import time


def wiki_IR_pipe(found_locations, found_persons, existing_entities, document):
    location_entities = add_wiki_info_location(found_locations, document)
    existing_entities = unify_locations(location_entities, existing_entities)
    person_entities = add_wiki_info_person(found_persons, document)
    existing_entities = unify_persons(person_entities, existing_entities)
    return existing_entities


def get_position(coordinate):
    longitude, latitude = coordinate.split(" ")
    return longitude.strip('Point('), latitude.strip(')')


def make_loc_query(name, lang):
    sparql_statement = """
    select ?wikiItem ?geonameID ?coordinate
    where {""" + \
                       '?wikiItem rdfs:label "' + name.title() + '"@' + lang + "; " + \
                       """wdt:P1566 ?geonameID;\n
    wdt:P625 ?coordinate
    }
    """

    res = return_sparql_query_results(sparql_statement)
    results = res["results"]["bindings"]
    return results


def get_wiki_record_location(name, lang):
    results = make_loc_query(name, lang)
    wiki_id = ""
    geoname_id = ""
    longitude = ""
    latitude = ""
    if len(results) == 0:
        msg = "No records found for location " + name + " in language " + lang + "."
        print(msg)
        pass
    else:
        record = results[0]
        if len(results) > 1:
            msg = "Multiple records found for location " + name + " in language " + lang + ". Top one is chosen."
            print(msg)
        wiki_id = record['wikiItem']['value']
        geoname_id = record['geonameID']['value']
        coordinate = record['coordinate']['value']
        longitude, latitude = get_position(coordinate)

    return wiki_id, geoname_id, longitude, latitude


def get_wiki_record_person(name, lang):
    sparql_statement = """
       SELECT ?person ?gnd ?givenNameLabel ?familyNameLabel ?gender_label
WHERE {
  ?person wdt:P31 wd:Q5; \n""" + \
                       'rdfs:label "' + name + '"@' + lang + "; \n" + \
                       """     wdt:P227 ?gnd ;
          wdt:P735 ?givenName ;
          wdt:P734 ?familyName ;
          wdt:P21 ?gender .
  ?gender rdfs:label ?gender_label. \n""" + \
                       'FILTER ( lang(?gender_label) = "' + lang + '" )\n' + \
                       'SERVICE wikibase:label { bd:serviceParam wikibase:language "' + lang + '". }\n}'

    res = return_sparql_query_results(sparql_statement)
    results = res["results"]["bindings"]
    wiki_id = ""
    gnd = ""
    given_name = ""
    family_name = ""
    gender =""
    if len(results) == 0:
        msg = "No records found for person " + name + " in language " + lang + "."
        print(msg)
        pass
    else:
        record = results[0]
        if len(results) > 1:
            msg = "Multiple records found for person " + name + " in language " + lang + ". Top one is chosen."
            print(msg)
        wiki_id = record['person']['value']
        gnd = record['gnd']['value']
        given_name = record['givenNameLabel']['value']
        family_name = record['familyNameLabel']['value']
        gender = record['gender_label']['value']

    return wiki_id, gnd, given_name, family_name, gender


def add_wiki_info_location(found_locations, document):
    counter = 0
    for loc in found_locations:
        loc.document = document
        same_loc = list(filter(lambda x: x.text == loc.text and x.geoname_id != '', found_locations))
        if len(same_loc) != 0:
            same_item = same_loc[0]
            loc.wiki_id = same_item.wiki_id
            loc.geoname_id = same_item.geoname_id
            loc.latitude = same_item.latitude
            loc.longitude = same_item.longitude
            counter -= 1
        else:
            loc.wiki_id, loc.geoname_id, loc.longitude, loc.latitude = get_wiki_record_location(loc.text, loc.language)
        if counter == 8:
            time.sleep(90)
            counter = 0
        else:
            counter += 1
    return found_locations


def add_wiki_info_person(found_persons, document):
    counter = 0
    for pers in found_persons:
        pers.document = document
        same_pers = list(filter(lambda x: x.text == pers.text and x.gnd != '', found_persons))
        if len(same_pers) != 0:
            same_item = same_pers[0]
            pers.wiki_id = same_item.wiki_id
            pers.given_name = same_item.given_name
            pers.family_name = same_item.family_name
            pers.gnd = same_item.gnd
            pers.gender = same_item.gender
            counter -= 1
        else:
            pers.wiki_id, pers.gnd, pers.given_name, pers.family_name, pers.gender = get_wiki_record_person(pers.text, pers.language)
        if counter == 8:
            time.sleep(90)
            counter = 0
        else:
            counter += 1
    return found_persons


def unify_locations(found_locations, entities_dict):
    for loc in found_locations:
        if loc.geoname_id == '':
            pass
        elif loc.geoname_id not in entities_dict['Locations'].keys():
            entities_dict['Locations'][loc.geoname_id] = [loc]
        else:
            entities_dict['Locations'][loc.geoname_id].append(loc)
    return entities_dict


def unify_persons(found_persons, entities_dict):
    for pers in found_persons:
        if pers.gnd == '':
            pass
        elif pers.gnd not in entities_dict['Persons'].keys():
            entities_dict['Persons'][pers.gnd] = [pers]
        else:
            entities_dict['Persons'][pers.gnd].append(pers)
    return entities_dict


if __name__ == '__main__':
    # print(get_wiki_record_location("koblenz", "en"))
    print(get_wiki_record_person("Jacob Bernoulli", "en"))
