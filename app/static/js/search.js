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

    fetch(`/api/search_organizations?type=${type}&query=` + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            var resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '';

            if (data.length === 0) {
                resultsDiv.textContent = 'No results found.';
                document.getElementById('addButton').style.display = 'block';
            } else {
                var ul = document.createElement('ul');
                data.forEach(org => {
                    var li = document.createElement('li');
                    li.innerHTML = `<strong>${org.name}</strong><br>Type: ${org.type}<br>Address: ${org.address}<br>Total Trash: ${org.total_trash}`;
                    ul.appendChild(li);
                });
                resultsDiv.appendChild(ul);
                document.getElementById('addButton').style.display = 'none';
            }
        });
}

function redirectToCreate() {
    var urlParams = new URLSearchParams(window.location.search);
    var type = urlParams.get('type');
    window.location.href = '/createinformation?type=' + encodeURIComponent(type);
}
