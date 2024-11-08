import json
import requests
from transformers import BertForQuestionAnswering, AutoTokenizer, pipeline

# Charger le modèle et le tokenizer pour le question-answering
model = BertForQuestionAnswering.from_pretrained("deepset/bert-base-cased-squad2")
tokenizer = AutoTokenizer.from_pretrained("deepset/bert-base-cased-squad2")


# Fonction pour obtenir le nom de l'auteur à partir de DBLP
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
    response = requests.post(
        endpoint,
        data={"query": sparql_query},
        headers={"Accept": "application/sparql-results+json"},
    )

    if response.status_code == 200:
        results = response.json()
        if results["results"]["bindings"]:
            name = results["results"]["bindings"][0]["name"]["value"]
            print(f"Author name from DBLP: {name}")
            return name
        else:
            print(f"No name found for {author_dblp_uri}")
            return None
    else:
        print(f"Error in SPARQL query execution for DBLP: {response.status_code}")
        return None


# Fonction pour obtenir les informations de l'auteur à partir de SemOpenAlex
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
    response = requests.post(
        endpoint,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
    )
    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     print(f"Error fetching data from SemOpenAlex: {response.status_code}")
    #     return None

    if response.status_code == 200:
        results = response.json()
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]

    return None


def extract_info(author_info, key):
    if author_info is None:
        return "Not Mentioned"
    return author_info.get(key, {}).get("value", "Not Mentioned")


def compare_values(value1, value2, comparison_type):
    if value1 == "Not Mentioned" or value2 == "Not Mentioned":
        return "Not Mentioned"

    try:
        value1 = float(value1)
        value2 = float(value2)
    except ValueError:
        return "Not Mentioned"

    if comparison_type == "higher":
        return max(value1, value2)
    elif comparison_type == "lower":
        return min(value1, value2)
    else:
        return "Invalid comparison type"


# Fonction pour obtenir des informations d'institution à partir de SemOpenAlex
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
    response = requests.post(
        endpoint,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
    )

    if response.status_code == 200:
        results = response.json()
        # print("result", results)
        if results["results"]["bindings"]:
            # print("result bindings", results['results']['bindings'][0])
            return results["results"]["bindings"][0]
    else:
        return None


