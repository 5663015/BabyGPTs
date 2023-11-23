import os
import gradio as gr
import logging
import coloredlogs
from colorama import Fore, Style
from GPTs_builder import GPTsBuilder
from GPTs import GPTs
from ChatGPT_api import LLM
from Tools.hf_tools import HF_Tools


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


# init GPTsBuilder
def init_GPTsBuilder():
    llm = LLM()
    builder = GPTsBuilder(llm)
    logger.info('GPTsBuilder init done.')
    return builder
builder = init_GPTsBuilder()

# init tools
def init_tools():
    tools_management = HF_Tools()
    logger.info('tools management init done.')
    return tools_management
tools_management = init_tools()

# init GPTs
def init_GPTs():
    llm = LLM()
    gpts = GPTs(llm, tools_management=tools_management)
    logger.info('GPTs init done.')
    return gpts
gpts = init_GPTs()




# set parameters
def set_model_params(api_key, api_base, model, hf_key, temperature, max_tokens, top_p, frequency_penalty):

    model = 'gpt-3.5-turbo-16k'
    llm = LLM(api_key=api_key, api_base=api_base, model=model, temperature=temperature, max_tokens=max_tokens, 
              top_p=top_p, frequency_penalty=frequency_penalty)
    builder.llm = llm
    gpts.llm = llm
    tools_management.hf_key = hf_key
    logger.info('Parameters of ChatGPT have been set.')
    gr.Info('Parameters of ChatGPT have been set.')
    

