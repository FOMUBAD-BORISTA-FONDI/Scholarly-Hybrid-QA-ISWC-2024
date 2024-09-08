import json

# Define the input and output file paths
input_file = '../refined_context.json'
output_file = 'context-not-found.json'

# Function to filter elements with empty context
def filter_empty_context(input_path, output_path):
    try:
        # Read the original JSON file
        with open(input_path, 'r') as infile:
            data = json.load(infile)
        
        # Filter elements where context is empty
        filtered_data = [item for item in data if item.get('context') == '']
        
        # Write the filtered elements to the new JSON file
        with open(output_path, 'w') as outfile:
            json.dump(filtered_data, outfile, indent=4)
        
        print(f"Filtered data has been written to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
filter_empty_context(input_file, output_file)
