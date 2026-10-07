ALLOWED_STATUSES = {"확인 전", "확인 중", "완료"}


def read_note(data):
    if not isinstance(data, dict):
        return None, "제목과 내용을 JSON으로 보내 주세요."
    title = data.get("title")
    body = data.get("body")
    if not isinstance(title, str) or not isinstance(body, str):
        return None, "제목과 내용을 문자열로 보내 주세요."
    title = title.strip()
    body = body.strip()
    if not title or not body:
        return None, "제목과 내용을 모두 입력해 주세요."

    status = data.get("status", "확인 전")
    if not isinstance(status, str):
        return None, "처리 상태를 문자열로 보내 주세요."
    status = status.strip()
    if not status:
        status = "확인 전"
    elif status not in ALLOWED_STATUSES:
        return None, f"처리 상태는 {', '.join(sorted(ALLOWED_STATUSES))} 중 하나여야 합니다."

    return {"title": title, "body": body, "status": status}, None
