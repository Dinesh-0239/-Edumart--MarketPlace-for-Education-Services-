function toggleOtherCategory() {
    var categorySelect = document.getElementById("category");
    var otherCategoryDiv = document.getElementById("other-category-div");
    var otherCategoryInput = document.getElementById("other_category");

    if (categorySelect.value === "Other") {
        otherCategoryDiv.style.display = "block";
        otherCategoryInput.required = true;
    } else {
        otherCategoryDiv.style.display = "none";
        otherCategoryInput.required = false;
    }
}

// Ensure the correct state on page load
document.addEventListener("DOMContentLoaded", toggleOtherCategory);
