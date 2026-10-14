const API_BASE = `${window.location.protocol}//${window.location.hostname}:8001`;
const token = localStorage.getItem("access_token");
const technicianList = document.getElementById("technicianList");

async function loadTechnicians() {
    try {
        const response = await fetch(
            `${API_BASE}/technicians`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const technicians = await response.json();

        if (!response.ok) {
            throw new Error(
                technicians.detail || "Teknisyenler alınamadı."
            );
        }

        technicianList.innerHTML = "";

        technicians.forEach(function (technician) {
            const card = document.createElement("div");

            card.className = "dashboard-card";

            card.innerHTML = `
                <h3>${technician.username}</h3>
                <p>Kullanıcı ID: ${technician.id}</p>
                <p>Rol: ${technician.role}</p>
                <p>Durum: ${technician.availability}</p>
            `;

            technicianList.appendChild(card);
        });

    } catch (error) {
        technicianList.innerHTML = `
            <p>Teknisyenler yüklenemedi: ${error.message}</p>
        `;
    }
}

document.getElementById("logoutButton").addEventListener(
    "click",
    function () {
        localStorage.removeItem("access_token");
        window.location.href = "index.html";
    }
);

loadTechnicians();
