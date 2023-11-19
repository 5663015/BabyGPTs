import traceback
from ChatGPT_api import LLM
from Prompts import GPTs_builder_system_prompt


class GPTsBuilder:
    def __init__(self) -> None:
        self.system_prompt = GPTs_builder_system_prompt
        self.llm = LLM()
        self.memory = [{'role': 'system', 'content': self.system_prompt}]

    def update_memory(self, message: list):
        self.memory.extend(message)

    def chat(self, input: str):
        user_message = [{'role': 'user', 'content': input}]
        self.update_memory(user_message)

        try:
            response = self.llm.query(self.memory)
            output = response['choices'][0]['message']['content']
            assistant_message = [{'role': 'assistant', 'content': output}]
            self.update_memory(assistant_message)
        except: 
            traceback.print_exc()
        return output


if __name__ == "__main__":
    builder = GPTsBuilder()
    input = '请做一个广告投放助手，用户根据自然语言交互进行广告投放，要包括选择商品、设置人群标签设置出价方式、设置商品图片和营销文案四个步骤。'
    output = builder.chat(input)
    print(output)
