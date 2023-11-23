import os
import openai
import traceback



class LLM:
    def __init__(self, 
                 api_key='',
                 api_base=None,
                 model='gpt-3.5-turbo',
                 temperature=0.,
                 max_tokens=1000,
                 top_p=2,
                 frequency_penalty=1.2,
                 ) -> None:
        openai.api_key = api_key
        openai.api_base = api_base

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.frequency_penalty = frequency_penalty
        self.top_p = top_p

    def query(self, messages, tools=None, tool_choice='auto'):
        try:
            if tools is None:
                response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        frequency_penalty=self.frequency_penalty
                    )
            else:
                response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        frequency_penalty=self.frequency_penalty,
                        functions=tools,
                        functionCall=tool_choice
                    )
        except Exception as e:
            traceback.print_exc()
            return str(e)
        return response



