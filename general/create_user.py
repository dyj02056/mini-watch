from werkzeug.security import generate_password_hash
from db import connect_db

password_hash = generate_password_hash("1234")

with connect_db() as conn:
    result = conn.execute(
        """INSERT INTO users (username, password_hash)
           VALUES (%s, %s)
           ON CONFLICT (username) DO NOTHING""",
        ("student1", password_hash),
    )
    if result.rowcount == 1:
        print("student1 계정을 만들었습니다.")
    else:
        print("student1 계정이 이미 있습니다. 기존 계정을 유지합니다.")