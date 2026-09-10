# hello_graph.py - 첫 그래프 전체 코드
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from graph_utils import save_graph_png


class State(TypedDict):
    user_input: str
    response: str


def respond(state: State) -> dict:
    user = state["user_input"]
    return {"response": f"입력하신 내용은 '{user}' 입니다."}


builder = StateGraph(State)
builder.add_node("respond", respond)
builder.add_edge(START, "respond")
builder.add_edge("respond", END)

graph = builder.compile()    # 그래프를 실행 가능한 객체로 변환

result = graph.invoke({"user_input": "안녕하세요"})
print(result)

# 구조 시각화
save_graph_png(graph)