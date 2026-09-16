# router_only.py - Supervisor의 핵심인 라우팅 결정만 분리해 관찰

# typing.Literal: "이 값은 아래 나열된 문자열 중 하나만 가능" 이라고 타입으로 못박는 도구
from typing import Literal
# load_dotenv: 같은 폴더(또는 상위)의 .env 파일을 읽어 환경변수로 올려주는 함수
from dotenv import load_dotenv
# BaseModel: 데이터 구조(스키마)를 클래스로 정의하는 부모 클래스
# Field: 그 구조의 각 항목에 설명/기본값 같은 부가정보를 붙이는 함수
from pydantic import BaseModel, Field
# ChatBedrockConverse: AWS Bedrock의 Converse API로 LLM을 호출하는 LangChain 래퍼 클래스
from langchain_aws import ChatBedrockConverse

# .env 실행 → AWS 키, 리전 등이 환경변수로 로드됨 (아래 LLM 호출이 이걸 씀)
load_dotenv()


# Route: LLM이 "반드시 이 모양으로" 답하게 만들 출력 스키마.
# class = 설계도, BaseModel을 상속받아 "검증되는 데이터 구조"가 된다.
class Route(BaseModel):
    # next_agent: 4개 문자열 중 하나만 허용. 다른 값이 오면 pydantic이 에러를 낸다.
    next_agent: Literal["data_agent", "research_agent", "general_agent", "FINISH"] = Field(
        # description은 사람이 아니라 LLM이 읽는다. 이 문장이 곧 필드 작성 지침이 됨.
        description="다음에 호출할 Agent, 또는 작업 완료 시 FINISH"
    )
    # reason: 자유 문자열(str). 왜 그 에이전트를 골랐는지 근거를 같이 받는다.
    reason: str = Field(description="선택 이유 한 줄")


# llm: 실제 모델 객체. 클래스명(...) 형태는 "그 설계도로 객체를 하나 만든다"는 뜻.
llm = ChatBedrockConverse(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",  # 사용할 모델 ID
    region_name="us-east-1",                               # Bedrock 리전
    temperature=0,                                         # 0 = 무작위성 최소화(라우팅은 일관성이 중요)
)

# with_structured_output: "이제부터 자유 문장 말고 Route 모양으로만 답해" 라고 묶어
# 새 객체를 돌려준다. 원본 llm은 그대로 남고, router_llm은 Route 객체를 반환한다.
router_llm = llm.with_structured_output(Route)


# ROUTING_GUIDE: 프롬프트 문자열.
# 괄호 안에 문자열을 줄바꿈해 나열하면 파이썬이 자동으로 하나로 이어붙인다(연결 연산자 불필요).
# \n 은 줄바꿈 문자.
ROUTING_GUIDE = (
    "다음 질문을 처리할 Agent를 골라라.\n"
    "- data_agent: 임직원, 자산, 프로젝트 등 사내 시스템 데이터 조회\n"
    "- research_agent: 연차, 재택근무, 출장 등 사내 규정 문서 검색\n"
    "- general_agent: 인사말, 잡담, 범위 밖 질문 응대\n"
    "- FINISH: 이미 답변 가능\n\n질문: "
)

# questions: 리스트(list). 대괄호 [] 안에 값을 나열한 순서 있는 묶음.
questions = [
    "클라우드운영팀 임직원 명단 알려줘",
    "연차는 며칠까지 쓸 수 있어?",
    "안녕하세요, 오늘 기분 어때요?",
]

# for ... in ...: 리스트 원소를 하나씩 q에 담아 반복. 들여쓰기된 줄이 반복 대상(블록).
for q in questions:
    # invoke: 모델 1회 호출. 가이드 + 질문을 이어붙여(+) 보낸다.
    # 반환값 decision은 문자열이 아니라 Route 객체다.
    decision = router_llm.invoke(ROUTING_GUIDE + q)
    # f"...": f-string. 중괄호 {} 안의 파이썬 값이 문자열에 끼워 넣어진다.
    # decision.next_agent 처럼 점(.)으로 객체 안의 필드를 꺼내 쓴다.
    print(f"{q}\n  -> {decision.next_agent} ({decision.reason})\n")
