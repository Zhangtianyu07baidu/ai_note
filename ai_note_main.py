from ai_note.note import AINote
from elasticsearch import Elasticsearch
# import appbuilder

# note = AINote(True)

# message = appbuilder.Message(["2024年5月18日，拜访了客户王刚，他是自来水的主任，他的联系方式是13823454563",
#                               "2024年5月19日，拜访了客户李勇，他是电力公司的主任，他的联系方式是13823454564",
#                               "2024年5月19日，我拜访了客户王刚，他是自来水的主任，他的联系方式是13823454563",
#                               "2024年5月20日，我拜访了客户王刚，他是自来水的主任，他的联系方式是13823454563",
#                               "2024年5月21日，拜访了客户王五，他是煤矿公司的主任，他的联系方式是13823454567",
#                               "2024年5月21日，拜访了客户赵六，他是煤矿公司的主任，他的联系方式是13823454568",
#                               "2024年5月22日，拜访了客户孙七，他是煤矿公司的主任，他的联系方式是13823454569"])
# note.save_at_now(message)
# result = note.call_gpt("分析一下这周我拜访了哪几位客户，分别拜访了几次，将重要信息提取到简化的excel表格中")
# print(result)
# result = note.call_gpt("2024年5月20日，我拜访了客户李勇，他是自来水的主任，他的联系方式是13823454563")
# print(result)
# result = note.call_gpt("客户李勇的联系方式是什么？")
# print(result)

client = Elasticsearch(
  "https://6e073ff78e434e19802fda143c5204e8.us-central1.gcp.cloud.es.io:443",
  api_key="Rm5kUVRwQUIzelVaTnExMm1FZ2g6Q2g4U05ON1BTOS1GazJGRm9yTlJQdw=="
)

print(client.info())

# documents = [
#   { "index": { "_index": "ai_note", "_id": "9780553351927"}},
#   {"name": "Snow Crash", "author": "Neal Stephenson", "release_date": "1992-06-01", "page_count": 470, "_extract_binary_content": True, "_reduce_whitespace": True, "_run_ml_inference": True},
#   { "index": { "_index": "ai_note", "_id": "9780441017225"}},
#   {"name": "Revelation Space", "author": "Alastair Reynolds", "release_date": "2000-03-15", "page_count": 585, "_extract_binary_content": True, "_reduce_whitespace": True, "_run_ml_inference": True},
#   { "index": { "_index": "ai_note", "_id": "9780451524935"}},
#   {"name": "1984", "author": "George Orwell", "release_date": "1985-06-01", "page_count": 328, "_extract_binary_content": True, "_reduce_whitespace": True, "_run_ml_inference": True},
#   { "index": { "_index": "ai_note", "_id": "9781451673319"}},
#   {"name": "Fahrenheit 451", "author": "Ray Bradbury", "release_date": "1953-10-15", "page_count": 227, "_extract_binary_content": True, "_reduce_whitespace": True, "_run_ml_inference": True},
#   { "index": { "_index": "ai_note", "_id": "9780060850524"}},
#   {"name": "Brave New World", "author": "Aldous Huxley", "release_date": "1932-06-01", "page_count": 268, "_extract_binary_content": True, "_reduce_whitespace": True, "_run_ml_inference": True},
#   { "index": { "_index": "ai_note", "_id": "9780385490818"}},
#   {"name": "The Handmaid's Tale", "author": "Margaret Atwood", "release_date": "1985-06-01", "page_count": 311, "_extract_binary_content": True, "_reduce_whitespace": True, "_run_ml_inference": True},
# ]

# client.bulk(operations=documents, pipeline="ent-search-generic-ingestion")

client.create()

print(client.search(index="ai_note", q="snow"))
client.search(index="ai_note", body={
  "query": {
    "match": {
      "name": "snow"
    }
  }
})