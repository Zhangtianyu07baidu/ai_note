import os
import gradio as gr
from ai_note.note import AINote
import appbuilder

note = AINote(True)

def on_submit(user_message, chatbot_messages):
    """提交按钮事件"""
    result = note.call_gpt(user_message)
    chatbot_messages.append([user_message, result])
    return "", chatbot_messages

# -------------------------------------------------------------------
# | Web UI                                                          |
# -------------------------------------------------------------------

PageTitle = "AI工作云笔记"
with gr.Blocks(title=PageTitle) as app:
    gr.Markdown(f"<h1 style='text-align:center;'>{PageTitle}</h1>")
    with gr.Column():
        chatbot_messages = gr.Chatbot(
            value=[],
            height=520,
            bubble_full_width=False,
            avatar_images=(
                (os.path.join(os.path.dirname(__file__), "./assets/human.png")),
                (os.path.join(os.path.dirname(__file__), "./assets/autogen.png")),
            ),
            show_copy_button=True,
        )

        textbox_user_msg = gr.Textbox(label="User Input", interactive=True)
        button_submit = gr.Button(value="提交", variant="primary")

# -------------------------------------------------------------------
# | Events                                                          |
# -------------------------------------------------------------------

    button_submit.click(
        on_submit,
        inputs=[
            textbox_user_msg,
            chatbot_messages
        ],
        outputs=[
            textbox_user_msg,
            chatbot_messages
        ]
    )

def launch(server_port=8895):
    """启动web服务"""
    app.launch(server_port=server_port, share=False, server_name="0.0.0.0", show_api=False)

if __name__ == "__main__":
    launch()