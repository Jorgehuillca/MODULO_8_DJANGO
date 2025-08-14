document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:8000/api/company/1/"; // Ajusta al endpoint correcto

    fetch(API_URL)
        .then(response => response.json())
        .then(data => {
            document.getElementById("company-name").textContent = data.company_name;
            document.getElementById("company-logo").src = data.company_logo;
            document.getElementById("company-ruc").textContent = data.ruc || "No disponible";
            document.getElementById("company-created").textContent = new Date(data.created_at).toLocaleString();
            document.getElementById("company-updated").textContent = new Date(data.updated_at).toLocaleString();
        })
        .catch(error => {
            console.error("Error cargando datos de la empresa:", error);
        });
});
