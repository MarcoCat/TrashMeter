// leaderboard.js
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("filterSelect").addEventListener("change", function() {
        var filterValue = this.value;
        var tbody = document.getElementById("leaderboardBody");
        var rows = Array.from(tbody.getElementsByTagName("tr"));

        rows.sort(function(a, b) {
            var aValue = parseInt(a.cells[2].textContent);
            var bValue = parseInt(b.cells[2].textContent);

            if (filterValue === "asc") {
                return aValue - bValue;
            } else if (filterValue === "desc") {
                return bValue - aValue;
            } else {
                return 0;
            }
        });

        // Clear the table body and re-append sorted rows
        while (tbody.firstChild) {
            tbody.removeChild(tbody.firstChild);
        }
        rows.forEach(function(row) {
            tbody.appendChild(row);
        });
    });
});
