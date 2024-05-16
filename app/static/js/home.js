document.addEventListener('DOMContentLoaded', (event) => {
    const learnHowModal = document.getElementById("learn-how-modal");
    const learnMoreModal = document.getElementById("learn-more-modal");
    const learnHowBtn = document.getElementById("learn-how-btn");
    const learnMoreBtn = document.getElementById("learn-more-btn");
    const closeButtons = document.getElementsByClassName("close-button");

    learnHowBtn.onclick = function(event) {
        event.preventDefault(); // Prevent the default anchor behavior
        learnHowModal.style.display = "flex"; // Set display to flex to center it
    }

    learnMoreBtn.onclick = function(event) {
        event.preventDefault(); // Prevent the default anchor behavior
        learnMoreModal.style.display = "flex"; // Set display to flex to center it
    }

    for (let i = 0; i < closeButtons.length; i++) {
        closeButtons[i].onclick = function() {
            this.parentElement.parentElement.style.display = "none";
        }
    }

    window.onclick = function(event) {
        if (event.target == learnHowModal) {
            learnHowModal.style.display = "none";
        } else if (event.target == learnMoreModal) {
            learnMoreModal.style.display = "none";
        }
    }
});
