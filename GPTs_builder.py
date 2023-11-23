import json
import traceback
from Prompts import GPTs_builder_system_prompt
from GPTs import GPTs


class GPTsBuilder:
    def __init__(self, llm) -> None:
        self.system_prompt = GPTs_builder_system_prompt
        self.llm = llm
        self.chat_memory = [{'role': 'system', 'content': self.system_prompt}]
        self.build_history = []
        self.gpts_config = {}

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
        user_message = [{'role': 'user', 'content': input}]
        self.update_memory(user_message)

        # call chatgpt
        response = self.llm.query(self.chat_memory)
        output = response['choices'][0]['message']['content']

        # assistant message, update memory
        assistant_message = [{'role': 'assistant', 'content': output}]
        self.update_memory(assistant_message)

        # config of GPTs
        # TODO
        try:
            self.gpts_config = json.loads(output)
        except:
            import warnings
            warnings.warn("ChatGPT didn't output right json format, the default json or previous json will be output!")
        return self.gpts_config




