import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, FOAF

# Load the locally stored Knowledge Graphs
dblp_graph = Graph()
dblp_graph.parse("/home/borista/Desktop/Schorlarly QALD/QALD-data-files/semoa/semoa_authors.trig", format="trig")

semopenalex_graph = Graph()
semopenalex_graph.parse("/home/borista/Desktop/Schorlarly QALD/QALD-data-files/semoa/institutions-semopenalex-2023-10-26.trig", format="trig")

DBLP = Namespace("https://dblp.org/rdf/schema#")
SEMOPENALEX = Namespace("https://semopenalex.org/ontology/")
ORG = Namespace("http://www.w3.org/ns/org#")
SPAR = Namespace("http://purl.org/spar/bido/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DBPEDIA = Namespace("https://dbpedia.org/property/")

# Function to get the author's name from the DBLP KG
def get_author_name_from_dblp(author_dblp_uri):
    author_uri = URIRef(author_dblp_uri)
    name = dblp_graph.value(subject=author_uri, predicate=DBLP.primaryCreatorName)
    if name:
        print(f"Author name from DBLP: {name}")
        return str(name)
    else:
        print(f"No name found for {author_dblp_uri}")
        return None

# Function to get author information from the SemOpenAlex KG
def get_author_info_from_semopenalex(author_name):
    for s, p, o in semopenalex_graph.triples((None, FOAF.name, Literal(author_name))):
        author_info = {
            'citedByCount': semopenalex_graph.value(subject=s, predicate=SEMOPENALEX.citedByCount),
            'worksCount': semopenalex_graph.value(subject=s, predicate=SEMOPENALEX.worksCount),
            'hindex': semopenalex_graph.value(subject=s, predicate=SPAR.hIndex),
            'i10Index': semopenalex_graph.value(subject=s, predicate=SEMOPENALEX.i10Index),
            '2YrMeanCitedness': semopenalex_graph.value(subject=s, predicate=SEMOPENALEX.meanCitedness),
            'memberOf': semopenalex_graph.value(subject=s, predicate=ORG.memberOf),
        }
        return author_info
    return None

def extract_info(author_info, key):
    if author_info is None:
        return "Information not available"
    return author_info.get(key, "Information not available")

def compare_values(value1, value2, comparison_type):
    if value1 == "Information not available" or value2 == "Information not available":
        return "Information not available"

    try:
        value1 = float(value1)
        value2 = float(value2)
    except ValueError:
        return "Information not available"

    if comparison_type == "higher":
        return max(value1, value2)
    elif comparison_type == "lower":
        return min(value1, value2)
    else:
        return "Invalid comparison type"

# Function to get institution information from the SemOpenAlex KG
def get_institution_info_from_semopenalex(institution_uri):
    institution_uri = URIRef(institution_uri)
    institution_info = {
        'citedByCount': semopenalex_graph.value(subject=institution_uri, predicate=SEMOPENALEX.citedByCount),
        'worksCount': semopenalex_graph.value(subject=institution_uri, predicate=SEMOPENALEX.worksCount),
        'homepage': semopenalex_graph.value(subject=institution_uri, predicate=FOAF.homepage),
        'name': semopenalex_graph.value(subject=institution_uri, predicate=FOAF.name),
        'countryCode': semopenalex_graph.value(subject=institution_uri, predicate=DBPEDIA.countryCode),
        'rorType': semopenalex_graph.value(subject=institution_uri, predicate=SEMOPENALEX.rorType),
    }
    return institution_info

# Open the output files in write mode
with open('save-prediction/answers2.txt', 'w', encoding='utf-8') as outfile, \
     open('save-prediction/answers2context.txt', 'w', encoding='utf-8') as outfile_context:
    
    # Write the opening brackets for the JSON arrays
    outfile.write('[\n')
    outfile_context.write('[\n')

    # Read the input file
    with open('refined_context.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    null_count = 0
    total_questions = len(data)

    # Process each question
    for i, test_data in enumerate(data):
        try:
            question_id = test_data['id']
            question_text = test_data['question']
            context = test_data.get('context', "")
            author_dblp_uri = test_data.get('author_dblp_uri')
            answer = None

            print(f"Processing ID: {question_id} ({i+1}/{total_questions})")

            # Step 1: Try to answer using the SemOpenAlex or DBLP data
            if isinstance(author_dblp_uri, str):
                # Case of a single author
                author_name = get_author_name_from_dblp(author_dblp_uri)
                author_info = get_author_info_from_semopenalex(author_name) if author_name else None
                institution_info = get_institution_info_from_semopenalex(extract_info(author_info, 'memberOf'))

                if "two years citedness".lower() in question_text.lower():
                    print("inside Two years Citedness")
                    answer = extract_info(author_info, '2YrMeanCitedness')
                    print("The answer of type is ", answer )
                if "hindex".lower() in question_text.lower():
                    print("inside HIndex")
                    answer = extract_info(author_info, 'hindex')
                    print("The answer of hindex is ", answer )
                if "i10index".lower() in question_text.lower():
                    print("inside i10index")
                    answer = extract_info(author_info, 'i10Index')
                    print("The answer of i10index is ", answer )
                if "cited by count".lower() in question_text.lower() or "citedbycount".lower() in question_text.lower() or "citedby count".lower() in question_text.lower():
                    print("inside cited by count(author's)")
                    answer = extract_info(author_info, 'citedByCount')
                    print("The answer of cited by count(authors) is ", answer )
                if "works count".lower() in question_text.lower() or "workscount" in question_text.lower():
                    print("inside works count(Author)")
                    answer = extract_info(author_info, 'worksCount')
                    print("The answer of works count(Author) is ", answer )
                if "cited by count".lower() in question_text.lower() and "affiliation".lower() or "affiliate".lower() in question_text.lower():
                    print("inside cited by count(institution)")
                    answer = extract_info(institution_info, 'citedByCount')
                    print("The answer of cited by count(institution) is ", answer )
                if "cited by count".lower() in question_text.lower() and "institution".lower() in question_text.lower():
                    print("inside cited by count(institution)")
                    answer = extract_info(institution_info, 'citedByCount')
                    print("The answer of cited by count(institution) is ", answer )
                if "kind".lower() in question_text.lower():
                    print("inside kind(institution)")
                    answer = extract_info(institution_info, 'rorType')
                    print("The answer of kind(institution) is ", answer )

            elif isinstance(author_dblp_uri, list) and len(author_dblp_uri) == 2:
                # Case of comparison between two authors
                author_name1 = get_author_name_from_dblp(author_dblp_uri[0])
                author_info1 = get_author_info_from_semopenalex(author_name1) if author_name1 else None

                author_name2 = get_author_name_from_dblp(author_dblp_uri[1])
                author_info2 = get_author_info_from_semopenalex(author_name2) if author_name2 else None

                if "higher" in question_text.lower():
                    if "hindex" in question_text.lower():
                        hindex1 = extract_info(author_info1, 'hindex')
                        hindex2 = extract_info(author_info2, 'hindex')
                        answer = compare_values(hindex1, hindex2, "higher")
                    elif "i10index" in question_text.lower():
                        i10index1 = extract_info(author_info1, 'i10Index')
                        i10index2 = extract_info(author_info2, 'i10Index')
                        answer = compare_values(i10index1, i10index2, "higher")
                    elif "citedbycount" in question_text.lower():
                        citedByCount1 = extract_info(author_info1, 'citedByCount')
                        citedByCount2 = extract_info(author_info2, 'citedByCount')
                        answer = compare_values(citedByCount1, citedByCount2, "higher")
                    elif "works count" in question_text.lower():
                        worksCount1 = extract_info(author_info1, 'worksCount')
                        worksCount2 = extract_info(author_info2, 'worksCount')
                        answer = compare_values(worksCount1, worksCount2, "higher")

                if "lower" in question_text.lower():
                    if "hindex" in question_text.lower():
                        hindex1 = extract_info(author_info1, 'hindex')
                        hindex2 = extract_info(author_info2, 'hindex')
                        answer = compare_values(hindex1, hindex2, "lower")
                    elif "i10index" in question_text.lower():
                        i10index1 = extract_info(author_info1, 'i10Index')
                        i10index2 = extract_info(author_info2, 'i10Index')
                        answer = compare_values(i10index1, i10index2, "lower")
                    elif "citedbycount" in question_text.lower():
                        citedByCount1 = extract_info(author_info1, 'citedByCount')
                        citedByCount2 = extract_info(author_info2, 'citedByCount')
                        answer = compare_values(citedByCount1, citedByCount2, "lower")
                    elif "works count" in question_text.lower():
                        worksCount1 = extract_info(author_info1, 'worksCount')
                        worksCount2 = extract_info(author_info2, 'worksCount')
                        answer = compare_values(worksCount1, worksCount2, "lower")

            if answer is None:
                answer = "Information not available"
                null_count += 1

            # Save the result for this question
            result = {
                'id': question_id,
                'question': question_text,
                'author_dblp_uri': author_dblp_uri,
                'answer': answer
            }
            json.dump(result, outfile, ensure_ascii=False, indent=2)
            outfile.write(',\n')

            # Save the context result for this question
            result_context = {
                'id': question_id,
                'question': question_text,
                'context': context,
                'author_dblp_uri': author_dblp_uri,
                'answer': answer
            }
            json.dump(result_context, outfile_context, ensure_ascii=False, indent=2)
            outfile_context.write(',\n')

        except Exception as e:
            print(f"Error processing ID {question_id}: {e}")

    # Write the closing brackets for the JSON arrays
    outfile.write(']\n')
    outfile_context.write(']\n')

print(f"Total questions: {total_questions}")
print(f"Questions with 'Information not available': {null_count}")



# import json
# from rdflib import Graph

# # Load the locally stored Knowledge Graphs
# def load_local_kg(file_path):
#     graph = Graph()
#     graph.parse(file_path, format='trig')
#     return graph

# # Load the authors KG
# author_graph = load_local_kg('semoa_authors.trig')

# # Load the institutions KG
# institution_graph = load_local_kg('institutions-semopenalex-2023-10-26.trig')

# # Query for author name from the locally stored author KG
# def get_author_name_from_dblp(author_dblp_uri, graph):
#     sparql_query = f"""
#     PREFIX dblp: <https://dblp.org/rdf/schema#>
#     PREFIX foaf: <http://xmlns.com/foaf/0.1/>

#     SELECT ?name
#     WHERE {{
#         <{author_dblp_uri}> dblp:creatorName ?name .
#     }}
#     """
#     result = graph.query(sparql_query)
    
#     for row in result:
#         return str(row['name'])
    
#     print(f"No results for author URI: {author_dblp_uri}")
#     return None

# # Query for author information from the locally stored SemOpenAlex KG
# def get_author_info_from_semopenalex(author_name, graph):
#     sparql_query = f"""
#     PREFIX dcterms: <http://purl.org/dc/terms/>
#     PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#     PREFIX ns2: <https://semopenalex.org/ontology/>
#     PREFIX org: <http://www.w3.org/ns/org#>
#     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#     PREFIX ns3: <http://purl.org/spar/bido/>

#     SELECT ?author ?name ?memberOf ?citedByCount ?worksCount ?hindex ?i10Index ?myc
#     WHERE {{
#         {{
#             ?author foaf:name ?name .
#             ?author org:memberOf ?memberOf .
#             ?author ns2:citedByCount ?citedByCount .
#             ?author ns2:worksCount ?worksCount .
#             ?author ns3:h-index ?hindex .
#             ?author ns2:2YrMeanCitedness ?myc .
#             ?author ns2:i10Index ?i10Index .
            
#             FILTER(lcase(str(?name)) = lcase("{author_name}"))
#         }}
#         UNION
#         {{
#             ?author ns2:alternativeName ?altName .
#             ?author foaf:name ?name .
#             ?author org:memberOf ?memberOf .
#             ?author ns2:citedByCount ?citedByCount .
#             ?author ns2:worksCount ?worksCount .
#             ?author ns3:h-index ?hindex .
#             ?author ns2:2YrMeanCitedness ?myc .
#             ?author ns2:i10Index ?i10Index .

#             FILTER(lcase(str(?altName)) = lcase("{author_name}") && lcase(str(?altName)) != lcase(str(?name)))
#         }}
#     }}
#     """
    
#     result = graph.query(sparql_query)
    
#     for row in result:
#         return row
    
#     print(f"No results for author name: {author_name}")
#     return None

# # Extract relevant information
# def extract_info(author_info, key):
#     if author_info is None:
#         return "Information not available"
#     return author_info.get(key, 'Information not available')

# # Query for institution information from the locally stored SemOpenAlex KG
# def get_institution_info_from_semopenalex(institution_uri, graph):
#     if not institution_uri:
#         return None

#     sparql_query = f"""
#     PREFIX dcterms: <http://purl.org/dc/terms/>
#     PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#     PREFIX ns3: <https://semopenalex.org/ontology/>
#     PREFIX ns4: <https://dbpedia.org/property/>
#     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

#     SELECT ?citedByCount ?worksCount ?homepage ?name ?countryCode ?rorType
#     WHERE {{
#         <{institution_uri}> a ns3:Institution ;
#         ns3:citedByCount ?citedByCount ;
#         ns3:worksCount ?worksCount ;
#         foaf:homepage ?homepage ;
#         foaf:name ?name ;
#         ns4:countryCode ?countryCode ;
#         ns3:rorType ?rorType .
#     }}
#     """
    
#     result = graph.query(sparql_query)
    
#     for row in result:
#         return row
    
#     print(f"No results for institution URI: {institution_uri}")
#     return None

# # Compare values such as h-index, i10-index, etc.
# def compare_values(value1, value2, comparison_type):
#     if value1 == "Information not available" or value2 == "Information not available":
#         return "Information not available"

#     try:
#         value1 = float(value1)
#         value2 = float(value2)
#     except ValueError:
#         return "Information not available"

#     if comparison_type == "higher":
#         return max(value1, value2)
#     elif comparison_type == "lower":
#         return min(value1, value2)
#     else:
#         return "Invalid comparison type"

# # Main processing loop (reads questions, fetches answers, and writes to output)
# with open('sch_set2_test_questions.json', 'r') as f:
#     test_questions = json.load(f)

# answers = []

# for question in test_questions:
#     question_id = question['id']
#     question_text = question['question']
#     author_dblp_uri = question.get('author_dblp_uri')

#     if isinstance(author_dblp_uri, str):
#         # Single author case
#         author_name = get_author_name_from_dblp(author_dblp_uri, author_graph)
#         author_info = get_author_info_from_semopenalex(author_name, author_graph) if author_name else None

#         if "years citedness" in question_text.lower():
#             answer = extract_info(author_info, 'myc')
#         elif "hindex" in question_text.lower():
#             answer = extract_info(author_info, 'hindex')
#         elif "i10index" in question_text.lower():
#             answer = extract_info(author_info, 'i10Index')
#         elif "cited by count" in question_text.lower():
#             answer = extract_info(author_info, 'citedByCount')
#         elif "works count" in question_text.lower() or "workscount" in question_text.lower():
#             answer = extract_info(author_info, 'worksCount')
#         else:
#             answer = "Information not available"

#     elif isinstance(author_dblp_uri, list) and len(author_dblp_uri) == 2:
#         # Comparative case for two authors
#         author_name1 = get_author_name_from_dblp(author_dblp_uri[0], author_graph)
#         author_info1 = get_author_info_from_semopenalex(author_name1, author_graph) if author_name1 else None

#         author_name2 = get_author_name_from_dblp(author_dblp_uri[1], author_graph)
#         author_info2 = get_author_info_from_semopenalex(author_name2, author_graph) if author_name2 else None

#         if "higher" in question_text.lower() and "hindex" in question_text.lower():
#             hindex1 = extract_info(author_info1, 'hindex')
#             hindex2 = extract_info(author_info2, 'hindex')
#             answer = compare_values(hindex1, hindex2, "higher")
#         elif "higher" in question_text.lower() and "i10index" in question_text.lower():
#             i10index1 = extract_info(author_info1, 'i10Index')
#             i10index2 = extract_info(author_info2, 'i10Index')
#             answer = compare_values(i10index1, i10index2, "higher")
#         elif "higher" in question_text.lower() and "citedbycount" in question_text.lower():
#             citedByCount1 = extract_info(author_info1, 'citedByCount')
#             citedByCount2 = extract_info(author_info2, 'citedByCount')
#             answer = compare_values(citedByCount1, citedByCount2, "higher")
#         elif "higher works count" in question_text.lower():
#             worksCount1 = extract_info(author_info1, 'worksCount')
#             worksCount2 = extract_info(author_info2, 'worksCount')
#             answer = compare_values(worksCount1, worksCount2, "higher")
#         elif "higher two years citedness" in question_text.lower():
#             myc1 = extract_info(author_info1, 'myc')
#             myc2 = extract_info(author_info2, 'myc')
#             answer = compare_values(myc1, myc2, "higher")
#         else:
#             answer = "Information not available"
    
#     else:
#         answer = "Information not available"

#     answers.append({
#         'id': question_id,
#         'answer': answer
#     })

# with open('sch_set2_test_answers.json', 'w') as f:
#     json.dump(answers, f, indent=4)

