# vectorstore.py - 벡터 저장소 구축과 디스크 저장
import sys
from pathlib import Path

# 2일차 2번 폴더의 metadata.py를 그대로 재활용 (import 경로에 추가)
META_DIR = Path(__file__).resolve().parent.parent / "2"   # .../day2_practice/2
PROJECT_DIR = META_DIR.parents[1]                         # .../sds-ax-practice
sys.path.insert(0, str(META_DIR))

from dotenv import load_dotenv
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma
import metadata

# metadata.py의 문서 경로가 상대경로라, 실행 위치와 무관하도록 절대경로로 교체
metadata.FILE_META = {
    str(META_DIR / path): meta for path, meta in metadata.FILE_META.items()
}

load_dotenv(PROJECT_DIR / ".env")
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name="us-east-1",
)

db = Chroma.from_documents(
    documents=metadata.load_chunks(),
    embedding=embeddings,
    collection_name="sds_policies",
    persist_directory=str(PROJECT_DIR / "chroma_db"),   # 이 폴더에 저장됩니다 (6일차까지 사용)
)
print(f"적재 완료: {db._collection.count()}개 청크")

# 의미 검색 확인 (점수 포함)
for q in ["월차 며칠 받을 수 있어?", "집에서 일해도 되나요?", "법카 등록 기한"]:
    hits = db.similarity_search_with_score(q, k=2)
    print(f"\n질문: {q}")
    for doc, score in hits:
        name = Path(doc.metadata["source"]).name
        print(f"  [{name}] (거리 {score:.3f}) {doc.page_content[:40]}...")

# 메타데이터 필터 검색
hits = db.similarity_search("경비 정산 규정", k=2, filter={"department": "총무팀"})
print(f"\n총무팀 문서로 한정 검색: {[Path(h.metadata['source']).name for h in hits]}")
