document.addEventListener("DOMContentLoaded", function() {
    var urlParams = new URLSearchParams(window.location.search);
    var type = urlParams.get('type');
    var formTitle = document.getElementById('formTitle');
    var organizationTypeInput = document.getElementById('organization_type');

    switch (type) {
        case 'company':
            formTitle.textContent = 'Create Company Information';
            organizationTypeInput.value = 'Company';
            break;
        case 'school':
            formTitle.textContent = 'Create School Information';
            organizationTypeInput.value = 'School';
            break;
        case 'volunteer':
            formTitle.textContent = 'Create Volunteer Organization Information';
            organizationTypeInput.value = 'Volunteer Organization';
            break;
        default:
            formTitle.textContent = 'Create Organization Information';
            break;
    }

    organizationTypeInput.readOnly = true; // Make the input readonly to prevent changes
});

function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function() {
        var output = document.getElementById('organizationImagePreview');
        output.src = reader.result;
        output.style.display = 'block';
    };
    reader.readAsDataURL(event.target.files[0]);
}
function redirectToCreate() {
    var urlParams = new URLSearchParams(window.location.search);
    var type = urlParams.get('type');
    window.location.href = '/createinformation?type=' + encodeURIComponent(type);
}