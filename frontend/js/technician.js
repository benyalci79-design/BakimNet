const API_BASE = `${window.location.protocol}//${window.location.hostname}:8001`;
const token = localStorage.getItem("access_token");

const workOrderList = document.getElementById(
    "myWorkOrderList"
);


async function loadMyWorkOrders() {
    const response = await fetch(
        `${API_BASE}/my-work-orders`,
        {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    const workOrders = await response.json();

    workOrderList.innerHTML = "";

    workOrders.forEach(function (item) {
        const card = document.createElement("div");

        card.className = "dashboard-card";

        let actionButton = "";

        if (item.status === "Bekliyor") {
            actionButton = `
                <button onclick="startWorkOrder(${item.id})">
                    İşi Başlat
                </button>
            `;
        }

        if (item.status === "Devam Ediyor") {
            actionButton = `
                <textarea
                    id="work-done-${item.id}"
                    placeholder="Yapılan işlemi yaz"
                ></textarea>

                <input type="number" min="1" id="part-id-${item.id}" placeholder="Parça ID (opsiyonel)">
                <input type="number" min="1" id="part-quantity-${item.id}" placeholder="Parça miktarı">
                <button type="button" onclick="addPartUsage(${item.id})">
                    Parça Kullan
                </button>

                <button onclick="completeWorkOrder(${item.id})">
                    İşi Tamamla
                </button>
            `;
        }

        card.innerHTML = `
            <h3>${item.title}</h3>
            <p>Ekipman ID: ${item.equipment_id}</p>
            <p>Açıklama: ${item.description}</p>
            <p>Durum: ${item.status}</p>
            <p>Öncelik: ${item.priority}</p>

            ${actionButton}
        `;

        workOrderList.appendChild(card);
    });
}


async function addPartUsage(workOrderId) {
    const partId = Number(document.getElementById(`part-id-${workOrderId}`).value);
    const quantity = Number(document.getElementById(`part-quantity-${workOrderId}`).value);
    if (!partId || !quantity) {
        alert("Parça ID ve miktarını gir.");
        return;
    }
    const response = await fetch(`${API_BASE}/work-orders/${workOrderId}/parts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ spare_part_id: partId, quantity })
    });
    const data = await response.json();
    alert(response.ok ? "Parça kullanımı kaydedildi." : (data.detail || "Parça kullanılamadı."));
}


async function startWorkOrder(workOrderId) {
    const response = await fetch(
        `${API_BASE}/work-orders/${workOrderId}/start`,
        {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    if (response.ok) {
        alert("İş başlatıldı.");
        loadMyWorkOrders();
    } else {
        alert("İş başlatılamadı.");
    }
}


async function completeWorkOrder(workOrderId) {
    const workDone = document.getElementById(
        `work-done-${workOrderId}`
    ).value;

    if (!workDone) {
        alert("Yapılan işlemi yaz.");
        return;
    }

    const response = await fetch(
        `${API_BASE}/work-orders/${workOrderId}/complete`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                work_done: workDone
            })
        }
    );

    if (response.ok) {
        alert("İş tamamlandı.");
        loadMyWorkOrders();
    } else {
        alert("İş tamamlanamadı.");
    }
}


document.getElementById("logoutButton").addEventListener(
    "click",
    function () {
        localStorage.removeItem("access_token");
        window.location.href = "index.html";
    }
);


loadMyWorkOrders();
