# components.py - 세 부품을 각각 실행해 입출력 타입 확인
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- 부품 1: PromptTemplate ---
# 입력: dict, 출력: 완성된 프롬프트 (PromptValue)
prompt = PromptTemplate.from_template("{text}를 {language}로 번역해줘.")
filled = prompt.invoke({"text": "Good morning", "language": "한국어"})
print("1) prompt 출력 타입:", type(filled).__name__)
print("   내용:", filled.to_string())

# --- 부품 2: Model ---
# 입력: PromptValue(또는 메시지, 문자열), 출력: AIMessage
llm = ChatBedrockConverse(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="us-east-1",
)
ai_message = llm.invoke(filled)
print("2) llm 출력 타입:", type(ai_message).__name__)
print("   내용:", ai_message.content)

# --- 부품 3: OutputParser ---
# 입력: AIMessage, 출력: str
parser = StrOutputParser()
text = parser.invoke(ai_message)
print("3) parser 출력 타입:", type(text).__name__)
print("   내용:", text)

# 3번 세션 components.py — 부품을 하나씩 손으로 실행했습니다
filled = prompt.invoke({"text": "Good morning", "language": "한국어"})
ai_message = llm.invoke(filled)
text = parser.invoke(ai_message)

# 같은 일을 LCEL로 조립하면
chain = prompt | llm | parser
text = chain.invoke({"text": "Good morning", "language": "한국어"})