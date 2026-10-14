const API_BASE = `${window.location.protocol}//${window.location.hostname}:8001`;
const token = localStorage.getItem("access_token");

const workOrderForm = document.getElementById("workOrderForm");
const workOrderList = document.getElementById("workOrderList");
const workOrderMessage = document.getElementById("workOrderMessage");
const statusFilter = document.getElementById("statusFilter");
const priorityFilter = document.getElementById(
    "priorityFilter"
);

let technicians = [];
let allWorkOrders = [];


async function loadTechnicians() {
    const response = await fetch(
        `${API_BASE}/technicians`,
        {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    technicians = await response.json();
}


async function loadWorkOrders() {
    const response = await fetch(
        `${API_BASE}/work-orders`,
        {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    allWorkOrders = await response.json();

    renderWorkOrders(allWorkOrders);
}


function renderWorkOrders(workOrders) {
    workOrderList.innerHTML = "";

    workOrders.forEach(function (item) {
        const card = document.createElement("div");

        card.className = "dashboard-card";

        const technicianOptions = technicians.map(function (technician) {
            return `
                <option value="${technician.id}">
                    ${technician.username}
                </option>
            `;
        }).join("");

        const technicianName =
            item.technician_username || "Atama yapılmadı";

        const assignmentControls =
            item.status === "Tamamlandı"
                ? ""
                : `
                    <select id="technician-${item.id}">
                        <option value="">
                            Teknisyen seç
                        </option>

                        ${technicianOptions}
                    </select>

                    <button onclick="assignTechnician(${item.id})">
                        Teknisyen Ata
                    </button>
                `;

        card.innerHTML = `
            <h3>${item.title}</h3>

            <p>Ekipman ID: ${item.equipment_id}</p>
            <p>Açıklama: ${item.description}</p>
            <p>Durum: ${item.status}</p>
            <p>Öncelik: ${item.priority}</p>
            <p>Teknisyen: ${technicianName}</p>

            ${assignmentControls}
            <button type="button" onclick="showHistory(${item.id})">
                Durum Geçmişi
            </button>
            <div id="history-${item.id}" class="history-list"></div>
        `;

        workOrderList.appendChild(card);
    });
}


async function showHistory(workOrderId) {
    const target = document.getElementById(`history-${workOrderId}`);
    const response = await fetch(
        `${API_BASE}/work-orders/${workOrderId}/history`,
        { headers: { Authorization: `Bearer ${token}` } }
    );
    const data = await response.json();
    if (!response.ok) {
        target.textContent = data.detail || "Geçmiş yüklenemedi.";
        return;
    }
    target.innerHTML = data.length
        ? data.map((entry) => `<p>${entry.old_status || "Başlangıç"} → ${entry.new_status}</p>`).join("")
        : "<p>Henüz durum geçmişi yok.</p>";
}


function applyFilters() {
    const selectedStatus = statusFilter.value;
    const selectedPriority = priorityFilter.value;

    const filteredWorkOrders = allWorkOrders.filter(function (item) {
        const statusMatches =
            selectedStatus === "Tümü" ||
            item.status === selectedStatus;

        const priorityMatches =
            selectedPriority === "Tümü" ||
            item.priority === selectedPriority;

        return statusMatches && priorityMatches;
    });

    renderWorkOrders(filteredWorkOrders);
}

statusFilter.addEventListener(
    "change",
    applyFilters
);

priorityFilter.addEventListener(
    "change",
    applyFilters
);


async function assignTechnician(workOrderId) {
    const selectedTechnician = document.getElementById(
        `technician-${workOrderId}`
    ).value;

    if (!selectedTechnician) {
        alert("Önce bir teknisyen seç.");
        return;
    }

    const response = await fetch(
        `${API_BASE}/work-orders/${workOrderId}/assign`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                technician_id: Number(selectedTechnician)
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {
        alert(data.detail || "Teknisyen atanamadı.");
        return;
    }

    alert("Teknisyen başarıyla atandı.");

    loadWorkOrders();
}


workOrderForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const response = await fetch(
        `${API_BASE}/work-orders`,
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
        workOrderMessage.textContent =
            data.detail || "İş emri oluşturulamadı.";
        return;
    }

    workOrderMessage.textContent =
        "İş emri oluşturuldu.";

    workOrderForm.reset();

    loadWorkOrders();
});


document.getElementById("logoutButton").addEventListener(
    "click",
    function () {
        localStorage.removeItem("access_token");
        window.location.href = "index.html";
    }
);


async function initializePage() {
    await loadTechnicians();
    await loadWorkOrders();
}

initializePage();
