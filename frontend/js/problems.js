const API_BASE = `${window.location.protocol}//${window.location.hostname}:8001`;
const token = localStorage.getItem("access_token");
const problemList = document.getElementById("problemList");


async function loadProblems() {
    const response = await fetch(
        `${API_BASE}/problem-reports`,
        {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    const problems = await response.json();

    problemList.innerHTML = "";

    problems.forEach(function (item) {
        const card = document.createElement("div");

        card.className = "dashboard-card";

        const convertButton =
            item.status === "İş Emrine Dönüştürüldü"
                ? ""
                : `
                    <button onclick="convertProblem(${item.id})">
                        İş Emrine Dönüştür
                    </button>
                `;

        card.innerHTML = `
            <h3>${item.title}</h3>

            <p>Ekipman ID: ${item.equipment_id}</p>
            <p>Açıklama: ${item.description}</p>
            <p>Öncelik: ${item.priority}</p>
            <p>Durum: ${item.status}</p>
            <p>Bildiren: ${item.reported_by_username}</p>

            ${convertButton}
        `;

        problemList.appendChild(card);
    });
}


async function convertProblem(problemId) {
    const confirmed = confirm(
        "Bu bildirimi iş emrine dönüştürmek istiyor musun?"
    );

    if (!confirmed) {
        return;
    }

    const response = await fetch(
        `${API_BASE}/problem-reports/${problemId}/convert`,
        {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    const data = await response.json();

    if (!response.ok) {
        alert(data.detail || "Dönüştürme işlemi başarısız.");
        return;
    }

    alert("Sorun bildirimi iş emrine dönüştürüldü.");

    loadProblems();
}


document.getElementById("logoutButton").addEventListener(
    "click",
    function () {
        localStorage.removeItem("access_token");
        window.location.href = "index.html";
    }
);


loadProblems();
