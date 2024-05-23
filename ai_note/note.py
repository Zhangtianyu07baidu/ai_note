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
    try:
        timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        timeArray = time.strptime(time_str, "%Y-%m-%d")
    timestamp = int(time.mktime(timeArray))
    return timestamp

class RecordMetadata(BaseModel):
    timestamp: int

class AINote():
    """AI笔记"""

    def __init__(self, drop_exists: bool = False):
        """初始化"""
        self._create_vector_index(drop_exists)
        self._decision_app_id = "bf5c18b4-8244-4d8f-b290-af6573076e7b" # 决策的应用ID 
        self._analysis_app_id = "a5645664-645b-4d7b-860f-887d851cc3e6" # 分析的应用ID
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

    def call_gpt(self, msg: str) -> str:
        """调用模型"""
        builder = appbuilder.AppBuilderClient(self._decision_app_id)
        conversation_id = builder.create_conversation()
        run_result = builder.run(conversation_id, msg)
        print(run_result.model_dump_json(indent=4))
        client_answer: data_class.AppBuilderClientAnswer = run_result.content
        event: data_class.Event = client_answer.events[0]
        if event.status != "done" or event.event_type != "function_call" or event.content_type != "function_call":
            return client_answer.answer
        
        text_obj = event.detail["text"]
        arguments_obj = text_obj["arguments"]

        if "work_time" in arguments_obj and "work_detail" in arguments_obj:
            # 保存工作记录
            work_time = arguments_obj["work_time"]
            work_detail = arguments_obj["work_detail"]
            self.gpt_do_save(work_time, work_detail)
        
        if "keyword" in arguments_obj:
            # 查询工作记录
            keyword = arguments_obj["keyword"]
            start_time = arguments_obj["start_time"] if "start_time" in arguments_obj else ""
            end_time = arguments_obj["end_time"] if "end_time" in arguments_obj else ""
            return self.gpt_do_query(msg, keyword, start_time, end_time)

        return client_answer.answer

    def gpt_do_save(self, work_time: str, work_detail: str):
        """保存工作记录"""
        segments = appbuilder.Message([f"{work_time}：{work_detail}"])
        metadata = RecordMetadata(timestamp=to_timestamp(work_time))
        self.save(segments, metadata)
        print(f"保存成功！")
    
    def gpt_do_query(self, msg: str, keyword: str, start_time: str, end_time: str) -> str:
        """查询工作记录"""
        if keyword != "":
            query_message = self.query(keyword, 10)
        else:
            query_message = self.query(msg, 10)
        print(f"query_result:\n{query_message.model_dump_json(indent=4)}")
        records = []
        for query_record in query_message.content:
            text = query_record["text"]
            metadata = query_record["meta"]
            record_metadata = RecordMetadata.model_validate_json(metadata)
            # print(f"now_time: {to_local_time(record_metadata.timestamp)}")
            # 判断是否要加时间区间判断
            if start_time != "" and end_time != "":
                start_time_stamp = to_timestamp(start_time)
                end_time_stamp = to_timestamp(end_time)
                if record_metadata.timestamp >= start_time_stamp and record_metadata.timestamp <= end_time_stamp:
                    records.append(text)
            else:
                records.append(text)

        records_to_analysis = "\n".join(records)
        request_message = f"【待分析的工作记录】\n{records_to_analysis}\n【问题或要求】\n{msg}"
        print(request_message)
        return self._request_analysis(request_message)
    
    def _request_analysis(self, requst: str):
        """分析回答"""
        builder = appbuilder.AppBuilderClient(self._analysis_app_id)
        conversation_id = builder.create_conversation()
        run_result = builder.run(conversation_id, requst)
        print(run_result.model_dump_json(indent=4))
        client_answer: data_class.AppBuilderClientAnswer = run_result.content
        return client_answer.answer