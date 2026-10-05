const form = document.querySelector("#login-form");
const usernameInput = document.querySelector("#username");
const passwordInput = document.querySelector("#password");
const result = document.querySelector("#result");

form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const data = {
        username: usernameInput.value,
        password: passwordInput.value,
    };
    result.textContent = "확인 중입니다.";

    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data),
        });
        const answer = await response.json();
        if (response.ok) {
            result.textContent = answer.message + ": " + answer.user.username;
        } else {
            result.textContent = answer.error;
        }
    } catch (error) {
        result.textContent = "서버와 통신하지 못했습니다. 서버 실행 상태를 확인해 주세요.";
    }
});
