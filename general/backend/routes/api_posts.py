from flask import Blueprint, request
from auth_helpers import api_access_error
from post_rules import read_post
from repositories import posts as post_repository

posts_bp = Blueprint("api_posts", __name__)


@posts_bp.before_request
def require_login():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        return api_access_error()
    return None


@posts_bp.get("/api/posts")
def list_posts():
    return {"posts": post_repository.list_posts()}


@posts_bp.get("/api/posts/<int:post_id>")
def get_post(post_id):
    post = post_repository.find_post(post_id)
    if post is None:
        return {"error": "게시글을 찾을 수 없습니다."}, 404
    return {"post": post}


@posts_bp.post("/api/posts")
def create_post():
    post, error = read_post(request.get_json(silent=True))
    if error:
        return {"error": error}, 400
    created = post_repository.create_post(post["title"], post["body"])
    return {"post": created}, 201


@posts_bp.put("/api/posts/<int:post_id>")
def update_post(post_id):
    post, error = read_post(request.get_json(silent=True))
    if error:
        return {"error": error}, 400
    updated = post_repository.update_post(post_id, post["title"], post["body"])
    if updated is None:
        return {"error": "게시글을 찾을 수 없습니다."}, 404
    return {"post": updated}


@posts_bp.delete("/api/posts/<int:post_id>")
def delete_post(post_id):
    deleted = post_repository.delete_post(post_id)
    if deleted is None:
        return {"error": "게시글을 찾을 수 없습니다."}, 404
    return {"message": "게시글을 삭제했습니다."}
