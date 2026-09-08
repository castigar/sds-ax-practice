# vectorstore.py - 벡터 저장소 구축과 디스크 저장
import sys
from pathlib import Path

# 2일차 2번 폴더의 metadata.py를 그대로 재활용 (import 경로에 추가)
META_DIR = Path(__file__).resolve().parent.parent / "4"   # .../day2_practice/4
PROJECT_DIR = META_DIR.parents[1]                         # .../sds-ax-practice
sys.path.insert(0, str(META_DIR))

# failures.py - 검색 실패 재현
from rag_chain import db

fail_queries = [
    "출장 신청서 TR-102 어디서 내?",   # 유형 1: 고유 기호
    "3년차 연차 가산 규정",            # 유형 2: 청크 경계에 걸릴 수 있음
    "그거 신청 어떻게 해?",            # 유형 4: 모호한 질문
]
for q in fail_queries:
    hits = db.similarity_search_with_score(q, k=2)
    print(f"\n질문: {q}")
    for doc, score in hits:
        print(f"  (거리 {score:.3f}) [{doc.metadata['source']}] {doc.page_content[:40]}")