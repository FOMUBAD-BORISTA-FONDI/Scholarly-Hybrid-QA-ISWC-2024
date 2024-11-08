import json
import requests
import logging
import wikipedia

# Set up logging
logging.basicConfig(level=logging.INFO)


def get_author_name_from_dblp(author_dblp_uri):
    sparql_query = f"""
    PREFIX dblp: <https://dblp.org/rdf/schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT ?name
    WHERE {{
        <{author_dblp_uri}> dblp:primaryCreatorName ?name .
    }}
    """
    endpoint = "https://dblp-april24.skynet.coypu.org/sparql"
    try:
        response = requests.post(
            endpoint,
            data={"query": sparql_query},
            headers={"Accept": "application/sparql-results+json"},
        )
        response.raise_for_status()
        results = response.json()
        if results["results"]["bindings"]:
            name = results["results"]["bindings"][0]["name"]["value"]
            logging.info(f"Author name from DBLP: {name}")
            return name
        else:
            logging.warning(f"No name found for {author_dblp_uri}")
            return None
    except requests.RequestException as e:
        logging.error(f"Request error for DBLP: {e}")
        return None


def fetch_wikipedia_content(author_name):
    try:
        page_content = wikipedia.page(author_name).content
        logging.info(f"Fetched Wikipedia content for {author_name}")
        return page_content
    except wikipedia.exceptions.DisambiguationError as e:
        logging.error(f"Disambiguation error for {author_name}: {e.options}")
        return ""
    except wikipedia.exceptions.PageError:
        logging.error(f"No Wikipedia page found for {author_name}")
        return ""
    except Exception as e:
        logging.error(
            f"An error occurred while fetching Wikipedia content for {author_name}: {e}"
        )
        return ""


def process_file(input_file, output_file):
    with open(input_file, "r") as f:
        data = json.load(f)

    with open(output_file, "w") as f:  # Start the file with an empty list
        json.dump([], f)

    for element in data:
        author_dblp_uri = element["author_dblp_uri"]

        # Ignore entries where author_dblp_uri is a list (more than one link)
        if isinstance(author_dblp_uri, list):
            logging.warning(
                f"Ignoring question with multiple DBLP URIs: {element['id']}"
            )
            continue

        author_dblp_uri = author_dblp_uri.strip("<>")
        author_name = get_author_name_from_dblp(author_dblp_uri)

        if author_name:
            # Write to the file with empty wikipedia_content
            context_entry = {
                "id": element["id"],
                "author_name": author_name,
                "wikipedia_content": "",
            }

            with open(output_file, "r+") as f:
                file_data = json.load(f)
                file_data.append(context_entry)
                f.seek(0)
                json.dump(file_data, f, indent=4)

            logging.info(
                f"Author name for {author_name} written to {output_file} with empty Wikipedia content."
            )

            # Fetch Wikipedia content and update the file
            wikipedia_content = fetch_wikipedia_content(author_name)
            if wikipedia_content:
                # Update the entry in the file with the fetched Wikipedia content
                context_entry["wikipedia_content"] = wikipedia_content
                with open(output_file, "r+") as f:
                    file_data = json.load(f)
                    for entry in file_data:
                        if entry["id"] == element["id"]:
                            entry["wikipedia_content"] = wikipedia_content
                            break
                    f.seek(0)
                    json.dump(file_data, f, indent=4)

                logging.info(
                    f"Wikipedia content for {author_name} updated in {output_file}"
                )
            else:
                logging.warning(f"No Wikipedia content for author {author_name}")
        else:
            logging.warning(f"No author name retrieved for DBLP URI {author_dblp_uri}")


if __name__ == "__main__":
    input_file = "sch_set2_test_questions.json"
    output_file = "context_output_file.json"
    process_file(input_file, output_file)
