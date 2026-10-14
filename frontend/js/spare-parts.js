const API = `${window.location.protocol}//${window.location.hostname}:8001`;
const token = localStorage.getItem("access_token");
const partList = document.getElementById("partList");
const partForm = document.getElementById("partForm");
const partMessage = document.getElementById("partMessage");

async function loadParts() {
    const response = await fetch(`${API}/spare-parts`, {
        headers: { Authorization: `Bearer ${token}` }
    });
    const parts = await response.json();
    partList.innerHTML = "";
    if (!response.ok) {
        partList.textContent = parts.detail || "Parçalar yüklenemedi.";
        return;
    }
    parts.forEach((part) => {
        const card = document.createElement("div");
        card.className = "dashboard-card";
        const critical = part.stock_quantity <= part.critical_level;
        card.innerHTML = `<h3>${part.name}</h3>
            <p>Kod: ${part.code}</p>
            <p>Stok: ${part.stock_quantity}</p>
            <p>Kritik seviye: ${part.critical_level}</p>
            <p>${critical ? "Kritik stok" : "Stok yeterli"}</p>`;
        partList.appendChild(card);
    });
}

partForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await fetch(`${API}/spare-parts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
            code: document.getElementById("partCode").value,
            name: document.getElementById("partName").value,
            stock_quantity: Number(document.getElementById("stockQuantity").value),
            critical_level: Number(document.getElementById("criticalLevel").value)
        })
    });
    const data = await response.json();
    partMessage.textContent = response.ok ? "Parça eklendi." : (data.detail || "Parça eklenemedi.");
    if (response.ok) { partForm.reset(); await loadParts(); }
});

document.getElementById("logoutButton").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.href = "index.html";
});

loadParts();
