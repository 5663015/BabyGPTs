import os
import io
import ast
import json
import uuid
import requests
import traceback
from PIL import Image
from Prompts import GPTs_builder_system_prompt


CACHE_PATH = '.cache'


class GPTsBuilder:
    def __init__(self, llm) -> None:
        self.system_prompt = GPTs_builder_system_prompt
        self.llm = llm
        self.chat_memory = [{'role': 'system', 'content': self.system_prompt}]
        self.build_history = []
        self.gpts_config = {}
        self.hf_key = None      # use to generate logo

    def update_memory(self, chat_message: list):
        '''
        update the conversations history and build history
        '''
        self.chat_memory.extend(chat_message)

    def chat(self, input: str) -> str:
        '''
        chat with chatgpt
        '''
        # user message, update memory
        input = f'''user's input {input}\nyour output: '''
        user_message = [{'role': 'user', 'content': input}]
        self.update_memory(user_message)

        # call chatgpt
        response = self.llm.query(self.chat_memory)
        output = response['choices'][0]['message']['content']
        output = output.replace('\n', '\\n')
        # assistant message, update memory
        assistant_message = [{'role': 'assistant', 'content': output}]
        self.update_memory(assistant_message)
        # config of GPTs
        try:
            self.gpts_config = json.loads(output)
            # self.gpts_config = ast.literal_eval(output)
        except:
            import warnings
            warnings.warn("ChatGPT didn't output right json format, the default json or previous json will be output!")
        
        return self.gpts_config

    def generate_logo(self, prompt):
        '''
        use stable-diffusion-xl-base-1.0 model to generate GPTs logo
        '''
        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {self.hf_key}"}
        try:
            prompt = prompt.replace('\n', '\\n')
            response = requests.post(api_url, headers=headers, json={"inputs": f"{prompt}"})
            print(response)
            path = os.path.join(CACHE_PATH, f'images/logo_{str(uuid.uuid4())[:10]}.png')
            image = Image.open(io.BytesIO(response.content))
            image = image.resize((128, 128))
            image.save(path)
            return path
        except: 
            traceback.print_exc()
            return os.path.join(CACHE_PATH, f'images/default.png')
    