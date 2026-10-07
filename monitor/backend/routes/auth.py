from flask import Blueprint, request, session
from werkzeug.security import check_password_hash
from auth_helpers import current_user, csrf_token, valid_csrf
from repositories import users as user_repository

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/api/auth/me")
def me():
    user = current_user()
    token = csrf_token()
    if user is None:
        return {"user": None, "csrf_token": token}
    return {"user": {"id": user["id"], "username": user["username"]}, "csrf_token": token}


@auth_bp.post("/api/auth/login")
def login():
    if "csrf_token" in session:
        client_csrf = request.headers.get("X-CSRF-Token")
        if client_csrf and not valid_csrf(client_csrf):
            return {"error": "요청 확인 값이 올바르지 않습니다. 새로고침 후 다시 시도해 주세요."}, 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "아이디와 비밀번호를 JSON으로 보내 주세요."}, 400
    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return {"error": "아이디와 비밀번호를 문자열로 보내 주세요."}, 400
    if not username.strip() or not password.strip():
        return {"error": "아이디와 비밀번호를 모두 입력해 주세요."}, 400

    user = user_repository.find_user(username.strip())
    if user is None or not check_password_hash(user["password_hash"], password):
        return {"error": "아이디 또는 비밀번호가 올바르지 않습니다."}, 401

    session.clear()
    session["user_id"] = user["id"]
    token = csrf_token()

    return {"user": {"id": user["id"], "username": user["username"]}, "csrf_token": token}


@auth_bp.post("/api/auth/logout")
def logout():
    session.clear()
    token = csrf_token()
    return {"user": None, "csrf_token": token}