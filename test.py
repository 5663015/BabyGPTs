import requests

API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": {
		"question": "What is my name?",
		"context": "My name is Clara and I live in Berkeley."
	},
})
print(output)