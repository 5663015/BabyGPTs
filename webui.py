import os
import gradio as gr
import logging
import coloredlogs
from dotenv import load_dotenv
from GPTs_builder import GPTsBuilder
from GPTs import GPTs
from ChatGPT_api import LLM
from Tools import Tools_Manager


# set log
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

# load keys from .env
load_dotenv()
openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_base = os.environ['OPENAI_BASE']
openai_model = os.environ['OPENAI_MODEL']
hf_key = os.environ['HF_API_KEY']

# init chatgpt
llm = LLM(api_key=openai_api_key, api_base=openai_api_base, model=openai_model)

# init GPTsBuilder
builder = GPTsBuilder(llm)
logger.info('GPTsBuilder init done.')

# init tools
tools_management = Tools_Manager()
logger.info('tools management init done.')

# init GPTs
gpts = GPTs(llm, tools_management=tools_management)
logger.info('GPTs init done.')


# set parameters, for `model_button`
def set_model_params(temperature, max_tokens, top_p, frequency_penalty):
    llm.temperature = temperature
    llm.max_tokens = max_tokens
    llm.top_p = top_p
    llm.frequency_penalty = frequency_penalty
    builder.llm = llm
    gpts.llm = llm
    logger.info('Parameters of ChatGPT have been set.')
    gr.Info('Parameters of ChatGPT have been set.')
    

with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown('# BabyGPTs')
        gr.Markdown("BabyGPTs is a very simple implementation of OpenAI GPTs. It's current principle is to generate GPTs system instructions according to user's input, combined with custom tools, to achieve the construction of GPTs.")
        gr.Markdown('[GitHub](https://github.com/5663015/GPTs)')

        # chatgpt configure
        gr.Markdown('## ChatGPT configure')
        with gr.Row():
            chatgpt_temperature = gr.Slider(label='temperature', minimum=0, maximum=2, value=0.2, step=0.01)
            chatgpt_max_tokens = gr.Slider(label='max_tokens', minimum=1, maximum=4096, value=1000, step=1)
            chatgptr_top_p = gr.Slider(label='top_p', minimum=1, maximum=10, value=1, step=1)
            chatgpt_frequency_penalty = gr.Slider(label='frequency_penalty', minimum=-2, maximum=2, value=1.2, step=0.01)
            # set chatgpt parameters
            model_button = gr.Button('Set ChatGPT')
            model_button.click(
                    set_model_params, 
                    inputs=[chatgpt_temperature, chatgpt_max_tokens, chatgptr_top_p, chatgpt_frequency_penalty],
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
                    with gr.Row().style(equal_height=True):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown('**Logo**')
                            with gr.Column():
                                gpts_logo = gr.Image(type='filepath', interactive=False, height=128, width=128)
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
                        hf_tools_list = gr.CheckboxGroup(label='HF tools list', choices=[])
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
                            logger.info(f'add a new tool: {hf_model_name}')
                            return hf_tools_list.update(choices=tools_management.get_tools_list(), value=tools_management.get_tools_list())
                        hf_button.click(add_hf_tool, 
                                        inputs=[hf_model_url, hf_model_type, hf_model_description, hf_tool_params], 
                                        outputs=[hf_tools_list])
                        # select/unselect tools
                        def select_tools(selected):
                            tools_management.update_selected_tools(selected)
                        hf_tools_list.select(fn=select_tools, inputs=[hf_tools_list], outputs=[])

                # chatbot send message function
                def builder_respond(message, chat_history):
                    # chat
                    logger.info(f'[Builder ChatBot] ## user: {message}')
                    output = builder.chat(message)      # return config json
                    logger.info(f'[Builder ChatBot] ## assistant: {str(output)}')
                    # generate logo
                    logo = builder.generate_logo(output['logo_prompt'])
                    chat_history.append((message, output['response']))
                    return "", chat_history, output['name'], output['description'], logo, output['instructions'], output['conversation_starters'][0], output['conversation_starters'][1], output['conversation_starters'][2], output['conversation_starters'][3]
                builder_msg.submit(builder_respond, 
                                    inputs=[builder_msg, builder_chatbot], 
                                    outputs=[builder_msg, builder_chatbot, gpts_name, gpts_description, gpts_logo, gpts_instructions, gpts_conversatio_starters1, gpts_conversatio_starters2, gpts_conversatio_starters3, gpts_conversatio_starters4]
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
                    logger.info(f'[GPTs ChatBot] ## user: {message}')
                    bot_message = gpts.chat(message)
                    logger.info(f'[GPTs ChatBot] ## assistant: {bot_message}')

                    if os.path.isfile(bot_message):     # the output is an image or audio
                        chat_history += [(message, (bot_message,))]
                    else:       # the output is a str
                        chat_history.append((message, bot_message))
                    return "", chat_history
                gpts_msg.submit(gpts_respond, inputs=[gpts_msg, gpts_chatbot], outputs=[gpts_msg, gpts_chatbot])
                samples = [['gpts_conversatio_starters1'], ['gpts_conversatio_starters2'], ['gpts_conversatio_starters3'], ['gpts_conversatio_starters4']]
                gpts_conversatio_starters = gr.Dataset(
                    samples=samples, 
                    label='Conversatio starters', components=[gpts_msg], type="index")
                
                # preview button function and click action
                def preview_gpts(gpts_name, gpts_description, gpts_logo, gpts_instructions, gpts_conversatio_starters1, gpts_conversatio_starters2, gpts_conversatio_starters3, gpts_conversatio_starters4, hf_tools_list):
                    global samples
                    # update GPTs config and build
                    gpts.name = gpts_name
                    gpts.description = gpts_description
                    gpts.system_prompt = gpts_instructions
                    samples = [[gpts_conversatio_starters1], [gpts_conversatio_starters2], [gpts_conversatio_starters3], [gpts_conversatio_starters4]]
                    gpts.conversation_starters = samples
                    tools_management.update_selected_tools(hf_tools_list)
                    gpts.build()

                    gr.Info('You can chat with your GPTs.')
                    logger.info('preview GPTs')
                    return gpts_conversatio_starters.update(samples=gpts.conversation_starters), '', []
                preview_button.click(
                        preview_gpts, 
                        inputs=[gpts_name, gpts_description, gpts_logo, gpts_instructions, gpts_conversatio_starters1, gpts_conversatio_starters2, gpts_conversatio_starters3, gpts_conversatio_starters4, hf_tools_list], 
                        outputs=[gpts_conversatio_starters, gpts_msg, gpts_chatbot]
                    )
                # gpts_conversatio_starters click
                def load_conversatio_starters(id):
                    global samples
                    return samples[id][0]
                gpts_conversatio_starters.select(load_conversatio_starters, inputs=[gpts_conversatio_starters], outputs=[gpts_msg])


demo.launch(debug=True, show_error=True, enable_queue=True)

