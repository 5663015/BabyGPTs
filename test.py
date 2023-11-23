import requests

def test_hf():
	API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
	headers = {"Authorization": "Bearer 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"}

	def query(payload):
		response = requests.post(API_URL, headers=headers, json=payload)
		print(response.content)
		return response.content
	image_bytes = query({
		"inputs": "xiaomi phone, simaple style",
	})
	# You can access the image with PIL.Image for example
	import io
	from PIL import Image
	image = Image.open(io.BytesIO(image_bytes))
	image.save('sd.png')
	