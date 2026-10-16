import os

from notice_state import prepare_notice
from request_history_state import prepare_request_history


def main():
    prepare_notice()
    prepare_request_history()
    if os.environ.get("SEED_CLASSROOM_ACCOUNTS", "false").lower() == "true":
        from seed_classroom import main as prepare_classroom
        prepare_classroom()
    os.execvp("waitress-serve", [
        "waitress-serve", "--host=0.0.0.0", f"--port={os.environ.get('PORT', '5000')}", "app:app",
    ])


if __name__ == "__main__":
    main()
