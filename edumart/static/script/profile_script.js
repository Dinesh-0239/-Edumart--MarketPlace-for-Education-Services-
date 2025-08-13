document.addEventListener("DOMContentLoaded", function () {
    // Hover effect for profile image
    const profileImage = document.querySelector(".img-fluid");
    if (profileImage) {
        profileImage.addEventListener("mouseenter", function () {
            this.style.transform = "scale(1.1)";
            this.style.transition = "0.3s ease-in-out";
        });
        profileImage.addEventListener("mouseleave", function () {
            this.style.transform = "scale(1)";
        });
    }

    // Service Card Hover Effect
    const serviceCards = document.querySelectorAll(".service-card");
    serviceCards.forEach(card => {
        card.addEventListener("mouseenter", function () {
            this.style.boxShadow = "0px 5px 20px rgba(0, 120, 232, 0.3)";
            this.style.transition = "0.3s";
        });
        card.addEventListener("mouseleave", function () {
            this.style.boxShadow = "none";
        });
    });

    // Smooth Scroll to Reviews Section
    const reviewLink = document.getElementById("reviews-link");
    if (reviewLink) {
        reviewLink.addEventListener("click", function (event) {
            event.preventDefault();
            document.getElementById("reviews-section").scrollIntoView({ behavior: "smooth" });
        });
    }

    // Logout Confirmation Alert
    const logoutButton = document.querySelector(".logout-button");
    if (logoutButton) {
        logoutButton.addEventListener("click", function (event) {
            event.preventDefault();
            if (confirm("Are you sure you want to log out?")) {
                window.location.href = this.getAttribute("data-url");
            }
        });
    }
});
