# routing_test.py - 라우팅 테스트셋 정확도 측정
import asyncio
import json
from langchain_core.messages import HumanMessage
from final_scenario import build_app

PASS_MIN = 5   # 합격 기준: 6문항 중 5문항 이상 정답

def load_test_set(path="routing_test.json"):
    # 테스트셋 파일은 이 코드와 같은 폴더에 두세요
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    # type이 multi이거나 기대 Agent가 2개 이상이면 복합 질문으로 봅니다
    return [
        (
            row["question"],
            set(row["expected"]),
            row.get("type") == "multi" or len(row["expected"]) >= 2,
        )
        for row in rows
    ]

async def routed_agents(app, question: str) -> set:
    """질문 하나를 실행하고 호출된 서브 Agent 이름 집합을 반환한다."""
    called = set()
    async for event in app.astream(
        {"messages": [HumanMessage(content=question)]},
        stream_mode="updates",
        config={"recursion_limit": 30},
    ):
        for node in event:
            if node != "supervisor":
                called.add(node)
    return called

async def main():
    app = await build_app()
    test_set = load_test_set()
    correct = 0
    multi_total = 0
    multi_correct = 0
    for question, expected, is_multi in test_set:
        actual = await routed_agents(app, question)
        # 정답 기준: 기대한 Agent가 전부 호출되고 그 밖의 Agent는 불리지 않아야 합니다.
        # 호출 순서는 상황에 따라 달라지므로 따지지 않습니다
        ok = actual == expected
        correct += ok
        if is_multi:
            multi_total += 1
            multi_correct += ok
        mark = "정답" if ok else "오답"
        tag = " (복합)" if is_multi else ""
        print(f"[{mark}]{tag} {question}")
        print(f"       기대: {sorted(expected)} / 실제: {sorted(actual)}")

    total = len(test_set)
    accuracy_ok = correct >= PASS_MIN
    multi_ok = multi_total > 0 and multi_correct == multi_total
    print(f"\n라우팅 정확도: {correct}/{total} ({correct / total * 100:.0f}%)"
          f" -> {'통과' if accuracy_ok else '미통과'}")
    print(f"복합 질문: {multi_correct}/{multi_total}"
          f" -> {'통과' if multi_ok else '미통과'} (필수)")
    print(f"최종 판정: {'통과' if accuracy_ok and multi_ok else '미통과'}")

if __name__ == "__main__":
    asyncio.run(main())