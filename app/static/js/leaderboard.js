document.addEventListener("DOMContentLoaded", function() {
    function updateLeaderboardTitle(title) {
        document.getElementById("leaderboardTitle").textContent = title;
    }

    // Update title on tab click
    document.querySelectorAll('.nav-link').forEach(function(tab) {
        tab.addEventListener('click', function() {
            updateLeaderboardTitle(this.getAttribute('data-title'));
        });
    });

    // Update title on dropdown item click
    document.querySelectorAll('.dropdown-item').forEach(function(item) {
        item.addEventListener('click', function() {
            updateLeaderboardTitle(this.getAttribute('data-title'));
        });
    });

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

        // Reset pagination after sorting
        currentPage[tbodyId] = 1;
        updatePagination(tbodyId);
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

    // Handle mobile filter click events
    document.querySelectorAll('.dropdown-item').forEach(function(item) {
        item.addEventListener('click', function(event) {
            event.preventDefault();
            var targetTab = this.getAttribute('data-filter');
            var tabTrigger = new bootstrap.Tab(document.querySelector(targetTab + '-tab'));
            tabTrigger.show();
            updatePagination(targetTab.slice(1) + 'Body');
        });
    });

    // Pagination logic
    const rowsPerPage = 10;
    const currentPage = {
        allUsersBody: 1,
        companiesBody: 1,
        schoolsBody: 1,
        volunteersBody: 1
    };

    function updatePagination(tbodyId) {
        var tbody = document.getElementById(tbodyId);
        var rows = Array.from(tbody.getElementsByTagName("tr"));
        var totalRows = rows.length;
        var totalPages = Math.ceil(totalRows / rowsPerPage);
        var start = (currentPage[tbodyId] - 1) * rowsPerPage;
        var end = start + rowsPerPage;

        rows.forEach(function(row, index) {
            row.style.display = (index >= start && index < end) ? "" : "none";
        });

        var paginationControls = document.querySelector(`.pagination-controls[data-tbody-id="${tbodyId}"]`);
        if (paginationControls) {
            if (totalRows <= rowsPerPage) {
                paginationControls.style.display = "none";
            } else {
                paginationControls.style.display = "flex";
            }

            var prevButton = document.getElementById(`prevPage${tbodyId.charAt(0).toUpperCase() + tbodyId.slice(1)}`);
            var nextButton = document.getElementById(`nextPage${tbodyId.charAt(0).toUpperCase() + tbodyId.slice(1)}`);

            if (prevButton && nextButton) {
                prevButton.disabled = currentPage[tbodyId] === 1;
                nextButton.disabled = currentPage[tbodyId] === totalPages;
            }
        }
    }

    document.getElementById("prevPageAllUsers").addEventListener("click", function() {
        currentPage.allUsersBody = Math.max(1, currentPage.allUsersBody - 1);
        updatePagination("allUsersBody");
    });

    document.getElementById("nextPageAllUsers").addEventListener("click", function() {
        var tbody = document.getElementById("allUsersBody");
        var totalRows = tbody.getElementsByTagName("tr").length;
        var totalPages = Math.ceil(totalRows / rowsPerPage);
        currentPage.allUsersBody = Math.min(totalPages, currentPage.allUsersBody + 1);
        updatePagination("allUsersBody");
    });

    document.getElementById("prevPageCompanies").addEventListener("click", function() {
        currentPage.companiesBody = Math.max(1, currentPage.companiesBody - 1);
        updatePagination("companiesBody");
    });

    document.getElementById("nextPageCompanies").addEventListener("click", function() {
        var tbody = document.getElementById("companiesBody");
        var totalRows = tbody.getElementsByTagName("tr").length;
        var totalPages = Math.ceil(totalRows / rowsPerPage);
        currentPage.companiesBody = Math.min(totalPages, currentPage.companiesBody + 1);
        updatePagination("companiesBody");
    });

    document.getElementById("prevPageSchools").addEventListener("click", function() {
        currentPage.schoolsBody = Math.max(1, currentPage.schoolsBody - 1);
        updatePagination("schoolsBody");
    });

    document.getElementById("nextPageSchools").addEventListener("click", function() {
        var tbody = document.getElementById("schoolsBody");
        var totalRows = tbody.getElementsByTagName("tr").length;
        var totalPages = Math.ceil(totalRows / rowsPerPage);
        currentPage.schoolsBody = Math.min(totalPages, currentPage.schoolsBody + 1);
        updatePagination("schoolsBody");
    });

    document.getElementById("prevPageVolunteers").addEventListener("click", function() {
        currentPage.volunteersBody = Math.max(1, currentPage.volunteersBody - 1);
        updatePagination("volunteersBody");
    });

    document.getElementById("nextPageVolunteers").addEventListener("click", function() {
        var tbody = document.getElementById("volunteersBody");
        var totalRows = tbody.getElementsByTagName("tr").length;
        var totalPages = Math.ceil(totalRows / rowsPerPage);
        currentPage.volunteersBody = Math.min(totalPages, currentPage.volunteersBody + 1);
        updatePagination("volunteersBody");
    });

    // Initialize pagination on page load
    function initializePagination() {
        updatePagination("allUsersBody");
        updatePagination("companiesBody");
        updatePagination("schoolsBody");
        updatePagination("volunteersBody");
    }

    initializePagination();
});
