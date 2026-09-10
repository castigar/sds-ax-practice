# cycle.py - 조건을 만족할 때까지 반복하는 그래프
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


class QualityState(TypedDict):
    question: str
    answer: str
    attempts: int
    quality_score: float


def generate(state: QualityState) -> dict:
    """답변을 생성하고 시도 횟수를 1 올립니다."""
    response = llm.invoke(
        # f"다음 질문에 짧게 한 문장으로 답하세요: {state['question']}"
        f"다음 질문에 200자 이상으로 자세하게 답하세요: {state['question']}"
    )
    return {
        "answer": get_text(response),
        "attempts": state.get("attempts", 0) + 1,
    }


def check_quality(state: QualityState) -> dict:
    """품질 평가. 실습용으로 단순하게 길이 기반 점수를 씁니다 (200자면 만점)."""
    score = min(len(state["answer"]) / 200, 1.0)
    return {"quality_score": score}


def route_quality(state: QualityState) -> Literal["generate", "__end__"]:
    """품질이 좋거나 시도 한도에 도달하면 종료하고 아니면 재시도합니다."""
    if state["quality_score"] >= 0.8:
        return END
    if state["attempts"] >= 3:       # 안전장치: 무한 루프 방지
        return END
    return "generate"                # 이전 노드로 돌아감 = 반복


builder = StateGraph(QualityState)
builder.add_node("generate", generate)
builder.add_node("check_quality", check_quality)
builder.add_edge(START, "generate")
builder.add_edge("generate", "check_quality")
builder.add_conditional_edges("check_quality", route_quality)
graph = builder.compile()

if __name__ == "__main__":   # 5번째 세션에서 이 파일을 import해 쓰므로 실행 부분은 가드 아래에 둡니다
    result = graph.invoke({
        "question": "LangGraph의 장점을 설명해 주세요",
        "answer": "",
        "attempts": 0,
        "quality_score": 0.0,
    })
    # 구조 시각화
    save_graph_png(graph)
    print(f"시도 횟수: {result['attempts']}")
    print(f"품질 점수: {result['quality_score']:.2f}")
    print(f"답변 길이: {len(result['answer'])}자")
    print(f"답변 미리보기: {result['answer'][:80]}...")
