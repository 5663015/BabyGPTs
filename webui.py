import random
import gradio as gr
from GPTs_builder import GPTsBuilder


builder = GPTsBuilder()



with gr.Blocks() as demo:
    with gr.Column():
        # ------------------------
        # builder chatbox
        # ------------------------
        gr.Markdown('# GPTs')

        # chatgpt configure
        gr.Markdown('## ChatGPT configure')
        with gr.Row():
            chatgpt_apikey = gr.Text(label='API KEY')
            chatgpt_model = gr.Text(label='model')
            chatgpt_base_url = gr.Text(label='base url')
            chatgpt_temperature = gr.Slider(label='temperature', minimum=0, maximum=2, value=0.2, step=0.01)
            chatgptr_top_k = gr.Slider(label='top_k', minimum=1, maximum=10, value=2, step=1)
            chatgpt_max_tokens = gr.Slider(label='max_tokens', minimum=1, value=200, step=1)

        with gr.Row():
            with gr.Column(scale=0.5):
                gr.Markdown('## GPTs builder')
                # create
                with gr.Tab('Create'):
                    builder_chatbot = gr.Chatbot()
                    builder_msg = gr.Textbox(placeholder="Enter to send", show_label=False)
                    def builder_respond(message, chat_history):
                        bot_message = builder.chat(message)     # input message to builder
                        chat_history.append((message, bot_message))
                        return "", chat_history
                    builder_msg.submit(builder_respond, inputs=[builder_msg, builder_chatbot], outputs=[builder_msg, builder_chatbot])
                    # preview
                    def preview_gpts():
                        return 
                    preview_button = gr.Button("Preview GPTs")
                    preview_button.click(preview_gpts, inputs=[], outputs=[])

                # configure
                with gr.Tab('Configure'):
                    gr.Markdown('**Name**')
                    gpts_name = gr.Text(show_label=False)
                    gr.Markdown('**Description**')
                    gpts_description = gr.Text(show_label=False)
                    gr.Markdown('**Instructions**')
                    gpts_instructions = gr.TextArea(show_label=False)
                    gr.Markdown('**Conversation starters**')
                    gpts_conversatio_starters1 = gr.Text(show_label=False)
                    gpts_conversatio_starters2 = gr.Text(show_label=False)
                    gpts_conversatio_starters3 = gr.Text(show_label=False)
                    gpts_conversatio_starters4 = gr.Text(show_label=False)
                    gr.Markdown('**Knowledge**')
                    gpts_knowledge_file = gr.UploadButton()
                    gr.Markdown('**Capabilities**')
                    gpts_capabilities = gr.CheckboxGroup(['Web Browsing', 'DALLEImage Generation', 'Code Interpreter'])
                    gr.Markdown('**Actions**')
                    gr.Dropdown()


            # ------------------------
            # GPTs chatbox
            # ------------------------
            with gr.Column(scale=0.5):
                gr.Markdown('## Your GPTs')
                gpts_chatbot = gr.Chatbot()
                gpts_msg = gr.Textbox(placeholder="Enter to send", show_label=False)
                
                def gpts_respond(message, chat_history):
                    bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
                    chat_history.append((message, bot_message))
                    return "", chat_history
                gpts_msg.submit(builder_respond, inputs=[gpts_msg, gpts_chatbot], outputs=[gpts_msg, gpts_chatbot])
                gr.Examples(['gpts_conversatio_starters1', 'gpts_conversatio_starters2', 'gpts_conversatio_starters4', 'gpts_conversatio_starters4'], 
                            inputs=[gpts_msg], label='Conversatio starters')

demo.launch(debug=True)
