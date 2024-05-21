document.addEventListener("DOMContentLoaded", function() {
    var urlParams = new URLSearchParams(window.location.search);
    var type = urlParams.get('type');
    var searchTitle = document.getElementById('searchTitle');

    switch (type) {
        case 'company':
            searchTitle.textContent = 'Search Company';
            break;
        case 'school':
            searchTitle.textContent = 'Search School';
            break;
        case 'volunteer':
            searchTitle.textContent = 'Search Volunteer Organization';
            break;
        default:
            searchTitle.textContent = 'Search';
            break;
    }
});

function performSearch() {
    var query = document.getElementById('searchQuery').value;
    var urlParams = new URLSearchParams(window.location.search);
    var type = urlParams.get('type');

    // Assuming there's an endpoint to search organizations by type
    fetch(`/api/search_organizations?type=${type}&query=` + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            var resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '';

            if (data.length === 0) {
                resultsDiv.textContent = 'No results found.';
                document.getElementById('addButton').style.display = 'block';
            } else {
                data.forEach(org => {
                    var orgDiv = document.createElement('div');
                    orgDiv.textContent = org.name;
                    orgDiv.onclick = function() {
                        window.opener.loadSelectedOrganization(org.id, org.name);
                        window.close();
                    };
                    resultsDiv.appendChild(orgDiv);
                });
                document.getElementById('addButton').style.display = 'none';
            }
        });
}

function redirectToCreate() {
    var urlParams = new URLSearchParams(window.location.search);
    var type = urlParams.get('type');
    window.location.href = '/createinformation?type=' + encodeURIComponent(type);
}

