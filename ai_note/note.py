import json
import os
import time
import openai
import appbuilder
from appbuilder.core.console.appbuilder_client import data_class
from elasticsearch import Elasticsearch
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

class AINote():
    """AI笔记"""

    def __init__(self, drop_exists: bool = False):
        """初始化"""
        self.es = Elasticsearch(
            "https://6e073ff78e434e19802fda143c5204e8.us-central1.gcp.cloud.es.io:443",
            api_key="Rm5kUVRwQUIzelVaTnExMm1FZ2g6Q2g4U05ON1BTOS1GazJGRm9yTlJQdw=="
        )

        if drop_exists:
            self.drop_index("work")
            self.drop_index("schedule")
            self.drop_index("knowledge")
        
        self.embedding_model = openai.AzureOpenAI(
            api_key="c851dabeeea24771a17b0ca07f38379c",
            api_version="2023-07-01-preview",
            azure_endpoint="https://openai2-east-us2-hk.openai.azure.com/",
        )

        self._decision_app_id = "bf5c18b4-8244-4d8f-b290-af6573076e7b" # 决策的应用ID 
        self._analysis_app_id = "a5645664-645b-4d7b-860f-887d851cc3e6" # 分析的应用ID

    def drop_index(self, index_name: str):
        """删除索引"""
        if self.es.indices.exists(index=index_name):
            response = self.es.indices.delete(index=index_name)
            print(f"Index {index_name} deleted: {response}")
        else:
            print(f"Index {index_name} does not exist.")

    def embedding(self, content: str):
        """嵌入"""
        embedding_result = self.embedding_model.embeddings.create(
            input=content,
            model="deploy_text_embedding_ada_002"
        )
        return embedding_result.data[0].embedding

    def save(self, index_name: str, work_time: str, work_detail: str):
        """保存笔记"""
        timestamp = to_timestamp(work_time)
        content = f"{work_time}：{work_detail}"
        response = self.es.index(index=index_name, body={
            "timestamp": timestamp,
            "content": content,
            "vector": self.embedding(content)
        })
        print(f"Document added: {response} in {index_name}")

    def query_with_embedding(self, index_name: str, content: str, k: int = 1):
        """查询笔记"""
        query_vector = self.embedding(content)
        resp = self.es.search(index=index_name, knn={
            "field": "vector",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": 100,
        })
        return resp

    def query_with_time_range(self, index_name: str, start_time: str, end_time: str, k: int = 10):
        """查询笔记"""
        resp = self.es.search(
            index=index_name,
            size=k,  # 限制返回的文档数量为k
            body={
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": to_timestamp(start_time),
                            "lte": to_timestamp(end_time)
                        }
                    }
                }
            }
        )
        return resp

    def query_with_embedding_and_time_range(self, index_name: str, content: str, start_time: str, end_time: str, k: int = 1):
        """查询笔记"""
        query_vector = self.embedding(content)
        resp = self.es.search(
            index=index_name,
            size=k,  # 限制返回的文档数量为k
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": to_timestamp(start_time),
                                        "lte": to_timestamp(end_time)
                                    }
                                }
                            },
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                                        "params": {
                                            "query_vector": query_vector
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )
        return resp

    def delete_with_time_range(self, index_name: str, start_time: str, end_time: str):
        """删除笔记"""
        self.es.delete_by_query(
            index=index_name,
            body={
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": to_timestamp(start_time),
                            "lte": to_timestamp(end_time)
                        }
                    }
                }
            }
        )
        print(f"Documents in the time range deleted successfully.")

    def call_gpt(self, sapce: str, msg: str, retry = 0) -> str:
        """调用模型"""
        if retry >= 3:
            return "对不起，我无法理解您的问题。"

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
            # 保存
            work_time = arguments_obj["work_time"]
            work_detail = arguments_obj["work_detail"]
            self.gpt_do_save(sapce, work_time, work_detail)
            return client_answer.answer
        
        if "keyword" in arguments_obj:
            # 查询
            keyword = arguments_obj["keyword"]
            start_time = arguments_obj["start_time"] if "start_time" in arguments_obj else ""
            end_time = arguments_obj["end_time"] if "end_time" in arguments_obj else ""
            return self.gpt_do_query(sapce, msg, keyword, start_time, end_time)

        if "delete_keyword" in arguments_obj:
            # 删除
            start_time = arguments_obj["start_time"] if "start_time" in arguments_obj else ""
            end_time = arguments_obj["end_time"] if "end_time" in arguments_obj else ""
            delete_resp = self.gpt_do_delete(sapce, start_time, end_time)
            if delete_resp == "":
                delete_resp = client_answer.answer
            return delete_resp

        # 返回格式不正确，再次尝试
        return self.call_gpt(sapce, msg, retry + 1)

    def gpt_do_save(self, space: str, work_time: str, work_detail: str):
        """保存"""
        self.save(space, work_time, work_detail)
    
    def gpt_do_query(self, space: str, msg: str, keyword: str, start_time: str, end_time: str) -> str:
        """查询"""
        if start_time != "" and end_time != "":
            query_result = self.query_with_time_range(space, start_time, end_time)
        else:
            content = keyword if keyword != "" else msg
            query_result = self.query_with_embedding(space, content, 5)
        
        records = []
        for hit in query_result["hits"]["hits"]:
            records.append(hit["_source"]["content"])

        if len(records) == 0:
            return "对不起，没有找到相关的记录，请重新确认时间。"

        records_to_analysis = "\n".join(records)
        request_message = f"【待分析的记录】\n{records_to_analysis}\n【问题或要求】\n{msg}"
        print(request_message)
        return self._request_analysis(request_message)
    
    def gpt_do_delete(self, space: str, start_time: str, end_time: str) -> str:
        """删除"""
        if start_time != "" and end_time != "":
            self.delete_with_time_range(space, start_time, end_time)
            return ""
        return "对不起，删除记录需要提供确切的关键字和时间范围。"

    def _request_analysis(self, requst: str):
        """分析回答"""
        builder = appbuilder.AppBuilderClient(self._analysis_app_id)
        conversation_id = builder.create_conversation()
        run_result = builder.run(conversation_id, requst)
        print(run_result.model_dump_json(indent=4))
        client_answer: data_class.AppBuilderClientAnswer = run_result.content
        return client_answer.answer