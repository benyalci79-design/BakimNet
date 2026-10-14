const token = localStorage.getItem("access_token");

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8001`;
const equipmentList = document.getElementById("equipmentList");
const equipmentForm = document.getElementById("equipmentForm");
const equipmentMessage = document.getElementById("equipmentMessage");


async function loadEquipment() {
    const response = await fetch(
        `${API_BASE}/equipment`,
        {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    const equipment = await response.json();

    equipmentList.innerHTML = "";

    equipment.forEach(function (item) {
        const card = document.createElement("div");

        card.className = "dashboard-card";

        card.innerHTML = `
            <h3>${item.name}</h3>
            <p>Kod: ${item.code}</p>
            <p>Konum: ${item.location}</p>
            <p>ID: ${item.id}</p>

            <button onclick="updateEquipment(${item.id})">
                Konumu Güncelle
            </button>

            <button onclick="deleteEquipment(${item.id})">
                Sil
            </button>
        `;

        equipmentList.appendChild(card);
    });
}


equipmentForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const response = await fetch(
        `${API_BASE}/equipment`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                code: document.getElementById("code").value,
                name: document.getElementById("name").value,
                location: document.getElementById("location").value
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {
        equipmentMessage.textContent =
            data.detail || "Ekipman eklenemedi.";
        return;
    }

    equipmentMessage.textContent = "Ekipman başarıyla eklendi.";
    equipmentForm.reset();

    loadEquipment();
});


async function updateEquipment(id) {
    const newLocation = prompt("Yeni konumu yaz:");

    if (!newLocation) {
        return;
    }

    const response = await fetch(
        `${API_BASE}/equipment/${id}`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                location: newLocation
            })
        }
    );

    if (response.ok) {
        alert("Ekipman güncellendi.");
        loadEquipment();
    } else {
        alert("Ekipman güncellenemedi.");
    }
}


async function deleteEquipment(id) {
    const confirmed = confirm(
        "Bu ekipmanı silmek istediğine emin misin?"
    );

    if (!confirmed) {
        return;
    }

    const response = await fetch(
        `${API_BASE}/equipment/${id}`,
        {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    if (response.ok) {
        alert("Ekipman silindi.");
        loadEquipment();
    } else {
        alert("Ekipman silinemedi.");
    }
}


document.getElementById("logoutButton").addEventListener("click", function () {
    localStorage.removeItem("access_token");
    window.location.href = "index.html";
});


loadEquipment();
