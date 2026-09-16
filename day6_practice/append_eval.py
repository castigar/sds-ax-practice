# append_eval.py - 오늘 검증 문항을 누적 평가셋에 추가
import json
from pathlib import Path

EVAL_PATH = Path("eval_set.json")

# 2일차부터 고정된 스키마입니다: question, expected_source, type
# expected_source는 항상 문자열입니다(없으면 null). 리스트를 넣으면 7일차 평가 스크립트가 멈춥니다
# 여럿을 적어야 하면 쉼표로 이어 한 문자열로 만듭니다
today = [
    {
        "question": "물류플랫폼팀 인원을 조회하고, 출장 규정상 예상 식비 총액도 알려줘",
        "expected_source": "data_agent, research_agent",
        "type": "multi_agent",
    },
    {
        "question": "재택근무 신청은 언제까지 승인받아야 해?",
        "expected_source": "docs/remote_work_policy.md",
        "type": "fact",
    },
]

rows = json.loads(EVAL_PATH.read_text(encoding="utf-8")) if EVAL_PATH.exists() else []
rows.extend(today)
EVAL_PATH.write_text(
    json.dumps(rows, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"평가셋 누적 문항 수: {len(rows)}")