const API_BASE = `${window.location.protocol}//${window.location.hostname}:8001`;
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "index.html";
}

async function loadDashboard() {
    try {
        const response = await fetch(
            `${API_BASE}/admin/dashboard`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error("Dashboard verileri alınamadı.");
        }

        const data = await response.json();

        document.getElementById("totalEquipment").textContent =
            data.total_equipment;

        document.getElementById("totalWorkOrders").textContent =
            data.total_work_orders;

        document.getElementById("waitingWorkOrders").textContent =
            data.by_status["Bekliyor"] || 0;

        document.getElementById("availableTechnicians").textContent =
            data.available_technicians;

    } catch (error) {
        console.error(error);
    }
}

document.getElementById("logoutButton").addEventListener("click", function () {
    localStorage.removeItem("access_token");
    window.location.href = "index.html";
});

loadDashboard();
