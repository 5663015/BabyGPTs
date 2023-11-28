import os
import io
import json
import uuid
import requests
from PIL import Image
from pydub import AudioSegment

CACHE_PATH = '.cache'


class Tools_Manager:
    def __init__(self) -> None:
        self.tools_all = {}
        self.tools_selected = {}
        self.hf_key = None
    
    def add_tool(self, tool: dict):
        '''
        add a new tool to dict
        '''
        self.tools_all[tool['name']] = tool
        self.tools_selected[tool['name']] = tool

    def get_tools_list(self) -> list:
        '''
        get the list of all tools
        '''
        return list(self.tools_all.keys())

    def update_selected_tools(self, selected: list):
        '''
        update the selected tools
        '''
        self.tools_selected = {}
        for tool_name in selected:
            self.tools_selected[tool_name] = self.tools_all[tool_name]

    def get_openai_format(self):
        '''
        change selected tools to openai format
        '''
        result = []
        for k, v in self.tools_selected.items():
            result.append(v['tool_info']['function'])
        return result

    def query_hf(self, payload: dict) -> str:
        '''
        call the HF API
        '''
        model_name = payload['name']
        model_type = self.tools_selected[model_name]['model_type']
        model_args = json.loads(payload['arguments'].replace('\n', ''))
        api_url = self.tools_selected[model_name]['model_url']
        headers = {"Authorization": f"Bearer {self.hf_key}"}

        response = requests.post(api_url, headers=headers, json=model_args)
        print('tool response:\n', response)
        output = self.parse_response(response, model_type)
        return output

    def save_image(self, img: Image) -> str:
        '''
        save the generated image to cache
        '''
        path = os.path.join(CACHE_PATH, f'images/{str(uuid.uuid4())[:10]}.png')
        img.save(path)
        return path

    def save_audio(self, audio: AudioSegment) -> str:
        '''
        save the generated audio to cache
        '''
        path = os.path.join(CACHE_PATH, f"audios/{str(uuid.uuid4())[:10]}.flac")
        with open(path, "wb") as f:
            audio.export(f, format="flac")
        return path

    def parse_response(self, response, task_type):
        '''
        parse the response of HF API
        '''
        if task_type == 'text-to-image':
            image = Image.open(io.BytesIO(response.content))
            return self.save_image(image)
        elif task_type == 'text-to-speech':
            speech = AudioSegment.from_file(io.BytesIO(response.content))
            return self.save_audio(speech)
