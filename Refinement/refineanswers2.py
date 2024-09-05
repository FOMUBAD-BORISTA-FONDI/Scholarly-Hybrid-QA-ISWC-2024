import json

# Load the content of the two files
with open('/home/borista/Desktop/Scholarly-Hybrid-QA-ISWC-2024/prediction-3/prediction-3.json', 'r') as file3:
    prediction_3 = json.load(file3)

with open('/home/borista/Desktop/Scholarly-Hybrid-QA-ISWC-2024/prediction-1/LLMs/save-prediction/prediction-2.txt', 'r') as file2:
    prediction_2 = json.load(file2)

# Create a dictionary for quick lookup by id from prediction-3.json
id_to_answer = {item['id']: item['answer'] for item in prediction_3}

# Iterate over prediction_2, updating the answer if a matching id is found in prediction_3
for item in prediction_2:
    if item['id'] in id_to_answer:
        item['answer'] = id_to_answer[item['id']]

# Write the updated prediction_2 to a new file answers2.txt
with open('answers2.txt', 'w') as output_file:
    json.dump(prediction_2, output_file, indent=4)

print("Answers updated and saved to 'answers2.txt'.")
