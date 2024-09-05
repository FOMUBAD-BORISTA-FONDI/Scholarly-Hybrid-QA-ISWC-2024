import requests
import json
import re
import csv
import os

def get_author_names_from_dblp(author_dblp_uri):
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
            names = [binding['name']['value'] for binding in results['results']['bindings']]
            return names
        else:
            print(f"No names found for {author_dblp_uri}")
            return []
    else:
        print(f"Error in SPARQL query execution for DBLP: {response.status_code}")
        return []

def get_author_info_from_semopenalex(author_name):
    query = f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ns2: <https://semopenalex.org/ontology/>
    PREFIX org: <http://www.w3.org/ns/org#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX ns3: <http://purl.org/spar/bido/>

    SELECT ?author ?name ?memberOf ?citedByCount ?worksCount ?hindex ?i10Index ?2YrMeanCitedness 
    WHERE {{
        {{
            ?author foaf:name ?name .
            ?author org:memberOf ?memberOf .
            ?author ns2:citedByCount ?citedByCount .
            ?author ns2:worksCount ?worksCount .
            ?author ns3:h-index ?hindex .
            ?author ns2:2YrMeanCitedness ?2YrMeanCitedness .
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
            ?author ns2:2YrMeanCitedness ?2YrMeanCitedness .
            ?author ns2:i10Index ?i10Index .

            FILTER(lcase(str(?altName)) = lcase("{author_name}") && lcase(str(?altName)) != lcase(str(?name)))
        }}
    }}
    """

    endpoint = "https://semoa.skynet.coypu.org/sparql"
    response = requests.post(endpoint, data={"query": query}, headers={"Accept": "application/sparql-results+json"})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data from SemOpenAlex: {response.status_code}")
        return None

def get_institution_info_from_semopenalex(institution_uri):
    query = f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ns3: <https://semopenalex.org/ontology/>
    PREFIX ns4: <https://dbpedia.org/property/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?citedByCount ?worksCount (STR(?homepage) AS ?homepage) (STR(?name) AS ?name) (STR(?countryCode) AS ?countryCode) (STR(?rorType) AS ?rorType) (STR(?acronym) AS ?acronym)
    WHERE {{
        <{institution_uri}> a ns3:Institution ;
        ns3:citedByCount ?citedByCount ;
        ns3:worksCount ?worksCount ;
        foaf:homepage ?homepage ;
        foaf:name ?name ;
        ns4:countryCode ?countryCode ;
        ns3:rorType ?rorType ;
        ns4:acronym ?acronym .
    }}
    """

    endpoint = "https://semoa.skynet.coypu.org/sparql"
    response = requests.post(endpoint, data={"query": query}, headers={"Accept": "application/sparql-results+json"})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error in SPARQL query execution for SemOpenAlex: {response.status_code}")
        return None

def get_wikipedia_text(author_name):
    try:
        with open('sch_text_extract_1.txt', 'r') as file:
            text = file.read()
            text = text.replace('\\n', ' ')
            text = text.replace('\\"', '"')
            text = text.replace("\\'", "'")
            text = text.replace('\\', '')
            text = re.sub(r'\\u[\dA-Fa-f]{4}', '', text)

            pattern = re.compile(r"\[\{'author_wikipedia_text': [\"'](.*?)[\"']\}\]", re.DOTALL)
            matches = pattern.findall(text)

            for match in matches:
                if author_name.lower() in match.lower():
                    return match.strip()
    except FileNotFoundError:
        print("The file 'sch_text_extract_1.txt' was not found.")
    return "No Wikipedia text found"

