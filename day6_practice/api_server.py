# api_server.py - 종합 시나리오 앱을 API로 노출
# 이 실습에만 필요한 패키지입니다: pip install fastapi uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from final_scenario import build_app, get_text

graph_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph_app
    graph_app = await build_app()
    yield

class UTF8JSONResponse(JSONResponse):
    """응답 Content-Type에 charset=utf-8을 명시합니다.

    FastAPI 기본값은 charset 없는 application/json이라,
    Windows PowerShell 5.1의 Invoke-RestMethod가 본문을 ISO-8859-1로
    해독해 한글이 깨집니다(예: "출장" -> "ì¶œìž¥").
    """

    media_type = "application/json; charset=utf-8"


api = FastAPI(lifespan=lifespan, default_response_class=UTF8JSONResponse)

class Query(BaseModel):
    question: str

@api.post("/chat")
async def chat(q: Query):
    result = await graph_app.ainvoke({"messages": [HumanMessage(q.question)]})
    return {"answer": get_text(result["messages"][-1])}

# uvicorn api_server:api --port 8000 # 실행
#
# 테스트 (PowerShell): -ContentType 에 charset=utf-8 을 꼭 붙이세요.
#   Invoke-RestMethod -Uri http://localhost:8000/chat -Method Post `
#     -ContentType "application/json; charset=utf-8" `
#     -Body '{"question": "출장 식비 한도 얼마야?"}'
#
# charset 을 빼면 PowerShell 5.1이 요청 본문을 ASCII로 인코딩해
# 서버에 "?? ?? ?? ????" 가 도착합니다(복구 불가).
#
# 응답은 PowerShell이 자동으로 객체로 보여 줍니다. 원문이 보고 싶으면 위 명령 뒤에 | ConvertTo-Json 을 붙입니다