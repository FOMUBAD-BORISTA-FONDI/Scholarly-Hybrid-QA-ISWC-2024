import requests
import json
import re
import wikipedia

def get_author_name_from_dblp(author_dblp_uri):
    sparql_query = f"""
    PREFIX dblp: <https://dblp.org/rdf/schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT ?name
    WHERE {{
        {author_dblp_uri} dblp:primaryCreatorName ?name .
    }}
    """
    endpoint = "https://dblp-april24.skynet.coypu.org/sparql"
    response = requests.post(endpoint, data={'query': sparql_query}, headers={'Accept': 'application/sparql-results+json'})

    if response.status_code == 200:
        results = response.json()
        if results['results']['bindings']:
            name = results['results']['bindings'][0]['name']['value']
            print(f"Author name from DBLP: {name}")
            return name
        else:
            print(f"No name found for {author_dblp_uri}")
            return None
    else:
        print(f"Error in SPARQL query execution for DBLP: {response.status_code}")
        return None

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

    SELECT ?citedByCount ?worksCount (STR(?homepage) AS ?homepage) (STR(?name) AS ?name) (STR(?countryCode) AS ?countryCode) (STR(?rorType) AS ?rorType)
    WHERE {{
        <{institution_uri}> a ns3:Institution ;
        ns3:citedByCount ?citedByCount ;
        ns3:worksCount ?worksCount ;
        foaf:homepage ?homepage ;
        foaf:name ?name ;
        ns4:countryCode ?countryCode ;
        ns3:rorType ?rorType .
    }}
    """

    endpoint = "https://semoa.skynet.coypu.org/sparql"
    response = requests.post(endpoint, data={"query": query}, headers={"Accept": "application/sparql-results+json"})
    if response.status_code == 200:
        results = response.json()
        if results['results']['bindings']:
            return results
        else:
            return None
    else:
        print(f"Error in SPARQL query execution for SemOpenAlex: {response.status_code}")
        return None

def get_wikipedia_text(author_name):
    try:
        page = wikipedia.page(author_name)
        text = page.content
        text = re.sub(r'\\u[\dA-Fa-f]{4}', '', text)

        return text
    except:
        print(f"No Wikipedia page found for {author_name}")
        return None

def formulate_info(author_details, institution_details, wikipedia_text):
    if author_details and author_details['results']['bindings']:
        author_info = author_details['results']['bindings'][0]
        author_name = author_info.get('name', {}).get('value', "Unknown name")
        author_hindex = author_info.get('hindex', {}).get('value', "Unknown")
        author_i10index = author_info.get('i10Index', {}).get('value', "Unknown")
        author_cbc = author_info.get('citedByCount', {}).get('value', "Unknown")
        author_wc = author_info.get('worksCount', {}).get('value', "Unknown")
        author_myc = author_info.get('2YrMeanCitedness', {}).get('value', "Unknown")
    else:
        author_name = "Unknown"
        author_hindex = author_i10index = author_cbc = author_wc = author_myc = "Unknown"

    if institution_details and institution_details['results']['bindings']:
        inst_info = institution_details['results']['bindings'][0]
        institution_name = inst_info.get('name', {}).get('value', "Unknown institution")
        institution_type = inst_info.get('rorType', {}).get('value', "Unknown type")
        institution_cbc = inst_info.get('citedByCount', {}).get('value', "Unknown")
        institution_wc = inst_info.get('worksCount', {}).get('value', "Unknown")
        institution_homepage = inst_info.get('homepage', {}).get('value', "Unknown homepage")
    else:
        institution_name = institution_type = institution_cbc = institution_wc = institution_homepage = "Unknown"

    context = f"Author: {author_name}\nAffiliation: {institution_name}\nNumerical metrics:\n- hIndex: {author_hindex}\n- i10Index: {author_i10index}\n- Cited by count: {author_cbc}\n- Works count: {author_wc}\n- Two-year mean citedness: {author_myc}\n\nInstitution: {institution_name}\nType: {institution_type}\nLocation: Unknown\nNumerical metrics:\n- Cited by count: {institution_cbc}\n- Works count: {institution_wc}\nHomepage: {institution_homepage}\n\nAdditional information: {wikipedia_text}"

    return context

def main(questions):
    results = []
    for question_data in questions:
        question_id = question_data['id']
        question_text = question_data['question']
        author_dblp_uri = question_data['author_dblp_uri']
        author_name = get_author_name_from_dblp(author_dblp_uri)

        if author_name:
            author_details = get_author_info_from_semopenalex(author_name)
            institution_uri = author_details['results']['bindings'][0]['memberOf']['value']
            institution_details = get_institution_info_from_semopenalex(institution_uri)
            wikipedia_text = get_wikipedia_text(author_name)

            context = formulate_info(author_details, institution_details, wikipedia_text)
            result = {
                "id": question_id,
                "question": question_text,
                "author_dblp_uri": author_dblp_uri,
                "context": context
            }
            results.append(result)

    output_file = "results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"Results have been saved to {output_file}")

if __name__ == "__main__":
    # Replace this with your list of questions
    questions = [
        {
            "id": "4d1bee00-977d-44f6-857e-3d494972b8b7",
            "question": "How many citations have the publications of the institution where the creator of 'Array Layouts for Comparison-Based Searching' works been cited?",
            "author_dblp_uri": "<https://dblp.org/pid/24/1769>"
        },
        {
            "id": "fbf9c001-cefa-41b3-9324-7ccf9132c114",
            "question": "Which university is the author of 'Multiclass learning with hypothesis constraints' affiliated with?",
            "author_dblp_uri": "<https://dblp.org/pid/08/543>"
        }
    ]
    main(questions)
