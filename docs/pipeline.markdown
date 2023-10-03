---
layout: page
title: Pipeline
permalink: /pipeline/
---

![image](assets/pipeline.png)

The pipeline extracts the named entities and the relations between them from texts to augment a knowledge graph. 
The pipeline focuses on extracting and linking three types of entries from unstructured texts in different languages: 
locations, persons, and their relations. Based on the language of the input text, the pipeline will be initialized with 
a pre-trained statistical language model. Based on the input ontology, the pipeline will extract information from the 
input texts in different languages and will construct the output graph, that is an RDF-star-based graph with the source 
of the extracted information added to the edges of the graph.

Inputs:
- path to a .txt file containing text or path to a folder containing multiple text files. At these first stage of the development, the pipeline accepts only English, German, and Farsi texts.
- path to the ontology file and corresponding SHACL shapes file. From the ontology and SHACL shapes, the pipeline extracts types of entities that should be extracted, and their relations.

Read more about the inputs of pipeline [here](pipeline/pipeline_inputs.markdown)!

User can choose between spaCy and Flair libraries to be used for the NER (Named Entity Recognition) pipe. If spaCy is chose, large English or German language models is used for processing the input text. To process texts in Farsi, Flair is used.
The pipeline uses spaCy's POS-tagging and dependency parsing results, to parse the relations between entities.

