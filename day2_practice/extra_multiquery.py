# extra_multiquery.py - 멀티 쿼리 Retriever
import logging
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from rag_chain import db, llm

logging.basicConfig()
logging.getLogger("langchain_classic.retrievers.multi_query").setLevel(logging.INFO)

mq = MultiQueryRetriever.from_llm(
    retriever=db.as_retriever(search_kwargs={"k": 3}), llm=llm
)
docs = mq.invoke("쉬는 것 관련 규정 알려줘")
print([d.metadata["source"] for d in docs])