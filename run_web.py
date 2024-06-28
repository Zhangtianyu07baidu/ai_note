import os
import uuid
import gradio as gr
from ai_note.note import AINote

note = AINote(True)

def on_submit_knowledge(user_id, user_message, chatbot_messages):
    """知识点空间"""
    result = note.call_gpt(user_id, "knowledge", user_message)
    chatbot_messages.append([user_message, result])
    return "", chatbot_messages

def on_submit_schedule(user_id, user_message, chatbot_messages):
    """日程空间"""
    result = note.call_gpt(user_id, "schedule", user_message)
    chatbot_messages.append([user_message, result])
    return "", chatbot_messages

def on_submit_work(user_id, user_message, chatbot_messages):
    """工作空间"""
    result = note.call_gpt(user_id, "work", user_message)
    chatbot_messages.append([user_message, result])
    return "", chatbot_messages

def on_load(user_id):
    """加载"""
    if user_id == "":
        user_id = uuid.uuid4().hex
    return user_id



demo_introduction = """<h2>操作指南</h2>
<h3><产品简介></h3>
<p><strong>智能云笔记</strong> 为用户提供了强大的笔记管理功能，包括 <strong>存储</strong>、<strong>查询</strong>、<strong>删除</strong> 等操作。</p>
<h3><用户ID></h3>
<p>用户的唯一标识，每次刷新会重新生成，也可以用户输入，请妥善保管，切勿外传</p>
<h3><交互形式></h3>
<p>对话</p>
<h3><自定义空间划分></h3>
<p>可以划分不同的空间来分类和管理您的笔记，不同空间下存储的信息是完全隔离的，当前Demo示意如下：</p>
<ul>
  <strong>【工作】</strong>：专注于工作相关的内容，帮助您高效地组织和管理工作笔记。
  <br>
  <strong>【日程】</strong>：记录您的日程安排，让您不再错过任何重要的会议和活动。
  <br>
  <strong>【知识点】</strong>：存储和管理学习和研究中的重要知识点，让学习更加系统化。
</ul>
"""

# -------------------------------------------------------------------
# | Web UI                                                          |
# -------------------------------------------------------------------

PageTitle = "智能云笔记"
with gr.Blocks(title=PageTitle) as app:
    gr.Markdown(f"<h1 style='text-align:center;'>{PageTitle}</h1>")
    with gr.Row():
        with gr.Column(scale=1):
            textbox_user_id = gr.Textbox(value="", visible=True, label="用户ID")
            textarea_introduction = gr.Markdown(
                label="Demo功能指南", value=demo_introduction
            )
        with gr.Column(scale=3):
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

                    textbox_user_msg_work = gr.Textbox(label="用户输入", interactive=True)
                    button_submit_work = gr.Button(value="提交工作", variant="primary")

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
                    textbox_user_msg_schedule = gr.Textbox(label="用户输入", interactive=True)
                    button_submit_schedule = gr.Button(value="提交日程", variant="primary")

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
                    textbox_user_msg_knowledge = gr.Textbox(label="用户输入", interactive=True)
                    button_submit_knowledge = gr.Button(value="提交知识", variant="primary")

# -------------------------------------------------------------------
# | Events                                                          |
# -------------------------------------------------------------------

    work_inputs = [textbox_user_id, textbox_user_msg_work, chatbot_work]
    work_outputs = [textbox_user_msg_work, chatbot_work]
    textbox_user_msg_work.submit(on_submit_work, inputs=work_inputs, outputs=work_outputs)
    button_submit_work.click(on_submit_work, inputs=work_inputs, outputs=work_outputs)

    schedule_inputs = [textbox_user_id, textbox_user_msg_schedule, chatbot_schedule]
    schedule_outputs = [textbox_user_msg_schedule, chatbot_schedule]
    textbox_user_msg_schedule.submit(on_submit_schedule, inputs=schedule_inputs, outputs=schedule_outputs)
    button_submit_schedule.click(on_submit_schedule, inputs=schedule_inputs, outputs=schedule_outputs)

    knowledge_inputs = [textbox_user_id, textbox_user_msg_knowledge, chatbot_knowledge]
    knowledge_outputs = [textbox_user_msg_knowledge, chatbot_knowledge]
    textbox_user_msg_knowledge.submit(on_submit_knowledge, inputs=knowledge_inputs, outputs=knowledge_outputs)
    button_submit_knowledge.click(on_submit_knowledge, inputs=knowledge_inputs, outputs=knowledge_outputs)

    app.load(on_load, inputs=[textbox_user_id], outputs=[textbox_user_id])
    

def launch(server_port=8895):
    """启动web服务"""
    app.launch(server_port=server_port, share=False, server_name="0.0.0.0", show_api=False)

if __name__ == "__main__":
    launch()