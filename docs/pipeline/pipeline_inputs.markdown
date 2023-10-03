---
layout: page
title: Pipeline Inputs
permalink: /pipeline/inputs/
exclude: true
---

To start the pipeline, it needs the path to the text file, or the directory containing the text files, as well as a name for the project.
```
pipeline(data_path=text_path)
```

By default, the pipeline creates an output directory in the working directory `my_project` and stores all pipeline results in it. 
Other names can be given through `project_name` parameter.

```
pipeline(data_path=text_path, project_name='travel_records')
```

By default, the pipeline uses the basis ontology `nlpGraph_onto.ttl` to generate the graph and the SHACL shapes given 
in `nlpGraph_shacl.ttl` to validate the constructed graph. 

The user can provide a custom ontology and its corresponding SHACL shapes as inputs to the pipeline serialized in Turtle format.
The path of the ontology and SHACL shapes turtle files must be given as the input parameters when starting the pipeline.

```
pipeline(data_path=text_path,
         ontology_path=ontology_path,
         shacl_path=shacl_path,
         project_name=project_name)
```

For examples of custom ontology and custom SHACL shapes graph, see files `example_onto.ttl` and `example_shacl.ttl` in 
`inputs` directory of the code base.

## What can custom ontologies contains?
- Namespaces and prefixes that must be used to create the resources. For example, you can set the prefix `ex` for your project:
```
@prefix ex:     <http://www.example.com/ontology/> .
@prefix : <http://www.example.com/resource/> .
```
The resources will be created with IRIs having the default namespace as its main part.

- If you wish more datatype properties to be retrieved from wikidata for a person or a location, 
you must add that property to your ontology specifying it as sub-property of the correspodning wikidata property, as 
shown in the example below. In this way, you can tell the pipeline to retrieve information about the birthdate of a person from Wikidata and add this 
information to the node of the graph representing the person. **Note** that the property should have `owl:DatatypeProperty` type!

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

- The relations that must be extracted during the second stage of the pipeline through dependency parsing and POS tagging,
should be given as `owl:ObjectProperty` with `rdfs:range` and `rdfs:domain` which are `nlpg:Person` or `nlpg:Location`.
For example, suppose we want the pipeline to find all locations a person traveled to from the input text, we can define 
a new property describing this relation between a resource of type `nlpg:Person` and resources of type `nlpg:Location`, 
as shown below. Through this property definition, the pipeline will attempt to parse out from the text all the information about places the persons mentioned 
in the text traveled to. The locations will be stored as `nlpg:Location` resource, and an edge will be created connecting
the corresponding person and location resources. 

```
ex:traveledTo  rdf:type owl:ObjectProperty ;
               rdfs:label  "Traveled to"@en ;
               rdfs:comment "Trip destination."@en ;
               rdfs:domain  nlpg:Person ;
               rdfs:range   nlpg:Location .
```

## What can custom SHACL shapes contain?
- Property shapes to check the datatype properties given in the ontology. In this way, the pipeline can validate the information 
retrieved from Wikidata. In the example below, a property shape is given to be used to validate the birthdate retrieved from 
Wikidata for `nlpg:Person` resources. This shape must be given in a turtle file containing all shapes that must be used 
to validate the properties given in the custom ontology.

```
ex:BirthDateShape a sh:PropertyShape ;
	              sh:path ex:birthDate ;
	              sh:message "We need at least one birth date value for a person" ;
                  sh:severity sh:Violation ;
	              sh:minCount 1 ;
                  sh:datatype xsd:date ;
                  sh:targetClass nlpg:Person.
```

- The cardinality requirements for a property must be given using the `sh:maxCount` and `sh:minCount` predicates defined in 
SHACL vocabulary. For optional properties, no cardinality restriction is required in the shapes graph. However, for the 
non-optional properties, such as `ex:birthDate` above, a minimum cardinality value must be given in the shapes graph through 
`sh:minCount` predicate. The property shape `ex:BirthDateShape` states that each `nlpg:Person` resource in the output data graph, must 
at least have one birthdate given through `ex:birthdate` predicate. That means, the pipeline must retrieve at least one birthdate
from Wikidata for each Person entity.

- Property shapes to validate the object properties that represent relation between named entities. We can set different levels of severity of validation failure in case data is not consistent with the shape; for example 
in case the data is not consistent with this shape a warning is raised with the given custom message.

```
ex:TraveledToShape a sh:PropertyShape ;
	               sh:path ex:traveledTo ;
	               sh:message "No travel destinations found for the person." ;
                   sh:severity sh:Warning ;
                   sh:class nlpg:Location ;
                   sh:targetClass nlpg:Person.
```