# Open the output files in write mode
with open("save-prediction/prediction-2.txt", "w", encoding="utf-8") as outfile, open(
    "save-prediction/answers2context.txt", "w", encoding="utf-8"
) as outfile_context:

    # Write the opening brackets for the JSON arrays
    outfile.write("[\n")
    outfile_context.write("[\n")

    # Read the input file
    with open(
        "refineprocessedquestions/refined_context.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)

    null_count = 0
    total_questions = len(data)

    # Process each question
    for i, test_data in enumerate(data):
        try:
            question_id = test_data["id"]
            question_text = test_data["question"]
            context = test_data.get("context", "")
            author_dblp_uri = test_data.get("author_dblp_uri")
            answer = None

            print(f"Processing ID: {question_id} ({i+1}/{total_questions})")

            # Étape 1: Essayer de répondre avec les données de SemOpenAlex ou DBLP
            if isinstance(author_dblp_uri, str):
                # Cas d'un seul auteur
                author_name = get_author_name_from_dblp(author_dblp_uri)
                author_info = (
                    get_author_info_from_semopenalex(author_name)
                    if author_name
                    else None
                )
                institution_info = get_institution_info_from_semopenalex(
                    extract_info(author_info, "memberOf")
                )

                if "two years citedness".lower() in question_text.lower():
                    print("inside Two years Citedness")
                    answer = extract_info(author_info, "2YrMeanCitedness")
                    print("The answer of type is ", answer)
                if "hindex".lower() in question_text.lower():
                    print("inside HIndex")
                    answer = extract_info(author_info, "hindex")
                    print("The answer of hindex is ", answer)
                if (
                    "Which".lower() in question_text.lower()
                    and "affiliation".lower() in question_text.lower()
                ):
                    print("inside Which HIndex")
                    answer = extract_info(author_info, "name")
                    print("The answer of Which hindex is ", answer)
                if "i10index".lower() in question_text.lower():
                    print("inside i10index")
                    answer = extract_info(author_info, "i10Index")
                    print("The answer of i10index is ", answer)
                if (
                    "cited by count".lower() in question_text.lower()
                    or "citedbycount".lower() in question_text.lower()
                    or "citedby count".lower() in question_text.lower()
                ):
                    print("inside cited by count(author's)")
                    answer = extract_info(author_info, "citedByCount")
                    print("The answer of cited by count(authors) is ", answer)
                if (
                    "works count".lower() in question_text.lower()
                    or "workscount" in question_text.lower()
                ):
                    print("inside works count(Author)")
                    answer = extract_info(author_info, "worksCount")
                    print("The answer of works count(Author) is ", answer)
                if (
                    "cited by count".lower() in question_text.lower()
                    and "affiliation".lower()
                    or "affiliate".lower() in question_text.lower()
                ):
                    print("inside cited by count(institution)")
                    answer = extract_info(institution_info, "citedByCount")
                    print("The answer of cited by count(institution) is ", answer)
                if (
                    "cited by count".lower() in question_text.lower()
                    and "institution".lower() in question_text.lower()
                ):
                    print("inside cited by count(institution)")
                    answer = extract_info(institution_info, "citedByCount")
                    print("The answer of cited by count(institution) is ", answer)
                if "kind".lower() in question_text.lower():
                    print("inside kind(institution)")
                    answer = extract_info(institution_info, "rorType")
                    print("The answer of kind(institution) is ", answer)
                if "type".lower() in question_text.lower():
                    print("inside type")
                    answer = extract_info(institution_info, "rorType")
                    print("The answer of type is ", answer)
                if (
                    "What is the number of publications".lower()
                    in question_text.lower()
                    and (
                        "institution".lower() in question_text.lower()
                        or "affiliation".lower() in question_text.lower()
                    )
                ):
                    print("inside number of publications(institution,affiliation)")
                    answer = extract_info(institution_info, "worksCount")
                    print(
                        "The answer of number of publications(institution) is ", answer
                    )
                if (
                    "What is the number of publications".lower()
                    in question_text.lower()
                    and "affiliation".lower() in question_text.lower()
                ):
                    print("inside number of publications(affiliation)")
                    answer = extract_info(institution_info, "worksCount")
                    print(
                        "The answer of number of publications(affiliation) is ", answer
                    )
                if (
                    "What is the number of citations".lower() in question_text.lower()
                    and (
                        "institution".lower() in question_text.lower()
                        or "affiliation".lower() in question_text.lower()
                    )
                ):
                    print("inside number of citations(affiliation)")
                    answer = extract_info(institution_info, "citedByCount")
                    print("The answer of number of citations(affiliation) is ", answer)
                if (
                    "What is the number of publications".lower()
                    in question_text.lower()
                    and "cited".lower() in question_text.lower()
                ):
                    print("inside number of publications(cited)")
                    answer = extract_info(institution_info, "citedByCount")
                    print("The answer of number of publications(cited) is ", answer)
                if (
                    "How many citations".lower() in question_text.lower()
                    and "institution".lower() in question_text.lower()
                ):
                    print("inside How many citations")
                    answer = extract_info(institution_info, "citedByCount")
                if (
                    "How many papers".lower() in question_text.lower()
                    and "institution".lower() in question_text.lower()
                ):
                    print("inside How many papers")
                    answer = extract_info(institution_info, "worksCount")
                    print("The answer of How many papers(WorksCount) is ", answer)
                if (
                    "How many publications".lower() in question_text.lower()
                    and "affiliation".lower() in question_text.lower()
                ):
                    print("inside How many publications")
                    answer = extract_info(institution_info, "worksCount")
                    print("The answer of many publications(affiliation) is ", answer)
                if (
                    "How many books has ".lower()
                    in question_text.lower()
                    in question_text.lower()
                ):
                    print("inside many books has(author works)")
                    answer = extract_info(author_info, "worksCount")
                    print("The answer of many books has(author works) is ", answer)
                if "short name".lower() in question_text.lower():
                    print("inside short name")
                    answer = extract_info(institution_info, "acronym")
                    print("The answer of Shortname is ", answer)

            elif isinstance(author_dblp_uri, list) and len(author_dblp_uri) == 2:
                # Cas comparatif pour deux auteurs
                author_name1 = get_author_name_from_dblp(author_dblp_uri[0])
                author_info1 = (
                    get_author_info_from_semopenalex(author_name1)
                    if author_name1
                    else None
                )

                author_name2 = get_author_name_from_dblp(author_dblp_uri[1])
                author_info2 = (
                    get_author_info_from_semopenalex(author_name2)
                    if author_name2
                    else None
                )

                if "higher" in question_text.lower():
                    if "hindex" in question_text.lower():
                        hindex1 = extract_info(author_info1, "hindex")
                        hindex2 = extract_info(author_info2, "hindex")
                        answer = compare_values(hindex1, hindex2, "higher")
                    elif "i10index" in question_text.lower():
                        i10index1 = extract_info(author_info1, "i10Index")
                        i10index2 = extract_info(author_info2, "i10Index")
                        answer = compare_values(i10index1, i10index2, "higher")
                    elif "citedbycount" in question_text.lower():
                        citedByCount1 = extract_info(author_info1, "citedByCount")
                        citedByCount2 = extract_info(author_info2, "citedByCount")
                        answer = compare_values(citedByCount1, citedByCount2, "higher")
                    elif "works count" in question_text.lower():
                        worksCount1 = extract_info(author_info1, "worksCount")
                        worksCount2 = extract_info(author_info2, "worksCount")
                        answer = compare_values(worksCount1, worksCount2, "higher")
                    elif "two years citedness" in question_text.lower():
                        myc1 = extract_info(author_info1, "2YrMeanCitedness")
                        myc2 = extract_info(author_info2, "2YrMeanCitedness")
                        answer = compare_values(myc1, myc2, "higher")

            if answer and answer != "Not Mentioned":
                print(f"Answer found: {answer}")
            else:
                print("No answer found, using LLM")
                qa_pipeline = pipeline(
                    "question-answering", model=model, tokenizer=tokenizer
                )
                result = qa_pipeline(question=question_text, context=context)
                answer = result["answer"]

            if not answer:
                null_count += 1
                answer = "Not Mentioned"

            print(f"FINAL Answer: {answer}")

            # Create the output dictionaries
            prediction = {"id": question_id, "answer": answer}
            prediction_context = {
                "id": question_id,
                "question": question_text,
                "answer": answer,
                "context": context,
            }

            # Write the predictions to files
            json.dump(prediction, outfile, ensure_ascii=False, indent=4)
            json.dump(prediction_context, outfile_context, ensure_ascii=False, indent=4)

            # Add a comma and newline if it's not the last item
            if i < len(data) - 1:
                outfile.write(",\n")
                outfile_context.write(",\n")
            else:
                outfile.write("\n")
                outfile_context.write("\n")

            # Flush the files to ensure writing
            outfile.flush()
            outfile_context.flush()

        except Exception as e:
            print(f"An error occurred while processing ID {question_id}: {str(e)}")

    # Write the closing brackets for the JSON arrays
    outfile.write("]\n")
    outfile_context.write("]\n")

print(f"Processing complete. Total null predictions: {null_count}")
