# react_agent.py (1/3) - 도구 준비
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()
llm = ChatBedrockConverse(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="us-east-1",
)


def get_text(message):
    """ChatBedrockConverse는 content를 블록 리스트로 주기도 하므로 텍스트만 모아 반환합니다."""
    content = message.content
    if isinstance(content, list):
        return "".join(block.get("text", "") for block in content if isinstance(block, dict))
    return content


@tool
def search_employee(name: str) -> str:
    """임직원 이름으로 소속 팀과 이메일을 조회합니다. 임직원 정보 질문에 사용하세요."""
    # 교육용 더미 데이터입니다. 실제 사내 데이터와 무관합니다.
    employees = {
        "김하늘": {"team": "클라우드운영팀", "email": "haneul.kim@samsungsds.example.com"},
        "박도윤": {"team": "물류플랫폼팀", "email": "doyun.park@samsungsds.example.com"},
    }
    if name in employees:
        e = employees[name]
        return f"{name} / {e['team']} / {e['email']}"
    return f"'{name}' 님을 찾을 수 없습니다. 조회 가능한 임직원: {list(employees.keys())}"


@tool
def calculate(expression: str) -> str:
    """수식 문자열을 계산해 정확한 결과를 반환합니다. 예: '3480000 * 1.1', '48 * 1.12'"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"계산 실패: {e}. 수식 형식을 확인하세요."


@tool
def classify_request(text: str) -> str:
    """사내 문의 문장을 받아 담당 부서를 IT지원, 인사, 총무 중 하나로 분류합니다. 문의 접수와 부서 배정 질문에 사용하세요."""
    # 도구 안에서 다시 LLM을 호출합니다. 도구 안의 AI입니다.
    result = llm.invoke(
        "다음 사내 문의의 담당 부서를 IT지원, 인사, 총무 중 하나로만 답하세요. "
        f"다른 말은 붙이지 마세요.\n\n문의: {text}"
    )
    return get_text(result).strip()


tools = [search_employee, calculate, classify_request]

print(search_employee.invoke({"name": "김하늘"}))
print(calculate.invoke({"expression": "48 * 1.12"}))
print(classify_request.invoke({"text": "노트북 화면이 계속 깜빡거려요"}))