document.addEventListener("DOMContentLoaded", function() {
    function sortTable(tbodyId, filterValue) {
        var tbody = document.getElementById(tbodyId);
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
    }

    document.getElementById("allUsersFilter").addEventListener("change", function() {
        sortTable("allUsersBody", this.value);
    });

    document.getElementById("companiesFilter").addEventListener("change", function() {
        sortTable("companiesBody", this.value);
    });

    document.getElementById("schoolsFilter").addEventListener("change", function() {
        sortTable("schoolsBody", this.value);
    });

    document.getElementById("volunteersFilter").addEventListener("change", function() {
        sortTable("volunteersBody", this.value);
    });
});
