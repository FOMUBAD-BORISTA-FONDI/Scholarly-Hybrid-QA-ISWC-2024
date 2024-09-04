import json

def compare_and_copy_wikipedia_content(file1_path, file2_path, output_path):
    # Read the contents of both files
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    # Create dictionaries with id as key for faster lookup
    dict1 = {item['id']: item for item in data1}
    dict2 = {item['id']: item for item in data2}

    # Compare and copy wikipedia_content to empty context
    for id, item in dict1.items():
        if id in dict2 and 'context' in item and item['context'] == "":
            if 'wikipedia_content' in dict2[id]:
                item['context'] = dict2[id]['wikipedia_content']

    # Write the updated data to the output file
    with open(output_path, 'w') as f_out:
        json.dump(data1, f_out, indent=2)

    print(f"Processed files. Output written to {output_path}")

# usage
file1_path = 'processed_sch_set2_test_questions.json'
file2_path = '../extract_wiki_context/context_output_file.json'
output_path = 'refined_context.json'

compare_and_copy_wikipedia_content(file1_path, file2_path, output_path)