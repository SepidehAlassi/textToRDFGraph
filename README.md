# textToRDFGraph
## Pipeline to construct RDF graph from text
**textToRDFGraph** project aims to develop an automatic information retrieval pipeline based on Natural Language Processing and Semantic Web technologies to construct a knowledge graph from textual data. It explores how we can extract named entities from texts to create linked open data networks and then use the open network data to extract more information from texts and unify the resources representing identical entities retrieved from texts in different languages. The primary purpose of this project is thus to construct a graph from textual information that can be queried for the embedded references in texts regardless of the text language. A high-performing query requires the data to be stored in an optimized way with all the metadata about extracted statements necessary for a faithful citation and reliable representation of data and metadata. Using RDF-star technology in graph construction carries this objective; therefore, this project shows how to use this technology to comprehensively represent textual data and facilitate complex queries required for humanities research.

## Pipeline:

![image](https://github.com/SepidehAlassi/textToRDFGraph/assets/8567642/89c6a09c-08cd-438d-bd0d-d2bdc80d4baa)

The pipeline extracts the named entities and the relations between them from texts to augment a knowledge graph. The pipeline focuses on extracting and linking three types of entries from unstructured texts in different languages: locations, persons, and their relations. Based on the language of the input text, the pipeline will be initialized with a pre-trained statistical language model. Based on the input ontology, the pipeline will extract information from the input texts in different languages and will construct the output graph, that is an RDF-star-based graph with the source of the extracted information added to the edges of the graph.

Inputs:
- path to a .txt file containing text or path to a folder containing multiple text files. At these first stage of the development, the pipeline accepts only English, German, and Farsi texts.
- path to the ontology file and corresponding SHACL shapes file. From the ontology and SHACL shapes, the pipeline extracts types of entities that should be extracted, and their relations.

User can choose between spaCy and Flair libraries to be used for the NER (Named Entity Recognition) pipe. If spaCy is chose, large English or German language models is used for processing the input text. To process texts in Farsi, Flair is used.
The pipeline uses spaCy's POS-tagging and dependency parsing results, to parse the relations between entities.

