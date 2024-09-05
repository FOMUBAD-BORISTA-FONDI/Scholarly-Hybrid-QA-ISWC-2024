import json
import requests

def get_author_name_from_dblp(author_dblp_uri):
    sparql_query = f"""
    PREFIX dblp: <https://dblp.org/rdf/schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT ?name
    WHERE {{
        {author_dblp_uri} dblp:creatorName ?name .
    }}
    """
    endpoint = "https://dblp-april24.skynet.coypu.org/sparql"
    response = requests.post(endpoint, data={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})

    if response.status_code == 200:
        results = response.json()
        if results['results']['bindings']:
            return results['results']['bindings'][0]['name']['value']
    print(f"Errors or no results in DBLP query: {response.text}")
    return None

def get_author_info_from_semopenalex(author_name):
    sparql_query = f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ns2: <https://semopenalex.org/ontology/>
    PREFIX org: <http://www.w3.org/ns/org#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX ns3: <http://purl.org/spar/bido/>

    SELECT ?author ?name ?memberOf ?citedByCount ?worksCount ?hindex ?i10Index ?myc
    WHERE {{
        {{
            ?author foaf:name ?name .
            ?author org:memberOf ?memberOf .
            ?author ns2:citedByCount ?citedByCount .
            ?author ns2:worksCount ?worksCount .
            ?author ns3:h-index ?hindex .
            ?author ns2:2YrMeanCitedness ?myc .
            ?author ns2:i10Index ?i10Index .

            FILTER(lcase(str(?name)) = lcase("{author_name}"))
        }}
        UNION
        {{
            ?author ns2:alternativeName ?altName .
            ?author foaf:name ?name .
            ?author org:memberOf ?memberOf .
            ?author ns2:citedByCount ?citedByCount .
            ?author ns2:worksCount ?worksCount .
            ?author ns3:h-index ?hindex .
            ?author ns2:2YrMeanCitedness ?myc .
            ?author ns2:i10Index ?i10Index .

            FILTER(lcase(str(?altName)) = lcase("{author_name}") && lcase(str(?altName)) != lcase(str(?name)))
        }}
    }}
    """

    endpoint = "https://semoa.skynet.coypu.org/sparql"
    response = requests.post(endpoint, data={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})

    if response.status_code == 200:
        results = response.json()
        if results['results']['bindings']:
            return results['results']['bindings'][0]
    print(f"Error or no results in SemOpenAlex query: {response.text}")
    return None

def extract_info(author_info, key):
    if author_info is None:
        return "Information not available"
    return author_info.get(key, {}).get('value', 'Information not available')

def get_institution_info_from_semopenalex(institution_uri):
    if not institution_uri:
        return None

    sparql_query = f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ns3: <https://semopenalex.org/ontology/>
    PREFIX ns4: <https://dbpedia.org/property/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?citedByCount ?worksCount ?homepage ?name ?countryCode ?rorType
    WHERE {{
        {institution_uri} a ns3:Institution ;
        ns3:citedByCount ?citedByCount ;
        ns3:worksCount ?worksCount ;
        foaf:homepage ?homepage ;
        foaf:name ?name ;
        ns4:countryCode ?countryCode ;
        ns3:rorType ?rorType .
    }}
    """
    endpoint = "https://semoa.skynet.coypu.org/sparql"
    response = requests.post(endpoint, data={"query": sparql_query}, headers={"Accept": "application/sparql-results+json"})
    if response.status_code == 200:
        results = response.json()
        if results['results']['bindings']:
            return results['results']['bindings'][0]
    print(f"Error or no results in SemOpenAlex query: {response.text}")
    return None

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

with open('sch_set2_test_questions.json', 'r') as f:
    test_questions = json.load(f)

answers = []

for question in test_questions:
    question_id = question['id']
    question_text = question['question']
    author_dblp_uri = question.get('author_dblp_uri')

    if isinstance(author_dblp_uri, str):
        # Single author case
        author_name = get_author_name_from_dblp(author_dblp_uri)
        author_info = get_author_info_from_semopenalex(author_name) if author_name else None

        if "years citedness" in question_text.lower():
            answer = extract_info(author_info, 'myc')
        elif "hindex" in question_text.lower():
            answer = extract_info(author_info, 'hindex')
        elif "i10index" in question_text.lower():
            answer = extract_info(author_info, 'i10index')
        elif "cited by count" in question_text.lower():
            answer = extract_info(author_info, 'citedByCount')
        elif "works count" in question_text.lower() or "workscount" in question_text.lower():
            answer = extract_info(author_info, 'worksCount')
        else:
            answer = "Information not available"

    elif isinstance(author_dblp_uri, list) and len(author_dblp_uri) == 2:
        # Comparative case for two authors
        author_name1 = get_author_name_from_dblp(author_dblp_uri[0])
        author_info1 = get_author_info_from_semopenalex(author_name1) if author_name1 else None

        author_name2 = get_author_name_from_dblp(author_dblp_uri[1])
        author_info2 = get_author_info_from_semopenalex(author_name2) if author_name2 else None

        if "higher" in question_text.lower() and "hindex" in question_text.lower():
            hindex1 = extract_info(author_info1, 'hindex')
            hindex2 = extract_info(author_info2, 'hindex')
            answer = compare_values(hindex1, hindex2, "higher")
        elif "higher" in question_text.lower() and "i10index" in question_text.lower():
            i10index1 = extract_info(author_info1, 'i10index')
            i10index2 = extract_info(author_info2, 'i10index')
            answer = compare_values(i10index1, i10index2, "higher")
        elif "higher" in question_text.lower() and "citedbycount" in question_text.lower():
            citedByCount1 = extract_info(author_info1, 'citedByCount')
            citedByCount2 = extract_info(author_info2, 'citedByCount')
            answer = compare_values(citedByCount1, citedByCount2, "higher")
        elif "higher works count" in question_text.lower():
            worksCount1 = extract_info(author_info1, 'worksCount')
            worksCount2 = extract_info(author_info2, 'worksCount')
            answer = compare_values(worksCount1, worksCount2, "higher")
        elif "higher two years citedness" in question_text.lower():
            myc1 = extract_info(author_info1, 'myc')
            myc2 = extract_info(author_info2, 'myc')
            answer = compare_values(myc1, myc2, "higher")
        else:
            answer = "Information not available"

    elif isinstance(author_dblp_uri, str) and "institution" in question_text.lower():
        # Institution case
        author_name = get_author_name_from_dblp(author_dblp_uri)
        author_info = get_author_info_from_semopenalex(author_name) if author_name else None

        institution_uri = extract_info(author_info, 'memberOf') if author_info else None
        institution_info = get_institution_info_from_semopenalex(institution_uri) if institution_uri else None

        if "institution cited by count" in question_text.lower():
            answer = extract_info(institution_info, 'citedByCount')
        elif "institution works count" in question_text.lower():
            answer = extract_info(institution_info, 'worksCount')
        else:
            answer = "Information not available"

    else:
        answer = "Information not available"

    print(f"Answer for question {question_id}: {answer}")
    answers.append({
        'id': question_id,
        'answer': answer
    })

with open('answers2.txt', 'w') as f:
    json.dump(answers, f, indent=2)

print("Answers have been written to answers2.txt")