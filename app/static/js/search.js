document.addEventListener("DOMContentLoaded", function() {
    toggleVisibility();

    // Check if the organization name is provided in the URL and set it
    const urlParams = new URLSearchParams(window.location.search);
    const orgName = urlParams.get('org_name');
    if (orgName) {
        document.getElementById('organization_name').value = orgName;
    }

    // Prefill other form fields from URL parameters
    document.getElementById('username').value = urlParams.get('username') || '';
    document.getElementById('email').value = urlParams.get('email') || '';
    document.getElementById('first_name').value = urlParams.get('first_name') || '';
    document.getElementById('last_name').value = urlParams.get('last_name') || '';
    document.getElementById('password').value = urlParams.get('password') || '';
    document.getElementById('account_type').value = urlParams.get('account_type') || 'individual';
    toggleVisibility();  // Ensure the organization field is displayed if needed
});

function toggleVisibility() {
    var accountType = document.getElementById("account_type").value;
    var organizationNameDiv = document.getElementById("organization_name_field");

    if (["company", "school", "volunteer"].includes(accountType)) {
        organizationNameDiv.style.display = "block";
    } else {
        organizationNameDiv.style.display = "none";
    }
}

function redirectToSearch() {
    var accountType = document.getElementById("account_type").value;
    var url = '/search?type=' + encodeURIComponent(accountType);

    // Append current form data to the URL
    var formData = new URLSearchParams({
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        password: document.getElementById('password').value,
        account_type: document.getElementById('account_type').value
    }).toString();

    window.location.href = url + '&' + formData;
}

function redirectToCreate() {
    var urlParams = new URLSearchParams(window.location.search);
    var type = urlParams.get('type');
    window.location.href = '/createinformation?type=' + encodeURIComponent(type);
}

function loadSelectedOrganization(id, name) {
    document.getElementById('organization_name').value = name;
    document.getElementById('organization_id').value = id;
}

function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function() {
        var output = document.getElementById('profileImagePreview');
        output.src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);
}

