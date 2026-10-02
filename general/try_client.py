import requests

BASE = "http://127.0.0.1:5200"
client_a = requests.Session()
client_b = requests.Session()

response = client_a.post(
    f"{BASE}/auth/login",
    json={"username": "student1", "password": "1234"},
    timeout=5,
)
print("A 로그인", response.status_code)
print("A 조회", client_a.get(f"{BASE}/posts/1", timeout=5).status_code)
print("B 조회", client_b.get(f"{BASE}/posts/1", timeout=5).status_code)
response = client_b.post(
    f"{BASE}/auth/login",
    json={"username": "student", "password": "Wrong123!"},
    timeout=5,
)
print("B 로그인 실패", response.status_code)
print("A 다시 조회", client_a.get(f"{BASE}/posts/1", timeout=5).status_code)
client_a.close()
client_b.close()