import os
import openai


os.environ['OPENAI_API_KEY'] = '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'


class LLM:
    def __init__(self, 
                 model='gpt-3.5-turbo',
                 temperature=0.,
                 max_tokens=1000,
                 ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        
    def query(self, messages):
        response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            
            )
        return response



