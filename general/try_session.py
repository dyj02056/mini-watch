import requests

BASE = "http://127.0.0.1:5100"
client = requests.Session()

response = client.get(f"{BASE}/posts/1", timeout=5)
print("로그인 전", response.status_code)

response = client.post(
    f"{BASE}/auth/login",
    json={"username": "student1", "password": "1234"},
    timeout=5,
)
print("로그인", response.status_code)
print("쿠키 이름", list(client.cookies.keys()))

response = client.get(f"{BASE}/posts/1", timeout=5)
print("같은 Session", response.status_code, response.json())
response = requests.get(f"{BASE}/posts/1", timeout=5)
print("별도 요청", response.status_code)
response = client.get(f"{BASE}/posts/999", timeout=5)
print("없는 게시글", response.status_code)

response = client.post(f"{BASE}/auth/logout", timeout=5)
print("로그아웃", response.status_code)
print("남은 쿠키 수", len(client.cookies))
response = client.get(f"{BASE}/posts/1", timeout=5)
print("로그아웃 후", response.status_code)
client.close()