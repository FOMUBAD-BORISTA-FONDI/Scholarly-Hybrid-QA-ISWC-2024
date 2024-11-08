import json

# Load the content of the files
with open('../prediction-3/prediction-3.json', 'r') as file3:
    prediction_3 = json.load(file3)

with open('../prediction-1/LLMs/save-prediction/my-prediction-2.txt', 'r') as file2:
    prediction_2 = json.load(file2)

# Create a dictionary for quick lookup by id from prediction-3.json
id_to_answer = {item['id']: item['answer'] for item in prediction_3}

# Track the ids that are already in prediction_2 to avoid duplication
existing_ids = {item['id'] for item in prediction_2}

# Iterate over prediction_2, updating the answer if a matching id is found in prediction_3
for item in prediction_2:
    pred_id = item['id']
    if pred_id in id_to_answer:
        pred3_answer = id_to_answer[pred_id]
        pred2_answer = item.get('answer', None)
        
        # Only update if pred3 answer is not null and it's different from the current answer
        if pred3_answer is not None and pred3_answer != pred2_answer:
            item['answer'] = pred3_answer

# Now, check for entries in prediction_3 that are missing in prediction_2 and add them
for pred_item in prediction_3:
    if pred_item['id'] not in existing_ids:
        # Add missing items with only the 'id' and 'answer'
        prediction_2.append({
            'id': pred_item['id'],
            'answer': pred_item['answer']
        })

# Write the updated prediction_2 (including any new additions) to a new file answers2.txt
with open('answers2.txt', 'w') as output_file:
    json.dump(prediction_2, output_file, indent=4)

print("Answers updated and saved to 'answers2.txt'")

