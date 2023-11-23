import openai
import traceback



class GPTs:
    def __init__(self, 
                 llm, 
                 name: str='',
                 description: str='',
                 system_prompt: str='', 
                 conversation_starters: list=[], 
                 tools_management=None,
                 tool_call='auto'
            ) -> None:
        self.llm = llm
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.conversation_starters = conversation_starters
        self.tools_management = tools_management
        self.tool_call = tool_call
        
        self.gpts_config = None
    
    def build(self):
        # init memory
        self.chat_memory = [{'role': 'system', 'content': self.system_prompt}]
        # tools
        if len(self.tools_management.tools) == 0:
            self.tools = None
        else:
            self.tools = self.tools_management.get_openai_format()
        # print GPTs information
        self.info()
    
    def update_memory(self, chat_message: list):
        '''
        update the conversations history and build history
        '''
        self.chat_memory.extend(chat_message)

    def chat(self, input: str) -> str:
        self.update_memory([{'role': 'user', 'content': input}])
        # chat
        response = self.llm.query(self.chat_memory, self.tools)
        print('GPTs responese: ', response['choices'][0]['message'])
        # tool
        if 'function_call' in response['choices'][0]['message']:
            output = self.tools_management.query_hf(response['choices'][0]['message']['function_call'])
        else:
            output = response['choices'][0]['message']['content']
        assistant_message = [{'role': 'assistant', 'content': output}]
        self.update_memory(assistant_message)
        return output

    def info(self):
        print('Information of the created GPTs:\n ')
        print('### name: ', self.name)
        print('### description: ', self.description)
        print('### system prompt: \n', self.system_prompt)
        print('### conversation starters: \n', '**'.join([s[0] for s in self.conversation_starters]))
        print('### tools: \n', self.tools)

