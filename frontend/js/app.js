const API_BASE = `${window.location.protocol}//${window.location.hostname}:8001`;

function decodeToken(token) {
    const payload = token.split(".")[1];

    const base64 = payload
        .replace(/-/g, "+")
        .replace(/_/g, "/");

    return JSON.parse(atob(base64));
}

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            message.textContent = data.detail || "Giriş başarısız.";
            return;
        }

        localStorage.setItem("access_token", data.access_token);

        const tokenData = decodeToken(data.access_token);
        const role = tokenData.role;

        if (role === "Yönetici") {
            window.location.href = "admin.html";
        } else if (role === "Teknisyen") {
            window.location.href = "technician.html";
        } else if (role === "Personel") {
            window.location.href = "personel.html";
        } else {
            message.textContent = "Tanımsız kullanıcı rolü.";
        }

    } catch (error) {
        message.textContent = "Sunucuya bağlanılamadı.";
    }
});
