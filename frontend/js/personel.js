const token = localStorage.getItem("access_token");

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8001`;
const problemForm = document.getElementById("problemForm");
const problemMessage = document.getElementById("problemMessage");


problemForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const response = await fetch(
        `${API_BASE}/problem-reports`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                equipment_id: Number(
                    document.getElementById("equipmentId").value
                ),
                title: document.getElementById("title").value,
                description: document.getElementById("description").value,
                priority: document.getElementById("priority").value
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {
        problemMessage.textContent =
            data.detail || "Sorun bildirimi oluşturulamadı.";
        return;
    }

    problemMessage.style.color = "green";
    problemMessage.textContent =
        "Sorun bildirimi başarıyla oluşturuldu.";

    const photo = document.getElementById("photo").files[0];
    if (photo) {
        const formData = new FormData();
        formData.append("photo", photo);
        const photoResponse = await fetch(
            `${API_BASE}/problem-reports/${data.id}/photo`,
            { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData }
        );
        if (!photoResponse.ok) {
            problemMessage.textContent = "Bildirim oluşturuldu ancak fotoğraf yüklenemedi.";
        }
    }
    problemForm.reset();
});


document.getElementById("logoutButton").addEventListener(
    "click",
    function () {
        localStorage.removeItem("access_token");
        window.location.href = "index.html";
    }
);
