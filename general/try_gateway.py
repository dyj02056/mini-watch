import requests

BASE = "http://127.0.0.1:5200"
client = requests.Session()

response = client.post(
    f"{BASE}/auth/login",
    json={"username": "student1", "password": "1234"},
    timeout=5,
)
print("감시를 거친 로그인", response.status_code, response.json())
response = client.get(f"{BASE}/posts/1", timeout=5)
print("감시를 거친 조회", response.status_code, response.json())
response = client.post(f"{BASE}/auth/logout", timeout=5)
print("감시를 거친 로그아웃", response.status_code)
print("남은 쿠키 수", len(client.cookies))
response = client.get(f"{BASE}/posts/1", timeout=5)
print("로그아웃 후 조회", response.status_code)
client.close()