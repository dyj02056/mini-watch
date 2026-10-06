from flask import Flask
from routes.posts import posts_bp
from routes.auth import auth_bp
from request_logging import record_request

app = Flask(__name__)
app.json.ensure_ascii = False

app.register_blueprint(posts_bp)
app.register_blueprint(auth_bp)
app.after_request(record_request)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5100)
