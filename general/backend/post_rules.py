def validate_post(title, body):
    if not title or not body:
        return "제목과 내용을 모두 입력해 주세요."
    return None


def read_post(data):
    if not isinstance(data, dict):
        return None, "제목과 내용을 JSON으로 보내 주세요."
    title = data.get("title")
    body = data.get("body")
    if not isinstance(title, str) or not isinstance(body, str):
        return None, "제목과 내용을 문자열로 보내 주세요."
    title = title.strip()
    body = body.strip()
    error = validate_post(title, body)
    if error:
        return None, error
    return {"title": title, "body": body}, None
