# conditional.py - 조건부 엣지로 분기하기
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_aws import ChatBedrockConverse
from graph_utils import get_text, save_graph_png

load_dotenv()
llm = ChatBedrockConverse(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="us-east-1",
)


class ClassifyState(TypedDict):
    user_input: str
    intent: str
    response: str # reducer로 이어서 쌓을 게 아니므로 여기선 list로 선언하지 않음.


def classify(state: ClassifyState) -> dict:
    """입력에 '?'가 있으면 question, 없으면 exclaim으로 분류합니다."""
    intent = "question" if "?" in state["user_input"] else "exclaim"
    return {"intent": intent}


def answer_question(state: ClassifyState) -> dict:
    """질문에 LLM으로 답합니다."""
    response = llm.invoke(f"다음 질문에 한 줄로 답하세요: {state['user_input']}")
    return {"response": get_text(response)}


def react_exclaim(state: ClassifyState) -> dict:
    """감탄에는 LLM 없이 정해진 반응을 합니다."""
    return {"response": f"'{state['user_input']}' 라니 멋진 일이네요."}


def route_by_intent(state: ClassifyState) -> Literal["answer_question", "react_exclaim"]:
    """라우팅 함수: State를 보고 다음 노드의 이름을 반환합니다."""
    if state["intent"] == "question":
        return "answer_question"
    return "react_exclaim"


builder = StateGraph(ClassifyState)
builder.add_node("classify", classify)
builder.add_node("answer_question", answer_question)
builder.add_node("react_exclaim", react_exclaim)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_by_intent)   # 분기 등록
builder.add_edge("answer_question", END)
builder.add_edge("react_exclaim", END)
graph = builder.compile()

for text in ["오늘 사내 식당 메뉴 뭐야?", "와 배포가 한 번에 성공했다", "LangGraph가 뭐야?"]:
    result = graph.invoke({"user_input": text, "intent": "", "response": ""})
    print(f"입력: {text}")
    print(f"분류: {result['intent']} / 응답: {result['response']}\n")

# 구조 시각화
save_graph_png(graph)