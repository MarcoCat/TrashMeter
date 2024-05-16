document.addEventListener("DOMContentLoaded", function() {
    toggleVisibility();
});

function toggleVisibility() {
    var accountType = document.getElementById("account_type").value;
    var organizationNameDiv = document.getElementById("organization_name_field");
    var organizationLabel = document.getElementById("organization_label");

    if (["company", "school", "volunteer"].includes(accountType)) {
        organizationNameDiv.style.display = "block";
        organizationLabel.textContent = getLabelForType(accountType);
    } else {
        organizationNameDiv.style.display = "none";
    }
}

function getLabelForType(type) {
    switch (type) {
        case 'company':
            return 'Name of your Company:';
        case 'school':
            return 'Name of your School:';
        case 'volunteer':
            return 'Name of your Volunteer Organization:';
        default:
            return 'Name:';
    }
}

function redirectToSearch() {
    var searchTerm = document.getElementById("organization_name").value;
    window.location.href = 'search.html?query=' + encodeURIComponent(searchTerm); // Pass search term as a query parameter
}

function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function() {
        var output = document.getElementById('profileImagePreview');
        output.src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);
}
