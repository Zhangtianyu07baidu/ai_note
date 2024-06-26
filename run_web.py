import os
import gradio as gr
from ai_note.note import AINote
import appbuilder

note = AINote(True)

def on_submit_knowledge(user_message, chatbot_messages):
    """知识点空间"""
    result = note.call_gpt("knowledge", user_message)
    chatbot_messages.append([user_message, result])
    return "", chatbot_messages

def on_submit_schedule(user_message, chatbot_messages):
    """日程空间"""
    result = note.call_gpt("schedule", user_message)
    chatbot_messages.append([user_message, result])
    return "", chatbot_messages

def on_submit_work(user_message, chatbot_messages):
    """工作空间"""
    result = note.call_gpt("work", user_message)
    chatbot_messages.append([user_message, result])
    return "", chatbot_messages

# -------------------------------------------------------------------
# | Web UI                                                          |
# -------------------------------------------------------------------

PageTitle = "智能云笔记"
with gr.Blocks(title=PageTitle) as app:
    gr.Markdown(f"<h1 style='text-align:center;'>{PageTitle}</h1>")

    with gr.Tab("工作"):
        with gr.Column():
            chatbot_work = gr.Chatbot(
                value=[],
                height=520,
                bubble_full_width=False,
                avatar_images=(
                    (os.path.join(os.path.dirname(__file__), "./assets/human.png")),
                    (os.path.join(os.path.dirname(__file__), "./assets/autogen.png")),
                ),
                show_copy_button=True,
            )

            textbox_user_msg_work = gr.Textbox(label="User Input", interactive=True)
            button_submit_work = gr.Button(value="提交", variant="primary")

    with gr.Tab("日程"):
        with gr.Column():
            chatbot_schedule = gr.Chatbot(
                value=[],
                height=520,
                bubble_full_width=False,
                avatar_images=(
                    (os.path.join(os.path.dirname(__file__), "./assets/human.png")),
                    (os.path.join(os.path.dirname(__file__), "./assets/autogen.png")),
                ),
                show_copy_button=True,
            )
            textbox_user_msg_schedule = gr.Textbox(label="User Input", interactive=True)
            button_submit_schedule = gr.Button(value="提交", variant="primary")

    with gr.Tab("知识点"):
        with gr.Column():
            chatbot_knowledge = gr.Chatbot(
                value=[],
                height=520,
                bubble_full_width=False,
                avatar_images=(
                    (os.path.join(os.path.dirname(__file__), "./assets/human.png")),
                    (os.path.join(os.path.dirname(__file__), "./assets/autogen.png")),
                ),
                show_copy_button=True,
            )
            textbox_user_msg_knowledge = gr.Textbox(label="User Input", interactive=True)
            button_submit_knowledge = gr.Button(value="提交", variant="primary")

# -------------------------------------------------------------------
# | Events                                                          |
# -------------------------------------------------------------------

    button_submit_work.click(
        on_submit_work,
        inputs=[
            textbox_user_msg_work,
            chatbot_work
        ],
        outputs=[
            textbox_user_msg_work,
            chatbot_work
        ]
    )

    button_submit_schedule.click(
        on_submit_schedule,
        inputs=[
            textbox_user_msg_schedule,
            chatbot_schedule
        ],
        outputs=[
            textbox_user_msg_schedule,
            chatbot_schedule
        ]
    )

    button_submit_knowledge.click(
        on_submit_knowledge,
        inputs=[
            textbox_user_msg_knowledge,
            chatbot_knowledge
        ],
        outputs=[
            textbox_user_msg_knowledge,
            chatbot_knowledge
        ]
    )

def launch(server_port=8895):
    """启动web服务"""
    app.launch(server_port=server_port, share=False, server_name="0.0.0.0", show_api=False)

if __name__ == "__main__":
    launch()