with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown('# GPTs')

        # chatgpt configure
        gr.Markdown('## ChatGPT configure')
        with gr.Column():
            with gr.Row():
                chatgpt_api_key = gr.Text(label='API KEY', type='password')
                chatgpt_api_base = gr.Text(label='api base')
                chatgpt_model = gr.Text(label='model')
                hf_key = gr.Text(label='HuggingFace API KEY', type='password')
            with gr.Row():
                chatgpt_temperature = gr.Slider(label='temperature', minimum=0, maximum=2, value=0.2, step=0.01)
                chatgpt_max_tokens = gr.Slider(label='max_tokens', minimum=1, maximum=4096, value=1000, step=1)
                chatgptr_top_p = gr.Slider(label='top_p', minimum=1, maximum=10, value=1, step=1)
                chatgpt_frequency_penalty = gr.Slider(label='frequency_penalty', minimum=-2, maximum=2, value=1.2, step=0.01)
                # set chatgpt parameters
                model_button = gr.Button('Set ChatGPT')
            model_button.click(
                    set_model_params, 
                    inputs=[chatgpt_api_key, chatgpt_api_base, chatgpt_model, hf_key, chatgpt_temperature, chatgpt_max_tokens, chatgptr_top_p, chatgpt_frequency_penalty],
                    outputs=[]
                )
        
        with gr.Row():
            # ------------------------
            # builder chatbox
            # ------------------------
            with gr.Column(scale=0.5):
                gr.Markdown('## GPTs builder')
                # create
                with gr.Tab('Create'):
                    builder_chatbot = gr.Chatbot()
                    builder_msg = gr.Textbox(placeholder="Enter to send", show_label=False)
                    
                # configure
                with gr.Tab('Configure'):
                    gr.Markdown('**Name**')
                    gpts_name = gr.Text(show_label=False)
                    with gr.Row():
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown('**Logo**')
                            with gr.Column():
                                gpts_logo = gr.Image()
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown('**Description**')
                            with gr.Column():
                                gpts_description = gr.TextArea(show_label=False)
                    gr.Markdown('**Instructions**')
                    gpts_instructions = gr.TextArea(show_label=False)
                    gr.Markdown('**Conversation starters**')
                    gpts_conversatio_starters1 = gr.Text(show_label=False)
                    gpts_conversatio_starters2 = gr.Text(show_label=False)
                    gpts_conversatio_starters3 = gr.Text(show_label=False)
                    gpts_conversatio_starters4 = gr.Text(show_label=False)
                    # gr.Markdown('**Knowledge**')      # TODO
                    # gpts_knowledge_file = gr.UploadButton()
                    # gr.Markdown('**Capabilities**')
                    # gpts_capabilities = gr.CheckboxGroup(['Web Browsing', 'DALLEImage Generation', 'Code Interpreter'])
                    gr.Markdown('**Actions**')
                    with gr.Tab('HuggingFace Tools'):
                        hf_model_url = gr.Text(label='model url')
                        hf_model_type = gr.Dropdown(['text-to-image', 'text-to-speech'], label='model_type')
                        hf_model_description = gr.Text(label='model description')
                        hf_tool_params = gr.DataFrame(label='parameters set', 
                                                      headers=['param_name', 'type', 'description', 'required'], col_count=(4, 'fixed'), row_count=(1, 'fixed'))
                        hf_button = gr.Button('add tool')
                        hf_tools_list = gr.Dropdown(label='HF tools list', multiselect=True, show_label=True)
                        # add tools
                        def add_hf_tool(hf_model_url, hf_model_type, hf_model_description, hf_tool_params):
                            # tool's information
                            hf_model_name = hf_model_url.split('/')[-1].replace('-', '_').replace('.', '_')
                            params = {}
                            required = []
                            for _, p in hf_tool_params.iterrows():
                                params[p["param_name"]] = {"type": p["type"], "description": p["description"]}
                                if p["required"] == 'true':
                                    required.append(p['param_name'])
                            tool = {
                                    "name": hf_model_name,
                                    "model_type": hf_model_type,
                                    "model_url": hf_model_url,
                                    "tool_info": {          # openai function calling format
                                        "type": "function",
                                        "function": {
                                            "name": hf_model_name,
                                            "description": hf_model_description,
                                            "parameters": {
                                                "type": "object",
                                                "properties": params,
                                                "required": required,
                                            },
                                        }
                                    }
                                }
                            # add tool
                            tools_management.add_tool(tool)
                            return hf_tools_list.update(choices=tools_management.get_tools_list(), value=tools_management.get_tools_list())
                        hf_button.click(add_hf_tool, 
                                        inputs=[hf_model_url, hf_model_type, hf_model_description, hf_tool_params], 
                                        outputs=[hf_tools_list])
                        # TODO:select/del tools
                        def select_tools(hf_tools_list):
                            pass
                        hf_tools_list.select(fn=select_tools, inputs=[hf_tools_list], outputs=[hf_tools_list])

                # chatbot send message function
                def builder_respond(message, chat_history):
                    # chat
                    output = builder.chat(message)      # return config json
                    # bot_message = builder.build()
                    logger.info('response of builder chat:\n' + str(output))
                    # generate logo

                    chat_history.append((message, output['response']))
                    return "", chat_history, output['name'], output['description'], output['instructions'], output['conversation_starters'][0], output['conversation_starters'][1], output['conversation_starters'][2], output['conversation_starters'][3]
                builder_msg.submit(builder_respond, 
                                    inputs=[builder_msg, builder_chatbot], 
                                    outputs=[builder_msg, builder_chatbot, gpts_name, gpts_description, gpts_instructions, gpts_conversatio_starters1, gpts_conversatio_starters2, gpts_conversatio_starters3, gpts_conversatio_starters4]
                                )

            # ------------------------
            # GPTs chatbox
            # ------------------------
            with gr.Column(scale=0.5):
                gr.Markdown('## Your GPTs')
                # preview your GPTs
                preview_button = gr.Button("Preview GPTs")      # the preview function and click action is below

                # chatbox
                gpts_chatbot = gr.Chatbot()
                gpts_msg = gr.Textbox(placeholder="Enter to send", show_label=False)
                
                def gpts_respond(message, chat_history):
                    bot_message = gpts.chat(message)     # input message to builder
                    if os.path.isfile(bot_message):     # the output is an image or audio
                        # if bot_message.endswith('.png'):
                        chat_history += [(message, (bot_message,))]
                    else:
                        chat_history.append((message, bot_message))
                    return "", chat_history
                gpts_msg.submit(gpts_respond, inputs=[gpts_msg, gpts_chatbot], outputs=[gpts_msg, gpts_chatbot])
                gpts_conversatio_starters = gr.Dataset(
                    samples=[['gpts_conversatio_starters1'], ['gpts_conversatio_starters2'], ['gpts_conversatio_starters3'], ['gpts_conversatio_starters4']], 
                    label='Conversatio starters', components=[gpts_msg], type="values")
                
                # preview button function and click action
                def preview_gpts(gpts_name, gpts_description, gpts_logo, gpts_instructions, gpts_conversatio_starters1, gpts_conversatio_starters2, gpts_conversatio_starters3, gpts_conversatio_starters4):
                    # update GPTs config and build
                    gpts.name = gpts_name
                    gpts.description = gpts_description
                    gpts.system_prompt = gpts_instructions
                    gpts.conversation_starters = [[gpts_conversatio_starters1], [gpts_conversatio_starters2], [gpts_conversatio_starters3], [gpts_conversatio_starters4]]
                    print(gpts.conversation_starters)   # TODO
                    gpts.build()
                    gr.Info('You can chat with your GPTs.')
                    logger.info('preview GPTs')
                    return gpts_conversatio_starters.update(samples=gpts.conversation_starters)
                preview_button.click(
                        preview_gpts, 
                        inputs=[gpts_name, gpts_description, gpts_logo, gpts_instructions, gpts_conversatio_starters1, gpts_conversatio_starters2, gpts_conversatio_starters3, gpts_conversatio_starters4], 
                        outputs=[gpts_conversatio_starters]
                    )
                # gpts_conversatio_starters click
                # TODO
                def load_conversatio_starters(example):
                    print(example)
                    return example[0]
                gpts_conversatio_starters.click(load_conversatio_starters, inputs=[gpts_conversatio_starters], outputs=[gpts_msg])


demo.launch(debug=True, show_error=True, enable_queue=True)

# 帮我做一个广告投放助手，包括选品、设置创意、设置投放人群、设置出价4个阶段。
# https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0