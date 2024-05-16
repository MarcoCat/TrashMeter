function toggleVisibility() {
    var accountType = document.getElementById("account_type").value;
    var organizationNameDiv = document.getElementById("organization_name_field");
    var organizationLabel = document.getElementById("organization_label");
    var positionField = document.getElementById("position_field");

    if (["company", "school", "volunteer"].includes(accountType)) {
        organizationNameDiv.style.display = "block";
        organizationLabel.textContent = getLabelForType(accountType);
        filterOrganizations(accountType);
    } else {
        organizationNameDiv.style.display = "none";
    }

    if (accountType === "school") {
        positionField.style.display = "block";
    } else {
        positionField.style.display = "none";
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

function filterOrganizations(accountType) {
    var organizationSelect = document.getElementById("organization_id");
    var options = organizationSelect.options;
    
    for (var i = 0; i < options.length; i++) {
        var option = options[i];
        var orgType = option.getAttribute('data-type');

        if (accountType === orgType || option.value === "") {
            option.style.display = "block";
        } else {
            option.style.display = "none";
        }
    }
}
