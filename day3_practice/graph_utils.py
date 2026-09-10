# graph_utils.py - day3 실습에서 반복되는 헬퍼 모음
import inspect
from pathlib import Path


def get_text(message):
    """ChatBedrockConverse는 content를 블록 리스트로 주기도 하므로 텍스트만 모아 반환합니다."""
    content = message.content
    if isinstance(content, list):
        return "".join(block.get("text", "") for block in content if isinstance(block, dict))
    return content


def save_graph_png(graph, output_file_path=None):
    """그래프 구조를 PNG로 저장합니다.

    output_file_path를 생략하면 호출한 스크립트와 같은 이름/같은 폴더에 저장합니다.
    (conditional.py에서 부르면 -> 그 옆에 conditional.png)

    PNG 저장이 안 되는 환경(그래프 렌더링 서버 접근 불가 등)도 있으므로
    실패하면 mermaid 텍스트를 출력하고 False를 반환합니다.
    """
    if output_file_path is None:
        output_file_path = _default_png_path()
    try:
        graph.get_graph().draw_mermaid_png(output_file_path=str(output_file_path))
        print(f"{Path(output_file_path).name} 저장 완료")
        return True
    except Exception as e:
        print("PNG 저장은 건너뜁니다:", e)
        print(graph.get_graph().draw_mermaid())   # 텍스트 출력으로 대체
        return False


def _default_png_path():
    """호출한 스크립트 경로의 확장자를 .png로 바꿔 돌려줍니다."""
    here = Path(__file__).resolve()
    frame = inspect.currentframe()
    while frame is not None:     # 이 파일 바깥의 첫 호출자를 찾습니다
        caller_file = frame.f_globals.get("__file__")
        if caller_file and Path(caller_file).resolve() != here:
            return Path(caller_file).resolve().with_suffix(".png")
        frame = frame.f_back
    return Path("graph.png").resolve()   # REPL/노트북처럼 __file__이 없는 경우
