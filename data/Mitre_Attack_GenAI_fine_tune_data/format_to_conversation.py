import json

def convert_to_conversational(input_data):
    prompt = input_data.get('prompt', '')
    content = input_data.get('content', '')
    completion = input_data.get('completion', '') 
    
    conversation = []
    if prompt:
        conversation.append({"role": "system", "content": prompt})
    if content:
        conversation.append({"role": "user", "content": content})
    if completion:
        conversation.append({"role": "assistant", "content": completion})

    return conversation

conversations = []
with open('mitre_two_fine_tune.jsonl', 'r') as f:
    for line in f:
        input_data = json.loads(line)
        conversation = convert_to_conversational(input_data)
        if conversation:
            conversations.append(conversation)

with open('conversational_two.json', 'w') as f:
    json.dump({"conversations": conversations}, f, indent=2)