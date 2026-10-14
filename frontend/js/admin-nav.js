const adminNav = document.getElementById("adminNav");

const currentPage =
    window.location.pathname.split("/").pop() || "admin.html";

adminNav.innerHTML = `
    <h3>Menü</h3>

    <a href="admin.html"
       class="nav-link ${currentPage === "admin.html" ? "active" : ""}">
        Dashboard
    </a>
    <a href="problems.html"
   class="nav-link ${currentPage === "problems.html" ? "active" : ""}">
    Sorun Bildirimleri
</a>

    <a href="equipment.html"
       class="nav-link ${currentPage === "equipment.html" ? "active" : ""}">
        Ekipmanlar
    </a>
    <a href="technicians.html"
   class="nav-link ${currentPage === "technicians.html" ? "active" : ""}">
    Teknisyenler
</a>

    <a href="work-orders.html"
       class="nav-link ${currentPage === "work-orders.html" ? "active" : ""}">
        İş Emirleri
    </a>

   <a href="spare-parts.html"
      class="nav-link ${currentPage === "spare-parts.html" ? "active" : ""}">
       Stok ve Parçalar
   </a>
`;
