# Inputs of the Pipeline
By default, the pipeline uses the ontology given in `nlpGraph_onto.ttl` to generate the graph.
Similarly, by default, the pipeline uses the shacl shapes given in `nlpGraph_shacl.ttl` to validate the 
generated graph. 
The user can provide a custom ontology and shacl shapes as the input to the pipeline.
The path of the ontology and shacl shapes must be given as the input parameters when starting the pipeline.

## What can custom ontologies contains?
1. Namespaces and prefixes that must be used to create the resources. For example, you can set the prefix `ex` for your project:
```
@prefix ex:     <http://www.example.com/ontology/> .
@prefix : <http://www.example.com/resource/> .
```
The resources will be created with IRIs having the default namespace as its main part.

2. If you wish more datatype properties to be retrieved from wikidata for a person or a location, 
you must add that property to your ontology specifying it as sub-property of the wiki property as:
```
@prefix wdt: <http://www.wikidata.org/prop/direct/> .
@prefix owl:        <http://www.w3.org/2002/07/owl#> .
@prefix nlpg:     <http://www.NLPGraph.com/ontology/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:       <http://www.w3.org/2000/01/rdf-schema#> .

ex:birthDate rdf:type owl:DatatypeProperty ;
         rdfs:subPropertyOf wdt:P569 ;
         rdfs:label   "date of birth"@en ;
         rdfs:comment "date of birth of a person."@en ;
         rdfs:domain  nlpg:Person ;
         rdfs:range   xsd:date .
```
where 

In this way, you can tell pipeline to retrieve information about the birthdate of a person from Wikidata and add this 
info to the node of the graph representing this person.  
**Note:** the property should be given as `owl:DatatypeProperty`
3. The relations that must be extracted during the second stage of the pipeline through dependency parsing and POS tagging,
should be given as `owl:ObjectProperty` with `rdfs:range` and `rdfs:domain` which are `nlpg:Person` or `nlpg:Location`.
For example, suppose we want the pipeline to find all locations a person traveled to from the input text, we can define 
a new property describing this relation between a resource of type `nlpg:Person` and resources of type `nlpg:Location`:
```
ex:traveledTo  rdf:type owl:ObjectProperty ;
             rdfs:label  "Traveled to"@en ;
             rdfs:comment "Trip destination."@en ;
             rdfs:domain  nlpg:Person ;
             rdfs:range   nlpg:Location .
```
Through this property definition, the pipeline will try to parse out from the text all the information about places the persons mentioned 
in the text traveled to. The locations will be stored as `nlpg:Location` resource, and an edge will be created connecting
the corresponding person and location resources. 

## What can custom shacl graph contain?
1. Property shapes to check the datatype properties given in the ontology. In this way, we can validate that information 
retrieved from Wikidata is valid. Here is the property shape that should be used to validate the birthdate retrived from 
Wikidata for `nlpg:Person` resources. This shape must be given in a turtle file containing all shapes that must be used 
to validate the properties given in the custom ontology.

```
ex:BirthDateShape
	a sh:PropertyShape ;
	sh:path ex:birthDate;
	sh:message "We need at least one birth date value for a person" ;
    sh:severity sh:Violation ;
	sh:minCount 1 ;
    sh:datatype xsd:date ;
    sh:targetClass nlpg:Person.
```
2. Property shapes to validate the object properties that represent relation between named entities.
```
ex:TraveledToShape
	a sh:PropertyShape ;
	sh:path ex:traveledTo;
	sh:message "No travel destinations found for the person." ;
    sh:severity sh:Warning ;
    sh:class nlpg:Location ;
    sh:targetClass nlpg:Person.
```
We can set different levels of severity of validation failure in case data is not consistent with the shape; for example 
in case the data is not consistent with this shape a warning is raised with the given custom message.