def process_question(question):
    dblp_uri = question.get('author_dblp_uri')
    question_id = question.get('id')
    question_ask = question.get('question')

    if isinstance(dblp_uri, str):
        dblp_uri = [dblp_uri]

    results = []
    unique_names = set()
    for uri in dblp_uri:
        author_names = get_author_names_from_dblp(uri)
        if author_names:
            for author_name in author_names:
                if author_name not in unique_names:
                    unique_names.add(author_name)
                    author_details = get_author_info_from_semopenalex(author_name)
                    institution_details = None
                    if author_details and author_details['results']['bindings']:
                        author_info = author_details['results']['bindings'][0]
                        member_of_uri = author_info['memberOf']['value']
                        institution_details = get_institution_info_from_semopenalex(member_of_uri)
                        wikipedia_text = get_wikipedia_text(author_name)

                        # print(f"result {institution_details['results']['bindings']}")
                        if institution_details != None:
                            if institution_details['results']['bindings']:
                                result = {
                                'Question': question_ask,
                                'Associated_author_uri': uri,
                                'id': question_id,
                                'author_name': author_names,
                                'hindex': author_info.get('hindex', {}).get('value', "Unknown"),
                                'i10index': author_info.get('i10Index', {}).get('value', "Unknown"),
                                'citedByCount': author_info.get('citedByCount', {}).get('value', "Unknown"),
                                'worksCount': author_info.get('worksCount', {}).get('value', "Unknown"),
                                '2YrMeanCitedness': author_info.get('2YrMeanCitedness', {}).get('value', "Unknown"),
                                'memberOf': member_of_uri,
                                'institution_name': institution_details['results']['bindings'][0].get('name', {}).get('value', "Unknown") if institution_details else "Unknown",
                                'institution_country': institution_details['results']['bindings'][0].get('countryCode', {}).get('value', "Unknown") if institution_details else "Unknown",
                                'institution_acronym': institution_details['results']['bindings'][0].get('acronym', {}).get('value', "Unknown") if institution_details else "Unknown",
                                'institution_type': institution_details['results']['bindings'][0].get('rorType', {}).get('value', "Unknown") if institution_details else "Unknown",
                                'institution_citedByCount': institution_details['results']['bindings'][0].get('citedByCount', {}).get('value', "Unknown") if institution_details else "Unknown",
                                'institution_worksCount': institution_details['results']['bindings'][0].get('worksCount', {}).get('value', "Unknown") if institution_details else "Unknown",
                                'wikipedia_text': wikipedia_text
                                }
                                results.append(result)
                            else:
                                result = {
                                'Question': question_ask,
                                'Associated_author_uri': uri,
                                'id': question_id,
                                'author_name': author_names,
                                'hindex': author_info.get('hindex', {}).get('value', "Unknown"),
                                'i10index': author_info.get('i10Index', {}).get('value', "Unknown"),
                                'citedByCount': author_info.get('citedByCount', {}).get('value', "Unknown"),
                                'worksCount': author_info.get('worksCount', {}).get('value', "Unknown"),
                                '2YrMeanCitedness': author_info.get('2YrMeanCitedness', {}).get('value', "Unknown"),
                                'memberOf': member_of_uri,
                                'institution_name': "Unknown",
                                'institution_country': "Unknown",
                                'institution_acronym': "Unknown",
                                'institution_type': "Unknown",
                                'institution_citedByCount': "Unknown",
                                'institution_worksCount': "Unknown",
                                'wikipedia_text': wikipedia_text
                                }
                                results.append(result)

                    else:
                        result = {
                            'Question': question_ask,
                            'Associated_author_uri': uri,
                            'id': question_id,
                            'author_name': author_names,
                            'hindex': "Unknown",
                            'i10index': "Unknown",
                            'citedByCount': "Unknown",
                            'worksCount': "Unknown",
                            '2YrMeanCitedness': "Unknown",
                            'memberOf': "Unknown",
                            'institution_name': "Unknown",
                            'institution_country': "Unknown",
                            'institution_acronym': "Unknown",
                            'institution_type': "Unknown",
                            'institution_citedByCount': "Unknown",
                            'institution_worksCount': "Unknown",
                            'wikipedia_text': "No Wikipedia text found"
                        }
                        results.append(result)

    return results

def write_to_csv(data, filename='author_institution_info.csv'):
    fieldnames = ['Question', 'Associated_author_uri', 'id', 'author_name', 'hindex', 'i10index', 'citedByCount', 'worksCount',
                  '2YrMeanCitedness', 'memberOf', 'institution_name', 'institution_country', 'institution_acronym', 'institution_type',
                  'institution_citedByCount', 'institution_worksCount', 'wikipedia_text']

    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in data:
            writer.writerow(row)

def get_processed_ids(filename='author_institution_info.csv'):
    processed_ids = set()
    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            processed_ids = set(row['id'] for row in reader)
    return processed_ids

# Load questions
with open('sch_set2_test_questions.json', 'r') as file:
    questions = json.load(file)

# Get already processed IDs
processed_ids = get_processed_ids()

# Process questions and write to CSV
for question in questions:
    if question['id'] not in processed_ids:
        results = process_question(question)
        if results:
            write_to_csv(results)
            print(f"Question {question['id']} traitée et sauvegardée.")
        else:
            # write_to_csv(results)
            print(f"institu empty array {results}")
            print(f"Aucun résultat trouvé pour la question {question['id']}. == results {results}")
    else:
        print(f"Question {question['id']} déjà traitée, ignorée.")

print("Toutes les questions ont été traitées.")
