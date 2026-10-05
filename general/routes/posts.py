from flask import Blueprint, request, render_template, redirect
from db import connect_db
from post_rules import validate_post

posts_bp = Blueprint("posts", __name__)


def find_post(post_id):
    with connect_db() as conn:
        return conn.execute(
            "SELECT id, title, body FROM posts WHERE id = %s",
            (post_id,),
        ).fetchone()


@posts_bp.get("/")
def index():
    with connect_db() as conn:
        posts = conn.execute("SELECT id, title, body FROM posts ORDER BY id").fetchall()
    return render_template("index.html", posts=posts)


@posts_bp.get("/board/<int:post_id>")
def post_detail(post_id):
    post = find_post(post_id)
    if post is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return render_template("detail.html", post=post)


@posts_bp.route("/board/new", methods=["GET", "POST"])
def new_post():
    if request.method == "GET":
        return render_template("new.html", title="", body="", error=None)

    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    error = validate_post(title, body)
    if error:
        return render_template(
            "new.html", title=title, body=body,
            error=error,
        ), 400

    with connect_db() as conn:
        post = conn.execute(
            "INSERT INTO posts (title, body) VALUES (%s, %s) RETURNING id",
            (title, body),
        ).fetchone()
    return redirect(f"/board/{post['id']}", code=303)


@posts_bp.route("/board/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    post = find_post(post_id)
    if post is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    if request.method == "GET":
        return render_template(
            "edit.html", post_id=post_id,
            title=post["title"], body=post["body"], error=None,
        )

    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    error = validate_post(title, body)
    if error:
        return render_template(
            "edit.html", post_id=post_id, title=title, body=body,
            error=error,
        ), 400

    with connect_db() as conn:
        updated = conn.execute(
            "UPDATE posts SET title = %s, body = %s WHERE id = %s RETURNING id",
            (title, body, post_id),
        ).fetchone()
    if updated is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return redirect(f"/board/{post_id}", code=303)


@posts_bp.route("/board/<int:post_id>/delete", methods=["GET", "POST"])
def delete_post(post_id):
    if request.method == "GET":
        post = find_post(post_id)
        if post is None:
            return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
        return render_template("delete.html", post=post)

    with connect_db() as conn:
        deleted = conn.execute(
            "DELETE FROM posts WHERE id = %s RETURNING id", (post_id,),
        ).fetchone()
    if deleted is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return redirect("/", code=303)


@posts_bp.get("/posts/<int:post_id>")
def get_post(post_id):
    post = find_post(post_id)
    if post is None:
        return {"error": "게시글을 찾을 수 없습니다."}, 404
    return post
