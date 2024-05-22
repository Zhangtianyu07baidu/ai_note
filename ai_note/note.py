import json
import os
import time
import appbuilder
from appbuilder.core.console.appbuilder_client import data_class
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

def to_local_time(timestamp: int) -> str:
    """将时间戳转换为本地时间"""
    time_local = time.localtime(timestamp)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def to_timestamp(time_str: str) -> int:
    """将时间字符串转换为时间戳"""
    timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(timeArray))
    return timestamp

class RecordMetadata(BaseModel):
    timestamp: int

class AINote():
    """AI笔记"""

    def __init__(self, drop_exists: bool = False):
        """初始化"""
        self._create_vector_index(drop_exists)
        self._save_app_id = "539ebeaf-0640-493e-8a3d-9c47385ca0b9" # 保存工作记录的应用ID
        self._query_app_id = "9e4f3211-5f4f-4eed-bc7a-5404add491ca" # 查询工作记录的应用ID
        self._analysis_app_id = "1aaa0462-d5ef-43cf-968f-e7a430687fb8" # 分析工作记录的应用ID
        self._answer_app_id = "a5645664-645b-4d7b-860f-887d851cc3e6" # 回答问题的应用ID
        # self._data_visualize_app_id = "554ce20a-0fac-425f-ad74-c7290c71d7e3" # 数据可视化的应用ID

    def _create_vector_index(self, drop_exists: bool):
        """创建向量数据库"""
        self.vector_index = appbuilder.BaiduVDBVectorStoreIndex(
            instance_id="vdb-bj-guhdhzgqvyrj",
            api_key="Shenzhou6hao",
            table_params=appbuilder.TableParams(
                dimension=384,
                replication=1,
                drop_exists=drop_exists
            )
        )

    def save_at_now(self, segments: appbuilder.Message):
        """以当前时间戳保存工作记录"""
        now = int(time.time())
        metadata = RecordMetadata(timestamp=now)
        self.save(segments, metadata)

    def save_at_time_specific(self, segments: appbuilder.Message, time: str = "2024-05-18 12:00:00"):
        """以指定时间保存工作记录"""
        timestamp = to_timestamp(time)
        metadata = RecordMetadata(timestamp=timestamp)
        self.save(segments, metadata)

    def save(self, segments: appbuilder.Message, metadata: RecordMetadata):
        """保存工作记录"""
        self.vector_index.add_segments(segments, metadata.model_dump_json(indent=4))

    def query(self, content: str, k: int = 1) -> appbuilder.Message:
        """查询工作记录"""
        query_message = appbuilder.Message(content)
        retriever = self.vector_index.as_retriever()
        res = retriever.run(query_message, top_k=k)
        return res

    def gpt_save(self, msg: str) -> str:
        """保存工作记录"""
        builder = appbuilder.AppBuilderClient(self._save_app_id)
        conversation_id = builder.create_conversation()
        conversation_content = f"帮我保存一下这个工作记录：{msg}"
        run_result = builder.run(conversation_id, conversation_content)
        # print(run_result.model_dump_json(indent=4))
        client_answer: data_class.AppBuilderClientAnswer = run_result.content
        event: data_class.Event = client_answer.events[0]
        if event.status != "done" or event.event_type != "function_call" or event.content_type != "function_call":
            return "保存失败，请重试！"
        
        text_obj = event.detail["text"]
        arguments_obj = text_obj["arguments"]
        if "work_time" in arguments_obj and "work_detail" in arguments_obj:
            work_time = arguments_obj["work_time"]
            work_detail = arguments_obj["work_detail"]
            segments = appbuilder.Message([f"{work_time}：{work_detail}"])
            metadata = RecordMetadata(timestamp=to_timestamp(work_time))
            self.save(segments, metadata)
            print(f"work_time: {work_time}, work_detail: {work_detail}")
            answer = client_answer.answer
            return answer

        return "保存失败，请重试！"

    def gpt_query(self, query: str) -> str:
        """查询工作记录"""
        builder = appbuilder.AppBuilderClient(self._query_app_id)
        conversation_id = builder.create_conversation()
        conversation_content = f"帮我搜索：{query}"
        run_result = builder.run(conversation_id, conversation_content)
        # print(run_result.model_dump_json(indent=4))
        client_answer: data_class.AppBuilderClientAnswer = run_result.content
        event: data_class.Event = client_answer.events[0]
        if event.status != "done" or event.event_type != "function_call" or event.content_type != "function_call":
            return "抱歉，查询失败，请再明确一下您的问题或要求再试一次！"
        
        text_obj = event.detail["text"]
        arguments_obj = text_obj["arguments"]
        if "keyword" in arguments_obj:
            keyword = arguments_obj["keyword"]
            print(f"keyword: {keyword}")
            query_message = self.query(keyword, 3)
            print(f"query_result:\n{query_message.model_dump_json(indent=4)}")
            request_message = f"【查询到的工作记录】\n{query_message}\n【问题或要求】\n{query}"
            print(request_message)
            return self._request_answer(request_message)

        return "抱歉，查询失败，请再明确一下您的问题或要求再试一次！"

    def _request_answer(self, requst: str):
        """请求回答"""
        builder = appbuilder.AppBuilderClient(self._answer_app_id)
        conversation_id = builder.create_conversation()
        run_result = builder.run(conversation_id, requst)
        client_answer: data_class.AppBuilderClientAnswer = run_result.content
        return client_answer.answer

    def gpt_analysis(self, content: str) -> str:
        """分析工作记录"""
        builder = appbuilder.AppBuilderClient(self._analysis_app_id)
        conversation_id = builder.create_conversation()
        conversation_content = f"帮我分析：{content}"
        run_result = builder.run(conversation_id, conversation_content)
        # print(run_result.model_dump_json(indent=4))
        client_answer: data_class.AppBuilderClientAnswer = run_result.content
        event: data_class.Event = client_answer.events[0]
        if event.status != "done" or event.event_type != "function_call" or event.content_type != "function_call":
            return "抱歉，分析失败，请将您的需求描述的再细致一些，然后再试一次！"
        
        text_obj = event.detail["text"]
        arguments_obj = text_obj["arguments"]
        if "start_time" in arguments_obj and "end_time" in arguments_obj and "keyword" in arguments_obj:
            start_time = arguments_obj["start_time"]
            end_time = arguments_obj["end_time"]
            keyword = arguments_obj["keyword"]
            print(f"start_time: {start_time}, end_time: {end_time}, keyword: {keyword}")
            query_message = self.query(keyword, 10)
            print(f"query_result:\n{query_message.model_dump_json(indent=4)}")
            records = []
            for query_record in query_message.content:
                text = query_record["text"]
                metadata = query_record["meta"]
                record_metadata = RecordMetadata.model_validate_json(metadata)
                # print(f"now_time: {to_local_time(record_metadata.timestamp)}")
                if record_metadata.timestamp >= to_timestamp(start_time) and record_metadata.timestamp <= to_timestamp(end_time):
                    records.append(text)
            records_to_analysis = "\n".join(records)
            request_message = f"【待分析的工作记录】\n{records_to_analysis}\n【要求】\n分析：{content}"
            print(request_message)
            return self._request_analysis(request_message)

        return "抱歉，分析失败，请将您的需求描述的再细致一些，然后再试一次！"
    
    def _request_analysis(self, requst: str):
        """请求回答"""
        builder = appbuilder.AppBuilderClient(self._answer_app_id)
        conversation_id = builder.create_conversation()
        run_result = builder.run(conversation_id, requst)
        print(run_result.model_dump_json(indent=4))
        client_answer: data_class.AppBuilderClientAnswer = run_result.content
        return client_answer.answer